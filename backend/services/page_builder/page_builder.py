from datetime import datetime, timezone
import logging
import time
import asyncio
import uuid
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from dspy import ChainOfThought, context, Predict
from backend.core.ssh_manager import SSHManager
from backend.services.image_gen.image_gen_manager import ImageGenerator
from backend.services.page_builder.signatures import PageBuilderSignatures as Sigs
from backend.services.page_builder.builder_utils import (
    format_sse,
    clean_markup,
    create_component_scaffold,
)
from backend.utils.llm_utils import execute_llm_call, initialize_llm

logger = logging.getLogger('app.component_builder')

# Configuration settings
IS_DEV_MODE = True
LLM = 'haiku'
STRONG_LLM = 'sonnet'

ssh_manager = SSHManager(is_dev_mode=IS_DEV_MODE, logger=logger)
lm, strong_lm = initialize_llm(LLM, STRONG_LLM)

@dataclass
class PipelineResult:
    """Class to hold both results and progress messages"""
    result: Any = None
    progress_message: Optional[Dict] = None

async def page_builder_pipeline(prompt: str, db) -> AsyncGenerator[str, None]:
    """Build a web page based on the given prompt."""
    pipeline_id = uuid.uuid4()
    pipeline_logger = logging.getLogger(f'app.component_builder.pipeline_{pipeline_id}')
    start_time = time.time()
    pipeline_logger.info(f"Pipeline {pipeline_id} started for prompt: {prompt[:100]}...")

    try:
        # Analyze complexity
        yield format_sse({"type": "progress", "message": "🎯 Analyzing requirements..."})
        complexity_level = await analyze_complexity(prompt)

        parts = []
        styles = []
        images = []

        # Design components
        async for result in design_components(prompt, complexity_level):
            if result.progress_message:
                yield format_sse(result.progress_message)
            if result.result:
                components_result = result.result
                if isinstance(components_result, tuple) and len(components_result) == 2:
                    parts, styles = components_result
                else:
                    raise ValueError("Invalid component design result format")
        if not parts or not styles:
            raise ValueError("Component design did not produce valid results")

        # Process sections
        async for result in process_sections(parts, styles, pipeline_logger):
            if result.progress_message:
                yield format_sse(result.progress_message)
            if result.result:
                images = result.result

        await save_images_to_db(images, db)

        # Final outputs
        yield format_sse({
            "type": "pipeline_complete",
            "build_time": time.time() - start_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        pipeline_logger.info(f"Pipeline {pipeline_id} completed successfully.")
    except Exception as e:
        pipeline_logger.error(f"Pipeline {pipeline_id} failed: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})

async def analyze_complexity(prompt: str) -> str:
    try:
        with context(lm=lm):   
            complexity_analysis = await execute_llm_call(
                Predict(Sigs.ComplexityAnalyzer),
                description=prompt,
            )
        complexity_level = complexity_analysis.complexity_level.lower()
        return complexity_level
    except Exception as e:
        raise Exception(f"Error analyzing complexity: {str(e)}") from e

async def design_components(prompt: str, complexity_level: str) -> AsyncGenerator[PipelineResult, None]:
    parts = []
    styles = []
    name_key = ''
    
    try:
        if complexity_level == "complex":
            yield PipelineResult(
                progress_message={"type": "progress", "message": "🚧 Breaking down complex request..."}
            )
            with context(lm=strong_lm):
                web_app_architect = await execute_llm_call(
                    ChainOfThought(Sigs.WebAppArchitect),
                    description=prompt,
                )
            parts.extend(web_app_architect.sections)
            styles.append(web_app_architect.global_css)
            name_key = 'section_name'
            yield PipelineResult(
                progress_message={"type": "progress", "message": 'Design complete'}
            )
        else:
            yield PipelineResult(
                progress_message={"type": "progress", "message": "🏗️ Designing component..."}
            )
            with context(lm=strong_lm):
                component_architect = await execute_llm_call(
                    ChainOfThought(Sigs.WebComponentArchitect),
                    description=prompt,
                )
            parts.append(component_architect.component_spec)
            styles.append(f"/*Global CSS*/\n{component_architect.global_css}\n/*End Global CSS*/")
            name_key = 'component_name'

        # Update parts with a name key for consistency
        for part in parts:
            part['name'] = part.get(name_key, 'Unnamed Part')

        yield PipelineResult(result=(parts, styles))
    except Exception as e:
        raise Exception(f"Error designing components: {str(e)}") from e

async def process_sections(
    parts: List[Dict[str, Any]],
    styles: List[str],
    pipeline_logger: logging.Logger,
) -> AsyncGenerator[PipelineResult, None]:
    images = []
    cumulative_markups = []
    
    for index, section in enumerate(parts, 1):
        try:
            yield PipelineResult(
                progress_message={
                    "type": "progress",
                    "message": f"🏗️ Section {index}/{len(parts)}: {section['name']}",
                    "progress": (index / len(parts)) * 100,
                }
            )

            # Process single section
            result = await process_section(section, styles, pipeline_logger)
            
            if isinstance(result, dict):
                images.extend(result.get('images', []))
                cumulative_markups.append(result['markup'])
                current_scaffold = create_component_scaffold(
                    styles=f"<style>{' '.join(styles)}</style>",
                    markup=cumulative_markups,
                )

                yield PipelineResult(
                    progress_message={"type": "section_complete", "content": current_scaffold}
                )
            
        except Exception as e:
            pipeline_logger.error(f"Error processing section: {str(e)}", exc_info=True)
            yield PipelineResult(
                progress_message={"type": "warning", "message": f"Section issue: {str(e)}"}
            )

    yield PipelineResult(result=images)

async def process_section(
    section: Dict[str, Any],
    styles: List[str],
    pipeline_logger: logging.Logger,
) -> Dict[str, Any]:
    """Process an individual section."""
    try:
        # Generate images and styles concurrently
        image_task = generate_section_image_details(section.get('image_requirements', []))
        style_task = generate_section_style(
            section.get('css_style_and_animation_instructions', ''),
            styles[-1] if styles else '',
        )

        section_images, section_style = await asyncio.gather(image_task, style_task)

        images = section_images if section_images else []

        append_style(styles, section['name'], section_style['css_rules'], section_style['transitions'])

        # Build section structure
        markup = await build_page_section(
            layout_structure=section['layout_structure'],
            section_style=section_style,
            image_details=section_images,
        )
        return {
            'markup': markup,
            'images': images
        }
    except Exception as e:
        pipeline_logger.error(f"Section '{section['name']}' failed: {str(e)}", exc_info=True)
        raise e

def append_style(styles_list: List[str], section_name: str, css_rules: str, transitions: str) -> None:
    styles_list.append(f"""
    /* {section_name} */
    {css_rules}
    {transitions}
    """)

async def generate_section_style(
    style_instructions: str,
    global_css: str,
) -> Dict[str, str]:
    try:
        with context(lm=lm): 
            style_response = await execute_llm_call(
                Predict(Sigs.SectionStyle),
                style_instructions=style_instructions,
                global_css=global_css,
            )
        return {
            'css_rules': style_response.css_rules,
            'transitions': style_response.transitions,
        }
    except Exception as e:
        raise Exception(f"Error generating section styles: {str(e)}") from e

async def generate_section_image_details(image_instructions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not image_instructions:
        return []

    try:
        with context(lm=strong_lm):
            image_response = await execute_llm_call(
                ChainOfThought(Sigs.SectionImageDetails),
                image_instructions=image_instructions,
            )

        detailed_images = []
        image_generator = ImageGenerator(ssh_manager)
        loop = asyncio.get_running_loop()

        image_tasks = []
        for image in image_response.image_details:
            image_name = image['image_name']

            image_tasks.append(loop.run_in_executor(
                None,
                image_generator.generate_image,
                image["prompt"],
                image_name,
            ))

        image_lists = await asyncio.gather(*image_tasks)

        for image_list, image in zip(image_lists, image_response.image_details):
            if image_list:
                image_list[0].update({
                    'alt': image['alt'],
                    'prompt': image['prompt'],
                    'image_name': image['image_name'],
                })
                detailed_images.append(image_list[0])

        return detailed_images
    except Exception as e:
        raise Exception(f"Error generating image details: {str(e)}") from e

async def build_page_section(
    layout_structure: str,
    section_style: Dict[str, str],
    image_details: Optional[List[Dict[str, Any]]] = None,
) -> str:
    try:
        with context(lm=strong_lm):
            structure_response = await execute_llm_call(
                ChainOfThought(Sigs.ComponentStructure),
                layout_structure=layout_structure,
                section_css_rules=section_style['css_rules'],
                image_details=image_details,
            )

        # Combine the markup with accessibility features
        cleaned_markup = clean_markup(structure_response.markup)
        return cleaned_markup
    except Exception as e:
        logger.error(f"Error in build_page_section: {str(e)}", exc_info=True)
        raise Exception(f"Error building section structure: {str(e)}") from e

async def save_images_to_db(images: List[Dict[str, Any]], db) -> None:
    if images:
        current_time = datetime.now(timezone.utc)
        image_documents = [
            {**image, "created_at": current_time}
            for image in images
        ]

        collection = db.get_collection('generated_images')
        await collection.insert_many(image_documents)
