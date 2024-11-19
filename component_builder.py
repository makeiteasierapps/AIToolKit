import re
import pprint
import logging
import time
from typing import List, Dict, Literal, Any
import json
import os
from dspy import  LM, configure, InputField, OutputField, Signature, ChainOfThought, context, Predict
from dotenv import load_dotenv

COMPONENT_SCAFFOLD = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component_title}</title> 
    <!-- Dynamic Resource Loading -->
    {resource_links} 
    <!-- Component Styles -->
    {component_styles} 
    
</head>
<body>
    <!-- Component Container -->
    <div id="component-root">
        {component_markup}
    </div> 
    <!-- Dynamic Script Loading -->
    {script_imports}
    <!-- Component Scripts -->
    {component_scripts}
</body>
</html>
'''
load_dotenv()
os.environ.get("OPENAI_API_KEY")
os.environ.get("ANTHROPIC_API_KEY")
model_dict = {
    'sonnet': {'model': 'anthropic/claude-3-5-sonnet-latest', 'max_tokens': 8192},
    'haiku': {'model': 'anthropic/claude-3-haiku-20240307', 'max_tokens': 4096},
    'opus': {'model': 'anthropic/claude-3-opus-latest', 'max_tokens': 4096},
    '4o-mini': {'model': 'openai/gpt-4o-mini', 'max_tokens': 4096},
    '4o': {'model': 'openai/gpt-4o', 'max_tokens': 4096},
}
lm = LM(model_dict['4o-mini']['model'], max_tokens=model_dict['4o-mini']['max_tokens'])
strong_lm = LM(model_dict['4o-mini']['model'], max_tokens=model_dict['4o-mini']['max_tokens'])
configure(lm=lm)
logger = logging.getLogger('app.component_builder')

class ComponentDefinition(Signature):
    """Analyze the user's needs and define appropriate UI/UX components"""
    description = InputField(desc='The user\'s requirements')
    component_type = OutputField(desc='Type of UI/UX component (web, mobile, dashboard, etc.)')
    sections: List[Dict[Literal["section_name", "purpose", "interaction_type", "image_requirements"], str]] = OutputField()
    visual_theme = OutputField(desc='Visual design guidelines')
    global_interactions: List[Dict[Literal["event_type", "scope", "behavior"], str]] = OutputField(desc='Component-wide interaction patterns') 
class InteractionLogic(Signature):
    """Define pure interactive behaviors excluding visual styles"""
    section_details = InputField()
    component_type = InputField()
    global_interactions = InputField()
    event_handlers = OutputField(desc='Non-style related JavaScript functionality')
    state_management = OutputField(desc='Data and state handling logic')
class SectionImageDetails(Signature):
    """Generate detailed image specifications for a section"""
    section_details = InputField(desc="Section configuration and requirements")
    component_type = InputField(desc="Type of component being built")
    visual_theme = InputField(desc="Visual theme guidelines")
    image_details: List[Dict[Literal[
        "image_id",
        "alt",
        "prompt",
        "dimensions",
        "position",
        "style_focus"
    ], str]] = OutputField(
        desc="List of image specifications including prompts and placement details"
    )
class ComponentStyle(Signature):
    """Define global component styles and theme"""
    visual_theme = InputField()
    component_type = InputField()
    global_css = OutputField(desc='Global styles and CSS variables')
    global_animations = OutputField(desc='Global animations') 
    animation_rules = OutputField(desc='Transition and animation definitions')
class SectionStyle(Signature):
    """Define styles and transitions for a section"""
    section_details = InputField()
    visual_theme = InputField()
    component_type = InputField()
    css_rules = OutputField(desc='Core styles including responsive and state variations')
    transitions = OutputField(desc='CSS transitions and keyframe animations')
    motion_preferences = OutputField(desc='Reduced motion and accessibility considerations')
class ComponentStructure(Signature):
    """Define the structural layout for a component section"""
    section_details = InputField(desc='Details about the section being built')
    component_type = InputField()
    section_css_rules = InputField()
    section_javascript = InputField(desc='A reference to help ensure all sections are built correctly')
    image_details = InputField(desc='details of images to be used in the section')
    markup = OutputField(desc='HTML structure for the section')

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

def create_component_scaffold(component_type: str, styles: str, markup: List[str], image_placeholders: Dict, section_logic: Dict[str, str] = None) -> str:
    cleaned_styles = clean_markup(styles)
    cleaned_markup = [clean_markup(section) for section in markup]
    
    js_code = ""
    if section_logic:
        js_code = flatten_section_logic(section_logic)
    
    return COMPONENT_SCAFFOLD.format(
        component_title=f"Component: {component_type}",
        resource_links="",
        component_styles=cleaned_styles,
        component_markup="\n".join(cleaned_markup),
        script_imports="",
        component_scripts=f"{generate_image_loading_script(image_placeholders)}\n{js_code}"
    )

def generate_section_image_details(section, component_type, visual_theme):
    """Generate comprehensive image details for a section"""
    try:
        with context(lm=strong_lm):
            image_generator = ChainOfThought(SectionImageDetails)
            image_response = image_generator(
                section_details=section,
                component_type=component_type,
                visual_theme=visual_theme
            ) 
            # Transform the response into a structured format
            detailed_images = {}
            for image in image_response.image_details:
                image_id = f"{section['section_name'].lower()}-{image['image_id']}"
                detailed_images[image_id] = {
                    "alt": image["alt"],
                    "prompt": image["prompt"],
                    "dimensions": image["dimensions"],
                    "position": image["position"],
                    "style_focus": image["style_focus"]
                } 
            return detailed_images 
    except Exception as e:
        raise Exception(f"Error generating image details: {str(e)}")

def format_sse(data):
    return f"data: {json.dumps(data)}\n\n"

def generate_section_style(section, component_type, visual_theme):
    """Generate styles for a specific section"""
    try:
        section_style = Predict(SectionStyle)
        style_response = section_style(
            section_details=section,
            visual_theme=visual_theme,
            component_type=component_type
        )
        return {
            'css_rules': style_response.css_rules,
            'transitions': style_response.transitions,
            'motion_preferences': style_response.motion_preferences
        }
    except Exception as e:
        raise Exception(f"Error generating section styles: {str(e)}") 

def build_section_logic(section, component_type, global_interactions):
    """Generate logic for a specific section"""
    try:
        section_logic = Predict(InteractionLogic)
        logic_response = section_logic(
            section_details=section,
            component_type=component_type,
            global_interactions=global_interactions
        )
        return {
            'javascript': logic_response.event_handlers,
            'state_management': logic_response.state_management
        }
    except Exception as e:
        raise Exception(f"Error generating section logic: {str(e)}")

def build_component_section(
    section, 
    component_type, 
    javascript, 
    section_style=None,
    image_details=None
):
    """Build a complete section including structure with positioned image placeholders"""
    try:
        with context(lm=strong_lm):
            structure = ChainOfThought(ComponentStructure)
            structure_response = structure(
                section_details=section,
                component_type=component_type,
                section_css_rules=section_style['css_rules'],
                section_javascript=javascript,
                image_details=image_details
            ) 
        return structure_response.markup
        
    except Exception as e:
        raise Exception(f"Error building section structure: {str(e)}") 

def generate_image_loading_script(image_placeholders):
    """Generate JavaScript to handle image loading and replacement"""
    return f'''
    <script>
    const imagePlaceholders = {json.dumps(image_placeholders)}; 
    function loadGeneratedImage(imageId, imageUrl) {{
        const placeholder = document.querySelector(`[data-image-id="${{imageId}}"]`);
        if (placeholder) {{
            const img = new Image();
            img.src = imageUrl;
            img.alt = imagePlaceholders[imageId].alt;
            img.className = 'generated-image'; 
            img.onload = () => {{
                placeholder.querySelector('.loading-indicator').style.display = 'none';
                placeholder.appendChild(img);
                img.style.opacity = '1';
            }};
        }}
    }} 
    // Function to be called when images are generated
    window.updateGeneratedImages = function(imageMapping) {{
        Object.entries(imageMapping).forEach(([imageId, imageUrl]) => {{
            loadGeneratedImage(imageId, imageUrl);
        }});
    }};
    </script>
    '''

def flatten_section_logic(section_logic: Dict[str, str]) -> str:
    """Flatten multiple sections of JavaScript into a single coherent script."""
    
    # Extract JS content from each section, removing the markdown code blocks
    cleaned_sections = []
    for section_name, js_content in section_logic.items():
        # Remove markdown code blocks and clean whitespace
        clean_js = re.sub(r'```javascript\s*|```\s*', '', js_content).strip()
        
        # Wrap section code in IIFE with section name comment
        section_wrapped = f"""
// {section_name} Section Logic
(function() {{
    {clean_js}
}})();
"""
        cleaned_sections.append(section_wrapped)
    
    # Combine all sections and wrap in DOMContentLoaded
    combined_js = "\n".join(cleaned_sections)
    final_js = f"""
<script>
document.addEventListener('DOMContentLoaded', function() {{
    {combined_js}
}});
</script>
"""
    print(final_js)
    return final_js

def component_builder_pipeline(prompt):
    pipeline_start = time.time()
    logger.info(f"Starting component builder pipeline with prompt: {prompt[:100]}...") 
    
    # Component Definition
    try:
        step_start = time.time()
        yield format_sse({"type": "progress", "message": "🎯 Analyzing component requirements..."}) 
        with context(lm=strong_lm):
            component_def = ChainOfThought(ComponentDefinition)
            component_data = component_def(description=prompt)
        logger.info(f"Step 1 - Component defined in {time.time() - step_start:.2f} seconds")
        yield format_sse({
            "type": "progress",
            "message": f"📦 Component Type: {component_data.component_type}"
        })
    except Exception as e:
        elapsed = time.time() - pipeline_start
        logger.error(f"Pipeline failed in definition step: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})
        return 

    # Initialize collection structures
    section_styles = {}
    section_logic = {}
    accumulated_markup = []
    all_image_placeholders = {}
    combined_styles = []    
    
    # Style Generation
    try:
        step_start = time.time()
        yield format_sse({"type": "progress", "message": "🎨 Generating component styles..."}) 
        
        # Generate global styles
        style = Predict(ComponentStyle)
        global_style_response = style(
            visual_theme=component_data.visual_theme,
            component_type=component_data.component_type
        )
        
        combined_styles = [f'''
            /* Global Styles */
            {global_style_response.global_css} 
            /* Global Animations */
            {global_style_response.global_animations}
        ''']

        # Create final style element
        joined_styles = "\n".join(combined_styles)
        final_styles = f'''
            <style>
                {joined_styles}
            </style>
        '''

        logger.info(f"Step 3 - Styles generated in {time.time() - step_start:.2f} seconds") 
    except Exception as e:
        elapsed = time.time() - pipeline_start
        logger.error(f"Pipeline failed in style step: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})
        return
    
    # Section Building Loop
    total_sections = len(component_data.sections)
    for i, section in enumerate(component_data.sections, 1):
        section_start = time.time()
        section_name = section['section_name'] 
        try:
            yield format_sse({
                "type": "progress",
                "message": f"🏗️ Building section {i}/{total_sections}: {section_name}"
            }) 
            # 1. Generate Image Prompts
            section_images = None
            if 'image_requirements' in section:
                section_images = generate_section_image_details(
                    section,
                    component_data.component_type,
                    component_data.visual_theme
                )
                all_image_placeholders.update(section_images) 
        
            # 2. Generate Section Styles
            section_styling = generate_section_style(
                section,
                component_data.component_type,
                component_data.visual_theme
            )
            section_styles[section_name] = section_styling
            
            combined_styles.append(f'''
                /* Base styles: {section_name} */
                {section_styling['css_rules']} 
                /* States and interactions */
                {section_styling['transitions']} 
                /* Motion preferences */
                @media (prefers-reduced-motion: reduce) {{
                    {section_styling['motion_preferences']}
                }}
            ''')

            # Generate Section Logic
            section_logic = build_section_logic(
                section,
                component_data.component_type,
                component_data.global_interactions
            )
            section_logic[section_name] = section_logic['javascript']  

            # Build Section Content
            html_markup = build_component_section(
                section,
                component_data.component_type,
                section_logic['javascript'],
                section_styling,
                image_details=section_images
            )

            accumulated_markup.append(html_markup)

            # Create and yield intermediate component state
            joined_styles = "\n".join(combined_styles)
            final_styles = f"<style>{joined_styles}</style>"
            intermediate_component = create_component_scaffold(
                component_data.component_type,
                final_styles,
                accumulated_markup,
                all_image_placeholders
            )
            yield format_sse({
                "type": "section_complete",
                "section_name": section_name,
                "current_component": intermediate_component,
                "progress": {
                    "current": i,
                    "total": total_sections,
                    "section_build_time": time.time() - section_start
                }
            }) 
        except Exception as e:
            logger.error(f"Error processing section {section_name}: {str(e)}")
            yield format_sse({
                "type": "warning",
                "message": f"Issues with section {section_name}: {str(e)}"
            })
            continue
    final_component = create_component_scaffold(
        component_data.component_type,
        final_styles,
        accumulated_markup,
        all_image_placeholders,
        section_logic
    )

    # Send complete component with image placeholder information
    yield format_sse({
        "type": "component_complete",
        "content": final_component,
        "image_placeholders": all_image_placeholders
    }) 
    
    elapsed = time.time() - pipeline_start
    logger.error(f"Pipeline failed in section building: {str(e)}", exc_info=True)
    yield format_sse({"type": "error", "message": str(e)}) 


    total_time = time.time() - pipeline_start
    logger.info(f"Component pipeline completed in {total_time:.2f} seconds") 
    # Send final completion message
    yield format_sse({
        "type": "pipeline_complete",
        "build_time": total_time,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })