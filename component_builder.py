import re
from datetime import datetime, timezone
import logging
import time
from typing import List, Dict
import json
from dspy import ChainOfThought, context, Predict
from llm_utils import execute_llm_call, initialize_llm
from SSHManager import SSHManager
from ImageGenManager import ImageGenerator
from page_builder.PageBuilderSignatures import PageBuilderSignatures as Sigs

COMPONENT_SCAFFOLD = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component_title}</title>  
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script> 
    
    <!-- Additional Resource Loading -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Component Styles -->
    {component_styles} 
</head>
<body>
    <!-- Component Container -->
    <div id="component-root">
        {component_markup}
    </div>  
    <!-- Component Scripts -->
    {component_scripts}
</body>
</html>
'''

logger = logging.getLogger('app.component_builder')
ssh_manager = SSHManager(is_dev_mode=True, logger=logger)

strong_lm = initialize_llm('haiku', 'sonnet')

async def component_builder_pipeline(prompt, db):
    start = time.time()
    logger.info(f"Starting pipeline: {prompt[:100]}...") 
    parts = []
    styles = []
    markup = []
    images = []
    section_logic = {}
    try:
        yield format_sse({"type": "progress", "message": "🎯 Analyzing requirements..."})
        complexity_analysis = await execute_llm_call(
            Predict(Sigs.ComplexityAnalyzer),
            description=prompt
        )

        if complexity_analysis.complexity_level.lower() == "complex":
            yield format_sse({"type": "progress", "message": "🚧 Breaking down complex request..."})
            with context(lm=strong_lm):
                web_app_architect = await execute_llm_call(
                    ChainOfThought(Sigs.WebAppArchitect), description=prompt
                )
            parts.extend(web_app_architect.sections)
            styles.append(web_app_architect.global_css)
            name = 'section_name'
            yield format_sse({
                "type": "progress", 
                "message": 'Design complete'
            })
        else:
            yield format_sse({"type": "progress", "message": "🏗️ Designing component..."})
            with context(lm=strong_lm):
                component_architect = await execute_llm_call(
                    ChainOfThought(Sigs.WebComponentArchitect), description=prompt
                )
            parts.append(component_architect.component_spec)
            styles.append(f"/*Global CSS*/\n{component_architect.global_css}\n/*End Global CSS*/")
            name = 'component_name'

    except Exception as e:
        logger.error(f"Definition failed: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})
        return 

    # Section loop
    for i, section in enumerate(parts, 1):
        try:
            if len(parts) > 1:
                yield format_sse({
                    "type": "progress",
                    "message": f"🏗️ Section {i}/{len(parts)}: {section[name]}"
                })

            # Generate images
            if 'image_requirements' in section:
                section_images = await generate_section_image_details(
                    image_instructions=section['image_requirements']
                )
                images.extend(section_images)

            # Generate section-specific styles
            section_style = await generate_section_style(
                style_instructions=section['css_style_and_animation_instructions'],
                global_css=styles[-1]
            )

            styles.append(f"""
                /* {section[name]} */
                {section_style['css_rules']}
                {section_style['transitions']}
            """)

            # Generate section logic
            logic = await build_section_logic(
                javascript_instructions=section['javascript_instructions']
            )
            section_logic[section[name]] = logic
            # Build section structure
            markup.append(await build_component_section(
                layout_structure=section['layout_structure'],
                javascript=logic.get('javascript', ''),
                section_style=section_style,
                image_details=section_images,
            )) 
            # Provide intermediate feedback
            current_component = create_component_scaffold(
                styles=f"<style>{' '.join(styles)}</style>",
                markup=markup,
            )
            yield format_sse({
                "type": "section_complete",
                "content": current_component
            }) 
        except Exception as e:
            logger.error(f"Section {section[name]} failed: {str(e)}")
            yield format_sse({
                "type": "warning",
                "message": f"Section issue: {str(e)}"
            }) 
    # Generate final component
    final = create_component_scaffold(
        styles=f"<style>{' '.join(styles)}</style>",
        markup=markup,
        section_logic=section_logic
    )
    
    # Add timestamp to each image and insert into MongoDB if images exist
    if images:
        current_time = datetime.now(timezone.utc)
        image_documents = [
            {**image, "created_at": current_time} 
            for image in images
        ]
        
        await db.get_collection('generated_images').insert_many(image_documents)

    # Final outputs
    yield format_sse({
        "type": "component_complete",
        "content": final,
        "image_placeholders": images,
    }) 
    yield format_sse({
        "type": "pipeline_complete",
        "build_time": time.time() - start,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }) 

def format_sse(data):
    return f"data: {json.dumps(data)}\n\n"

def clean_markup(markup):
    try:
        if not isinstance(markup, str):
            raise ValueError("Input must be a string")
        if not markup.strip():
            raise ValueError("Input string is empty")
        clean_text = re.sub(r'```html|css|javascript|```', '', markup)
        return clean_text.strip()
        
    except re.error as e:
        raise ValueError(f"Error cleaning HTML: {str(e)}")

def create_component_scaffold(styles: str, markup: List[str], section_logic: Dict[str, str] = None) -> str:
    cleaned_styles = clean_markup(styles)
    cleaned_markup = [clean_markup(section) for section in markup]
    
    js_code = ""
    if section_logic:
        js_code = flatten_section_logic(section_logic)
    
    return COMPONENT_SCAFFOLD.format(
        component_title="",
        component_styles=cleaned_styles,
        component_markup="\n".join(cleaned_markup),
        script_imports="",
        component_scripts=f"{js_code}"
    )

def flatten_section_logic(section_logic: Dict[str, Dict[str, str]]) -> str:
    """Flatten multiple sections of JavaScript into a single coherent script."""
    cleaned_js_sections = []
    cleaned_state_sections = []
    cleaned_event_delegations = []

    for section_name, logic in section_logic.items():
        # Process JavaScript logic
        if 'javascript' in logic:
            js_content = re.sub(r'```javascript\s*|```\s*', '', logic['javascript']).strip()
            if js_content:
                cleaned_js_sections.append(f"""
                // {section_name} Section Logic
                {js_content}
                """)
        
        # Only process state management if it exists
        if 'state_management' in logic:
            state_content = re.sub(r'```javascript\s*|```\s*', '', logic['state_management']).strip()
            if state_content:
                cleaned_state_sections.append(f"""
                // {section_name} State Management
                {state_content}
                """)
                
        # Only process event delegation if it exists
        if 'event_delegation' in logic:
            event_delegation_content = re.sub(r'```javascript\s*|```\s*', '', logic['event_delegation']).strip()
            if event_delegation_content:
                cleaned_event_delegations.append(f"""
                // {section_name} Event Delegation
                {event_delegation_content}
                """)
    
    # Combine all sections into organized JavaScript
    joined_js_sections = "\n".join(cleaned_js_sections)
    joined_state_sections = "\n".join(cleaned_state_sections)
    joined_event_delegations = "\n".join(cleaned_event_delegations)

    # Construct the final JavaScript script
    final_js = f"""
<script>

    // Global State Management
    {joined_state_sections}

    // Section-specific Logic
    {joined_js_sections}

    // Event Delegations
    {joined_event_delegations}

</script>
"""
    return final_js

async def generate_section_style(style_instructions, global_css):
    """Generate context-aware styles for a section"""
    try:
        style_response = await execute_llm_call(
            Predict(Sigs.SectionStyle),
            style_instructions=style_instructions,
            global_css=global_css
        )
        return {
            'css_rules': style_response.css_rules,
            'transitions': style_response.transitions,
        }
    except Exception as e:
        raise Exception(f"Error generating section styles: {str(e)}")

async def build_section_logic(javascript_instructions):
    """Generate context-aware logic for a section"""
    try:
        result = {}
        section_logic = await execute_llm_call(
            Predict(Sigs.InteractionLogic),
            javascript_instructions=javascript_instructions
        )
        if section_logic.needs_javascript:
            result['javascript'] = section_logic.javascript
        if section_logic.need_state_management:
            result['state_management'] = section_logic.state_management
        if section_logic.need_event_delegation:
            result['event_delegation'] = section_logic.event_delegation
            
        return result
    except Exception as e:
        raise Exception(f"Error generating section logic: {str(e)}")

async def generate_section_image_details(image_instructions):
    """Generate image details for a section"""
    try:
        with context(lm=strong_lm):
            image_response = await execute_llm_call(
                ChainOfThought(Sigs.SectionImageDetails),
                image_instructions=image_instructions
            )

            detailed_images = []
            image_generator = ImageGenerator(ssh_manager)
            for image in image_response.image_details:
                image_name = image['image_name']
                image_list = image_generator.generate_image(image["prompt"], image_name)
                image_list[0].update({
                    'alt': image['alt'],
                    'prompt': image['prompt'],
                    'image_name': image_name
                })
                detailed_images.append(image_list[0])

            return detailed_images
    except Exception as e:
        raise Exception(f"Error generating image details: {str(e)}") 

async def build_component_section(
    layout_structure,
    javascript, 
    section_style=None,
    image_details=None,
):
    """
    Build a complete section including structure with positioned image placeholders
    and context-aware accessibility features
    """
    try:
        with context(lm=strong_lm):
            structure_response = await execute_llm_call(
                ChainOfThought(Sigs.ComponentStructure),
                layout_structure=layout_structure,
                section_css_rules=section_style['css_rules'],
                section_javascript=javascript,
                image_details=image_details,
            )
            
            # Combine the markup with accessibility features
            cleaned_markup = clean_markup(structure_response.markup)
            return cleaned_markup 
    except Exception as e:
        logger.error(f"Error in build_component_section: {str(e)}", exc_info=True)
        raise Exception(f"Error building section structure: {str(e)}") 