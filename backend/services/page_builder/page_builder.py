from datetime import datetime, timezone
import logging
import time
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Generator
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
ADVANCED_LM_MODEL_NAME = 'haiku'
ADVANCED_LM_STYLE = 'sonnet'

ssh_manager = SSHManager(is_dev_mode=IS_DEV_MODE, logger=logger)
advanced_language_model = initialize_llm(ADVANCED_LM_MODEL_NAME, ADVANCED_LM_STYLE)

@dataclass
class PipelineResult:
    """Class to hold both results and progress messages"""
    result: Any = None
    progress_message: Optional[Dict] = None

async def page_builder_pipeline(prompt: str, db) -> Generator[str, None, None]:
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
        section_markups = []
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
                if result.progress_message.get("type") == "section_complete":
                    section_markups.append(result.progress_message["content"])
            if result.result:
                images = result.result

        # Assemble final output
        final_output = assemble_page(styles, section_markups)
        await save_images_to_db(images, db)

        # Final outputs
        yield format_sse({
            "type": "component_complete",
            "content": final_output,
            "image_placeholders": images,
        })
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
    """
    Analyze the complexity of the user's prompt.

    Args:
        prompt (str): The user's input describing the desired page.

    Returns:
        str: Complexity level ('simple' or 'complex').
    """
    try:
        complexity_analysis = await execute_llm_call(
            Predict(Sigs.ComplexityAnalyzer),
            description=prompt,
        )
        complexity_level = complexity_analysis.complexity_level.lower()
        return complexity_level
    except Exception as e:
        raise Exception(f"Error analyzing complexity: {str(e)}") from e

async def design_components(prompt: str, complexity_level: str) -> Generator[PipelineResult, None, None]:
    """Design components or sections based on the prompt and complexity level."""
    parts = []
    styles = []
    name_key = ''
    
    try:
        if complexity_level == "complex":
            yield PipelineResult(
                progress_message={"type": "progress", "message": "🚧 Breaking down complex request..."}
            )
            with context(lm=advanced_language_model):
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
            with context(lm=advanced_language_model):
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
) -> Generator[PipelineResult, None, None]:
    """
    Process each section concurrently.

    Args:
        parts (List[Dict[str, Any]]): List of component or section specifications.
        styles (List[str]): List of CSS styles.
        pipeline_logger (logging.Logger): Logger for the pipeline.

    Yields:
        PipelineResult: Progress messages and results.
    """
    images = []
    
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
                yield PipelineResult(
                    progress_message={"type": "section_complete", "content": result['markup']}
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

        # Create component
        current_component = create_component_scaffold(
            styles=f"<style>{' '.join(styles)}</style>",
            markup=[markup],
        )
        return {
            'markup': markup,  # Return the raw markup
            'images': images
        }
    except Exception as e:
        pipeline_logger.error(f"Section '{section['name']}' failed: {str(e)}", exc_info=True)
        raise e

def append_style(styles_list: List[str], section_name: str, css_rules: str, transitions: str) -> None:
    """
    Append CSS styles for a section to the styles list.

    Args:
        styles_list (List[str]): List of CSS styles.
        section_name (str): Name of the section.
        css_rules (str): CSS rules for the section.
        transitions (str): CSS transitions for the section.
    """
    styles_list.append(f"""
    /* {section_name} */
    {css_rules}
    {transitions}
    """)

async def generate_section_style(
    style_instructions: str,
    global_css: str,
) -> Dict[str, str]:
    """
    Generate context-aware styles for a section.

    Args:
        style_instructions (str): Instructions for the section styles.
        global_css (str): Existing global CSS styles.

    Returns:
        Dict[str, str]: CSS rules and transitions for the section.
    """
    try:
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
    """
    Generate image details for a section.

    Args:
        image_instructions (List[Dict[str, Any]]): Instructions for image generation.

    Returns:
        List[Dict[str, Any]]: List of generated image details.
    """
    if not image_instructions:
        return []

    try:
        with context(lm=advanced_language_model):
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
            # Run the blocking operation in an executor
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
    """
    Build a complete section including structure with positioned image placeholders
    and context-aware accessibility features.

    Args:
        layout_structure (str): The layout structure of the section.
        section_style (Dict[str, str]): CSS rules and transitions for the section.
        image_details (List[Dict[str, Any]], optional): Details of images to include.

    Returns:
        str: Cleaned HTML markup of the section.
    """
    try:
        with context(lm=advanced_language_model):
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

def assemble_page(styles: List[str], markups: List[str]) -> str:
    """
    Assemble the final HTML page.

    Args:
        styles (List[str]): List of CSS styles.
        markups (List[str]): List of HTML markups.

    Returns:
        str: Final HTML content of the page.
    """
    # Combine all styles into a single style block
    combined_styles = f"<style>\n{' '.join(styles)}\n</style>"
    
    # Create the final scaffold with all section markups
    final_output = create_component_scaffold(
        styles=combined_styles,
        markup=markups,
    )
    return final_output

async def save_images_to_db(images: List[Dict[str, Any]], db) -> None:
    """
    Save generated images to the database.

    Args:
        images (List[Dict[str, Any]]): List of image details.
        db: Database connection object.
    """
    if images:
        current_time = datetime.now(timezone.utc)
        image_documents = [
            {**image, "created_at": current_time}
            for image in images
        ]

        collection = db.get_collection('generated_images')
        await collection.insert_many(image_documents)
