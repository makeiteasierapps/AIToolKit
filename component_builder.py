import re
from pprint import pprint
import replicate
import logging
import time
from typing import List, Dict, Literal
import json
import os
from dspy import  LM, configure, InputField, OutputField, Signature, ChainOfThought, context, Predict
from dotenv import load_dotenv
from SSHManager import SSHManager
from ImageGenManager import ImageGenerator
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
load_dotenv()
os.environ.get("OPENAI_API_KEY")
os.environ.get("ANTHROPIC_API_KEY")
os.environ.get("REPLICATE_API_TOKEN")
model_dict = {
    'sonnet': {'model': 'anthropic/claude-3-5-sonnet-latest', 'max_tokens': 8192},
    'haiku': {'model': 'anthropic/claude-3-haiku-20240307', 'max_tokens': 4096},
    'opus': {'model': 'anthropic/claude-3-opus-latest', 'max_tokens': 4096},
    '4o-mini': {'model': 'openai/gpt-4o-mini', 'max_tokens': 4096},
    '4o': {'model': 'openai/gpt-4o', 'max_tokens': 4096},
}
lm = LM(model_dict['4o-mini']['model'], max_tokens=model_dict['4o-mini']['max_tokens'], cache=False)
strong_lm = LM(model_dict['4o-mini']['model'], max_tokens=model_dict['4o-mini']['max_tokens'], cache=False)
configure(lm=lm)
logger = logging.getLogger('app.component_builder')

class WebAppArchitect(Signature):
    """Design a modern, responsive web app UI using Tailwind CSS for styling.
    Focus on:
    - Tailwind's utility-first approach for styling
    - Vanilla JavaScript for interactivity
    - Responsive design using Tailwind's breakpoint system
    - Modern layout patterns with Tailwind's flex and grid utilities
    - Simple, clean animations using Tailwind's transition utilities."""
    description = InputField(desc='The user\'s requirements')
    component_blueprint = OutputField(desc='Detailed high-level web app UI description and purpose')
    global_css = OutputField(desc='Global Tailwind configurations and any necessary custom CSS')
    global_javascript = OutputField(desc='Clean, vanilla JavaScript code') 
class SectionArchitect(Signature):
    """Design section-specific UI components using modern Tailwind patterns.
    Implement:
    - Tailwind's built-in animation and transition classes
    - Simple interactive elements using vanilla JavaScript
    - Tailwind's state modifiers (hover, focus, etc.)
    - Responsive patterns using Tailwind breakpoints
    - Clean event handling with vanilla JavaScript"""
    global_css = InputField()
    component_blueprint = InputField()
    sections: List[Dict[Literal[
        "section_name",
        "section_details",
        "image_requirements",
        "css_style_and_animation_instructions",
        "javascript_instructions"
    ], str]] = OutputField(desc='Instructions using Tailwind classes and vanilla JavaScript')  
class InteractionLogic(Signature):
    """Define interactive behaviors with awareness of component-wide context"""
    javascript_instructions = InputField()
    needs_javascript: bool = OutputField(desc='Whether the section needs JavaScript')
    javascript = OutputField(desc='Non-style related JavaScript functionality')
    need_state_management: bool = OutputField(desc='Whether the section needs state management')
    need_event_delegation: bool = OutputField(desc='Whether the section needs event delegation')
    state_management = OutputField(desc='JS code for Data and state handling logic')
    event_delegation = OutputField(desc='JS code for event handling')
class SectionImageDetails(Signature):
    """Generate image prompts that will be used to generate images"""
    image_instructions = InputField()
    image_details: List[Dict[Literal[
        "image_id",
        "alt",
        "prompt",
    ], str]] = OutputField(desc='prompt should be detailed and verbose') 
class SectionStyle(Signature):
    """Define section styles with awareness of global context"""
    style_instructions = InputField()
    global_css = InputField()
    css_rules = OutputField()
    transitions = OutputField(desc='CSS transitions and keyframe animations')
class ComponentStructure(Signature):
    """Create semantic HTML5 markup with Tailwind utility classes.
    Include:
    - Semantic HTML5 elements with Tailwind classes
    - Data attributes for JavaScript interactions
    - Tailwind's built-in responsive utilities
    - Simple state management with data attributes
    - Clean, readable markup structure"""
    section_details = InputField()
    section_css_rules = InputField()
    section_javascript = InputField()
    image_details = InputField()
    markup = OutputField(desc='Response should contain HTML with Tailwind classes')

def test_component_builder(prompt):
    try:
        input = {
            "prompt": prompt,
            "guidance": 3.5
        }

        output = replicate.run(
            "black-forest-labs/flux-dev",
            input=input
        )
        print(f"output: {output}")
        for index, item in enumerate(output):
            with open(f"output_{index}.webp", "wb") as file:
                file.write(item.read())
    except Exception as e:
        logger.error(f"Component architect failed: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

def component_builder_pipeline(prompt):
    start = time.time()
    logger.info(f"Starting pipeline: {prompt[:100]}...") 
    try:
        yield format_sse({"type": "progress", "message": "🎯 Analyzing requirements..."}) 
        # Generate initial component definition with enhanced context
        with context(lm=strong_lm):
            web_app_architect = ChainOfThought(WebAppArchitect)(description=prompt)
            section_architect = ChainOfThought(SectionArchitect)(
                global_css=web_app_architect.global_css,
                component_blueprint=web_app_architect.component_blueprint
            )
            print(f"section_architect: {section_architect.sections}")
        yield format_sse({
            "type": "progress", 
            "message": 'Design complete'
        }) 
    except Exception as e:
        logger.error(f"Definition failed: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})
        return 
    styles = []
    markup = []
    images = {}
    section_logic = {} 
    try:
        yield format_sse({"type": "progress", "message": "🎨 Generating global styles..."}) 
        
        styles.append(f"""
            /* Global Styles */
            {web_app_architect.global_css}
        """) 
    except Exception as e:
        logger.error(f"Style failed: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})
        return 
    # Process each section with enhanced context awareness
    for i, section in enumerate(section_architect.sections, 1):
        try:
            yield format_sse({
                "type": "progress",
                "message": f"🏗️ Section {i}/{len(section_architect.sections)}: {section['section_name']}"
            }) 
            # Generate images with context
            if 'image_requirements' in section:
                section_images = generate_section_image_details(
                    section_name=section['section_name'],
                    image_instructions=section['image_requirements']
                )
                images.update(section_images)

            # Generate section-specific styles with context
            section_style = generate_section_style(
                style_instructions=section['css_style_and_animation_instructions'],
                global_css=web_app_architect.global_css
            ) 
            styles.append(f"""
                /* {section['section_name']} */
                {section_style['css_rules']}
                {section_style['transitions']}
            """)

            # Generate section logic with context
            logic = build_section_logic(
                javascript_instructions=section['javascript_instructions']
            )
            section_logic[section['section_name']] = logic 
            # Build section structure with context
            markup.append(build_component_section(
                section_details=section['section_details'],
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
            logger.error(f"Section {section['section_name']} failed: {str(e)}")
            yield format_sse({
                "type": "warning",
                "message": f"Section issue: {str(e)}"
            }) 
    # Generate final component with all context-aware parts
    final = create_component_scaffold(
        styles=f"<style>{' '.join(styles)}</style>",
        markup=markup,
        section_logic=section_logic
    ) 
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

def generate_section_style(style_instructions, global_css):
    """Generate context-aware styles for a section"""
    try:
        section_style = Predict(SectionStyle)
        style_response = section_style(
            style_instructions=style_instructions,
            global_css=global_css
        )
        return {
            'css_rules': style_response.css_rules,
            'transitions': style_response.transitions,
        }
    except Exception as e:
        raise Exception(f"Error generating section styles: {str(e)}")

def build_section_logic(javascript_instructions):
    """Generate context-aware logic for a section"""
    try:
        result = {}
        section_logic = Predict(InteractionLogic)(javascript_instructions=javascript_instructions)
        if section_logic.needs_javascript:
            result['javascript'] = section_logic.javascript
        if section_logic.need_state_management:
            result['state_management'] = section_logic.state_management
        if section_logic.need_event_delegation:
            result['event_delegation'] = section_logic.event_delegation
            
        return result
    except Exception as e:
        raise Exception(f"Error generating section logic: {str(e)}")

def generate_section_image_details(section_name, image_instructions):
    """Generate image details for a section"""
    try:
        with context(lm=strong_lm):
            image_generator = ChainOfThought(SectionImageDetails)
            image_response = image_generator(
                image_instructions=image_instructions
            ) 
            detailed_images = {}
            for image in image_response.image_details:
                image_id = f"{section_name.lower()}-{image['image_id']}"
                detailed_images[image_id] = {
                    "alt": image["alt"],
                    "prompt": image["prompt"],
                }
            return detailed_images
    except Exception as e:
        raise Exception(f"Error generating image details: {str(e)}") 

def build_component_section(
    section_details, 
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
            structure = Predict(ComponentStructure)
            print(f"image_details: {image_details}")
            structure_response = structure(
                section_details=section_details,
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

# def generate_image_loading_script(image_placeholders):
#     """Generate JavaScript to handle image loading and replacement"""
#     return f'''
#     <script>
#     const imagePlaceholders = {json.dumps(image_placeholders)}; 
#     function loadGeneratedImage(imageId, imageUrl) {{
#         const placeholder = document.querySelector(`[data-image-id="${{imageId}}"]`);
#         if (placeholder) {{
#             const img = new Image();
#             img.src = imageUrl;
#             img.alt = imagePlaceholders[imageId].alt;
#             img.className = 'generated-image'; 
#             img.onload = () => {{
#                 placeholder.querySelector('.loading-indicator').style.display = 'none';
#                 placeholder.appendChild(img);
#                 img.style.opacity = '1';
#             }};
#         }}
#     }} 
#     // Function to be called when images are generated
#     window.updateGeneratedImages = function(imageMapping) {{
#         Object.entries(imageMapping).forEach(([imageId, imageUrl]) => {{
#             loadGeneratedImage(imageId, imageUrl);
#         }});
#     }};
#     </script>
#     '''
