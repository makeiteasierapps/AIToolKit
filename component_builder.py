import re
import logging
import time
from typing import List, Dict, Literal, Any
import json
import os
from dspy import  LM, configure, InputField, OutputField, Signature, ChainOfThought, context, Predict
from dotenv import load_dotenv
import requests

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
    <!-- Component Scripts -->
    {component_scripts}
</head>
<body>
    <!-- Component Container -->
    <div id="component-root">
        {component_markup}
    </div> 
    <!-- Dynamic Script Loading -->
    {script_imports}
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
class SectionLogic(Signature):
    """Define the interactive behavior for a specific section"""
    section_details = InputField()
    component_type = InputField()
    global_interactions = InputField()
    javascript_code = OutputField(desc='Section-specific behavior and event handling')
    state_requirements = OutputField(desc='State requirements for this section') 
class ComponentLogic(Signature):
    """Define the global state and interaction management"""
    component_type = InputField()
    global_interactions = InputField()
    section_states: List[Dict[str, Any]] = InputField(desc='State requirements from all sections')
    javascript_code = OutputField(desc='Global component behavior and state management')
    initialization_code = OutputField(desc='Component initialization and setup') 
class ComponentStyle(Signature):
    """Define global component styles and theme"""
    visual_theme = InputField()
    component_type = InputField()
    global_css = OutputField(desc='Global styles and CSS variables')
    global_animations = OutputField(desc='Global animations') 
    animation_rules = OutputField(desc='Transition and animation definitions')
class SectionStyle(Signature):
    """Define styles specific to a section"""
    section_details = InputField()
    visual_theme = InputField()
    component_type = InputField()
    section_css = OutputField(desc='Section-specific styles')
    section_animations = OutputField(desc='Section-specific animations')
    scoped_class = OutputField(desc='Unique class for scoping section styles')
class ComponentStructure(Signature):
    """Define the structural layout for a component section"""
    section_details = InputField(desc='Details about the section being built')
    component_type = InputField()
    image_prompt = InputField(desc='Generated image prompt for this section')
    visual_theme = InputField()
    markup = OutputField(desc='HTML structure for the section')
    container_class = OutputField(desc='Main container class for the section')
    image_placeholders: List[Dict[Literal["id", "alt", "dimensions"], str]] = OutputField(desc='Details for image placeholders') 
class ComponentSection(Signature):
    """Generate a specific section of the component"""
    component_type = InputField()
    section_details = InputField()
    visual_theme = InputField()
    media_assets = InputField()
    section_markup = OutputField(desc='HTML structure for the section')
    section_style = OutputField(desc='Specific styles for this section')
    section_logic = OutputField(desc='JavaScript for this section') 
class ImagePromptGenerator(Signature):
    """Generate detailed prompts for AI image generation"""
    section_purpose = InputField()
    visual_theme = InputField()
    component_type = InputField()
    image_requirements = InputField()
    image_prompt = OutputField(desc='Detailed prompt for image generation')
    image_style = OutputField(desc='Style parameters for the image generator') 

def clean_html(html):
    try:
        if not isinstance(html, str):
            raise ValueError("Input must be a string")
        if not html.strip():
            raise ValueError("Input string is empty")
        clean_text = re.sub(r'```html|```', '', html)
        return clean_text.strip()
        
    except re.error as e:
        raise ValueError(f"Error cleaning HTML: {str(e)}")

def transform_image_placeholders(placeholders):
    """Transform list of image placeholders into a dictionary keyed by 'id'"""
    return {placeholder["id"]: {k: v for k, v in placeholder.items() if k != "id"} for placeholder in placeholders}

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
            'css': style_response.section_css,
            'animations': style_response.section_animations,
            'scoped_class': style_response.scoped_class
        }
    except Exception as e:
        raise Exception(f"Error generating section styles: {str(e)}") 

def build_section_logic(section, component_type, global_interactions):
    """Generate logic for a specific section"""
    try:
        section_logic = Predict(SectionLogic)
        logic_response = section_logic(
            section_details=section,
            component_type=component_type,
            global_interactions=global_interactions
        )
        return {
            'javascript': logic_response.javascript_code,
            'state_requirements': logic_response.state_requirements
        }
    except Exception as e:
        raise Exception(f"Error generating section logic: {str(e)}")

def build_component_logic(component_type, global_interactions, section_states):
    """Generate global component logic"""
    try:
        component_logic = Predict(ComponentLogic)
        logic_response = component_logic(
            component_type=component_type,
            global_interactions=global_interactions,
            section_states=section_states
        )
        return {
            'global_javascript': logic_response.javascript_code,
            'init_code': logic_response.initialization_code
        }
    except Exception as e:
        raise Exception(f"Error generating component logic: {str(e)}") 

def build_component_section(section, component_type, visual_theme, image_prompt=None, section_style=None):
    """Build a complete section including structure, styles, and image placeholders"""
    try:
        # Generate structure with image placeholders
        with context(lm=strong_lm):
            structure = ChainOfThought(ComponentStructure)
            structure_response = structure(
                section_details=section,
                component_type=component_type,
                image_prompt=image_prompt,
                visual_theme=visual_theme
            ) 
        # Add scoped class to section markup
        scoped_class = section_style['scoped_class']
        section_markup = f'<div class="{scoped_class}">\n{structure_response.markup}\n</div>' 
        return {
            'markup': section_markup,
            'image_placeholders': structure_response.image_placeholders
        }
    except Exception as e:
        raise Exception(f"Error building section structure: {str(e)}") 

def generate_image_prompt(section, component_type, visual_theme):
    """Generate image generation prompt for a section"""
    try:
        prompt_generator = Predict(ImagePromptGenerator)
        prompt_response = prompt_generator(
            section_purpose=section['purpose'],
            visual_theme=visual_theme,
            component_type=component_type,
            image_requirements=section['image_requirements']
        )
        return {
            'prompt': prompt_response.image_prompt,
            'style': prompt_response.image_style
        }
    except Exception as e:
        raise Exception(f"Error generating image prompt for {section['section_name']}: {str(e)}") 

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

def component_builder_pipeline(prompt):
    def format_sse(data):
        return f"data: {json.dumps(data)}\n\n" 
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

    # Generate Image Prompts
    image_prompts = {}
    try:
        step_start = time.time()
        yield format_sse({"type": "progress", "message": "🎨 Generating image prompts..."}) 
        for section in component_data.sections:
            if 'image_requirements' in section and section['image_requirements']:
                image_prompt_data = generate_image_prompt(
                    section,
                    component_data.component_type,
                    component_data.visual_theme
                )
                image_prompts[section['section_name']] = image_prompt_data 
                yield format_sse({
                    "type": "image_prompt",
                    "section": section['section_name'],
                    "prompt": image_prompt_data['prompt'],
                    "style": image_prompt_data['style']
                }) 
        logger.info(f"Image prompts generated in {time.time() - step_start:.2f} seconds")
    except Exception as e:
        logger.warning(f"Image prompt generation warning: {str(e)}")
        yield format_sse({"type": "warning", "message": "Some image prompts could not be generated"})

    all_image_placeholders = {}
    
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
        
        # Generate section-specific styles
        section_styles = {}
        combined_styles = [] 
        
        # Add global styles first
        combined_styles.append(f'''
            /* Global Styles */
            {global_style_response.global_css} 
            /* Global Animations */
            {global_style_response.global_animations}
        ''') 
        
        # Generate styles for each section
        for section in component_data.sections:
            try:
                section_style_content = generate_section_style(
                    section,
                    component_data.component_type,
                    component_data.visual_theme
                ) 
                # Store section style information
                section_styles[section['section_name']] = section_style_content 
                # Add scoped section styles
                combined_styles.append(f'''
                    /* Styles for section: {section['section_name']} */
                    .{section_style_content['scoped_class']} {{
                        {section_style_content['css']}
                    }} 
                    /* Animations for section: {section['section_name']} */
                    @keyframes {section_style_content['scoped_class']}-animations {{
                        {section_style_content['animations']}
                    }}
                ''') 
                yield format_sse({
                    "type": "progress",
                    "message": f"Generated styles for section: {section['section_name']}"
                }) 
            except Exception as e:
                logger.error(f"Error generating styles for section {section['section_name']}: {str(e)}")
                yield format_sse({
                    "type": "warning",
                    "message": f"Issues with styles for {section['section_name']}: {str(e)}"
                }) 
        
        # Create final style element
        joined_styles = "\n".join(combined_styles)
        final_styles = f'''
            <style>
                {joined_styles}
            </style>
        '''
        
        # Store style data for later use
        style_data = {
            'global_styles': global_style_response,
            'section_styles': section_styles
        } 
        logger.info(f"Step 3 - Styles generated in {time.time() - step_start:.2f} seconds") 
    except Exception as e:
        elapsed = time.time() - pipeline_start
        logger.error(f"Pipeline failed in style step: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})
        return
    
    # Section Building Loop
    try:
        sections = component_data.sections
        total_sections = len(sections)
        accumulated_markup = []
        all_image_placeholders = {} 
        yield format_sse({
            "type": "progress",
            "message": f"🏗️ Building {total_sections} sections..."
        }) 
        for i, section in enumerate(sections, 1):
            section_start = time.time()
            try:
                yield format_sse({
                    "type": "progress",
                    "message": f"📄 Creating section {i}/{total_sections}: {section['section_name']}"
                }) 
                # Get image prompt for this section
                section_image_prompt = image_prompts.get(section['section_name']) 
                # Build section with image placeholders
                section_content = build_component_section(
                    section,
                    component_data.component_type,
                    component_data.visual_theme,
                    section_image_prompt,
                    section_styles[section['section_name']]  # Pass section-specific styles
                )
                print(section_content['image_placeholders'])
                # Track image placeholders
                transformed_placeholders = transform_image_placeholders(section_content['image_placeholders'])
                all_image_placeholders.update(transformed_placeholders)
                accumulated_markup.append(section_content['markup']) 
                # Create intermediate component to show progress
                intermediate_component = COMPONENT_SCAFFOLD.format(
                    component_title=f"Component: {component_data.component_type}",
                    resource_links="",
                    component_styles=final_styles,  # Use the styles generated earlier
                    component_markup="\n".join(accumulated_markup),
                    script_imports="",
                    component_scripts=generate_image_loading_script(all_image_placeholders)
                ) 
                # Send progress update with current state of component
                yield format_sse({
                    "type": "section_complete",
                    "section_name": section['section_name'],
                    "current_component": intermediate_component,
                    "image_placeholders": section_content['image_placeholders'],
                    "progress": {
                        "current": i,
                        "total": total_sections,
                        "section_build_time": time.time() - section_start
                    }
                }) 
                logger.info(f"Section {i}/{total_sections} ({section['section_name']}) built in {time.time() - section_start:.2f} seconds") 
            except Exception as e:
                logger.error(f"Failed building section {i}/{total_sections}: {str(e)}", exc_info=True)
                yield format_sse({
                    "type": "error",
                    "message": str(e),
                    "section": section['section_name']
                })
                continue 
    
        # Construct final component
        final_component = COMPONENT_SCAFFOLD.format(
            component_title=f"Component: {component_data.component_type}",
            resource_links="",  # Add any needed resources
            component_styles=final_styles,  # Include the final styles
            component_markup="\n".join(accumulated_markup),
            script_imports="",  # Add any needed scripts
            component_scripts=generate_image_loading_script(all_image_placeholders)
        ) 
        # Send complete component with image placeholder information
        yield format_sse({
            "type": "component_complete",
            "content": final_component,
            "image_placeholders": all_image_placeholders
        }) 
    except Exception as e:
        elapsed = time.time() - pipeline_start
        logger.error(f"Pipeline failed in section building: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)}) 

    # Component Logic Generation
    try:
        step_start = time.time()
        yield format_sse({"type": "progress", "message": "⚡ Generating component logic..."}) 
        # Track section-specific logic and state requirements
        section_logic = {}
        section_states = [] 
        # Generate logic for each section
        for section in component_data.sections:
            try:
                section_logic_content = build_section_logic(
                    section,
                    component_data.component_type,
                    component_data.global_interactions
                ) 
                section_logic[section['section_name']] = section_logic_content['javascript']
                section_states.append({
                    'section': section['section_name'],
                    'state': section_logic_content['state_requirements']
                }) 
                yield format_sse({
                    "type": "progress",
                    "message": f"Generated logic for section: {section['section_name']}"
                }) 
            except Exception as e:
                logger.error(f"Error in section logic generation: {str(e)}")
                yield format_sse({
                    "type": "warning",
                    "message": f"Issues with logic for {section['section_name']}: {str(e)}"
                }) 
        # Generate global component logic
        component_logic_content = build_component_logic(
            component_data.component_type,
            component_data.global_interactions,
            section_states
        ) 
        # Combine all JavaScript
        section_specific_logic = '\n'.join(section_logic.values())
        final_javascript = f'''
                    // Component Initialization
                    {component_logic_content['init_code']} 
                    // Global Component Logic
                    {component_logic_content['global_javascript']} 
                    // Section-Specific Logic
                    {section_specific_logic}
                '''
        logger.info(f"Step 2 - Logic generated in {time.time() - step_start:.2f} seconds")  
        # Store logic data for later use
        logic_data = {
            'section_logic': section_logic,
            'global_logic': component_logic_content,
            'combined_javascript': final_javascript
        } 
    except Exception as e:
        elapsed = time.time() - pipeline_start
        logger.error(f"Pipeline failed in logic step: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})
        return

    total_time = time.time() - pipeline_start
    logger.info(f"Component pipeline completed in {total_time:.2f} seconds") 
    # Send final completion message
    yield format_sse({
        "type": "pipeline_complete",
        "build_time": total_time,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })