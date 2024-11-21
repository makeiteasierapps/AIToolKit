import re
from pprint import pprint
import logging
import time
from typing import List, Dict, Literal, Union
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
lm = LM(model_dict['4o-mini']['model'], max_tokens=model_dict['4o-mini']['max_tokens'], cache=False)
strong_lm = LM(model_dict['4o-mini']['model'], max_tokens=model_dict['4o-mini']['max_tokens'], cache=False)
configure(lm=lm)
logger = logging.getLogger('app.component_builder')

class ComponentArchitect(Signature):
    """Design a web component"""
    description = InputField(desc='The user\'s requirements') 
    # Output Fields for overall architecture
    component_blueprint = OutputField(desc='Detailed and verbose component blueprint')
    component_outline: List[Dict[Literal[
        "section_id",
        "section_type",
        "responsibility",
        "javascript_instructions",
    ], Union[str, List[str]]]] = OutputField(desc='A compponent level outline')
class ComponentDefinition(Signature):
    """Analyze user needs and define component architecture with clear contextual guidance"""
    description = InputField(desc='The user\'s requirements')
    component_type = OutputField(desc='Type of UI/UX component (web, mobile, dashboard, etc.)') 
    # New fields for improved context and guidance
    component_purpose = OutputField(desc='Clear statement of component\'s main purpose and goals')
    user_story = OutputField(desc='Primary user journey and expected outcomes')
    design_principles = OutputField(desc='Key design principles to maintain throughout') 
    sections: List[Dict[Literal[
        "section_name",
        "purpose",
        "interaction_type",
        "image_requirements",
        "section_context",  
        "dependencies"
    ], str]] = OutputField() 
    visual_theme = OutputField(desc='Visual design guidelines')
    global_interactions: List[Dict[Literal[
        "event_type",
        "scope",
        "behavior",
        "purpose"
    ], str]] = OutputField() 
class ComponentContext(Signature):
    """Central context manager for maintaining component coherence"""
    # Input fields
    component_purpose = InputField()
    user_story = InputField()
    design_principles = InputField()
    visual_theme = InputField() 
    # Output fields
    section_relationships = OutputField(desc='How sections interact and depend on each other')
    state_flow = OutputField(desc='Component-wide state management strategy')
    context_guidelines = OutputField(desc='Guidelines for maintaining component coherence')
    component_strategy = OutputField(desc='Overall component strategy and goals') 
class InteractionLogic(Signature):
    """Define interactive behaviors with awareness of component-wide context"""
    section_details = InputField()
    component_type = InputField()
    global_interactions = InputField()
    component_context = InputField(desc='Reference to overall component goals and principles') 
    javascript = OutputField(desc='Non-style related JavaScript functionality')
    state_management = OutputField(desc='JS code for Data and state handling logic')
    event_delegation = OutputField(desc='JS code for event handling and bubbling strategy')
    section_api = OutputField(desc='JS code for inter-section communication') 
class SectionImageDetails(Signature):
    """Generate image specifications aligned with component goals"""
    section_details = InputField()
    component_type = InputField()
    visual_theme = InputField()
    component_context = InputField()  # New: Overall component context 
    image_details: List[Dict[Literal[
        "image_id",
        "alt",
        "prompt",
        "dimensions",
        "position",
        "style_focus",
        "purpose",           # New: Image's role in component
        "content_strategy"   # New: Content guidelines
    ], str]] = OutputField() 
class ComponentStyle(Signature):
    """Define cohesive component styles with context awareness"""
    visual_theme = InputField()
    component_type = InputField()
    component_context = InputField()
    global_css = OutputField()
    global_animations = OutputField()
    animation_rules = OutputField()
    style_tokens = OutputField(desc='Reusable style values and patterns')
    responsive_strategy = OutputField(desc='Breakpoint and adaptation strategy') 
class SectionStyle(Signature):
    """Define section styles with awareness of global context"""
    section_details = InputField()
    visual_theme = InputField()
    component_type = InputField()
    component_context = InputField()
    global_style_tokens = InputField()
    css_rules = OutputField()
    transitions = OutputField(desc='CSS transitions and keyframe animations')
    style_dependencies = OutputField(desc='Dependencies on other section styles') 
class ComponentStructure(Signature):
    """Define section structure with contextual awareness"""
    section_details = InputField()
    component_type = InputField()
    section_css_rules = InputField()
    section_javascript = InputField()
    image_details = InputField()
    component_context = InputField()
    markup = OutputField()
    accessibility_markup = OutputField(desc='ARIA and accessibility attributes')
    content_structure = OutputField(desc='Semantic structure and hierarchy')

def test_component_builder(prompt):
    try:
        print(prompt)
        architect = ChainOfThought(ComponentArchitect)(description=prompt)
        print(architect)
        # Convert the architect object to a dictionary for JSON serialization
        return {
            "component_blueprint": architect.component_blueprint,
            "component_outline": architect.component_outline,
        }
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
            component_data = ChainOfThought(ComponentDefinition)(description=prompt) 
            # Generate component-wide context
            component_context = ChainOfThought(ComponentContext)(
                component_purpose=component_data.component_purpose,
                user_story=component_data.user_story,
                design_principles=component_data.design_principles,
                visual_theme=component_data.visual_theme
            ) 
        yield format_sse({
            "type": "progress", 
            "message": f"""
            📦 Type: {component_data.component_type}
            🎯 Strategy: {component_context.component_strategy}
            🔄 State Flow: {component_context.state_flow}
            """
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
        # Generate global styles with context awareness
        global_style = Predict(ComponentStyle)(
            visual_theme=component_data.visual_theme,
            component_type=component_data.component_type,
            component_context=component_context
        ) 
        styles.append(f"""
            /* Global Styles */
            {global_style.global_css}
            /* Global Animations */
            {global_style.global_animations}
            /* Style Tokens */
            {global_style.style_tokens}
            /* Responsive Strategy */
            {global_style.responsive_strategy}
        """) 
    except Exception as e:
        logger.error(f"Style failed: {str(e)}", exc_info=True)
        yield format_sse({"type": "error", "message": str(e)})
        return 
    # Process each section with enhanced context awareness
    for i, section in enumerate(component_data.sections, 1):
        try:
            yield format_sse({
                "type": "progress",
                "message": f"🏗️ Section {i}/{len(component_data.sections)}: {section['section_name']}\nContext: {section['section_context']}"
            }) 
            # Generate images with context
            if 'image_requirements' in section:
                section_images = generate_section_image_details(
                    section=section,
                    component_type=component_data.component_type,
                    visual_theme=component_data.visual_theme,
                    component_context=component_context
                )
                images.update(section_images) 
            # Generate section-specific styles with context
            section_style = generate_section_style(
                section=section,
                component_type=component_data.component_type,
                visual_theme=component_data.visual_theme,
                component_context=component_context,
                global_style_tokens=global_style.style_tokens
            ) 
            styles.append(f"""
                /* {section['section_name']} */
                {section_style['css_rules']}
            """) 
            # Generate section logic with context
            logic = build_section_logic(
                section=section,
                component_type=component_data.component_type,
                global_interactions=component_data.global_interactions,
                component_context=component_context
            )
            section_logic[section['section_name']] = logic 
            # Build section structure with context
            markup.append(build_component_section(
                section=section,
                component_type=component_data.component_type,
                javascript=logic['javascript'],
                section_style=section_style,
                image_details=section_images,
                component_context=component_context
            )) 
            # Provide intermediate feedback
            yield format_sse({
                "type": "section_complete",
                "current_component": create_component_scaffold(
                    component_type=component_data.component_type,
                    styles=f"<style>{' '.join(styles)}</style>",
                    markup=markup,
                    image_placeholders=images,
                    section_logic=section_logic
                )
            }) 
        except Exception as e:
            logger.error(f"Section {section['section_name']} failed: {str(e)}")
            yield format_sse({
                "type": "warning",
                "message": f"Section issue: {str(e)}"
            }) 
    # Generate final component with all context-aware parts
    final = create_component_scaffold(
        component_type=component_data.component_type,
        styles=f"<style>{' '.join(styles)}</style>",
        markup=markup,
        image_placeholders=images,
        section_logic=section_logic
    ) 
    # Final outputs
    yield format_sse({
        "type": "component_complete",
        "content": final,
        "image_placeholders": images,
        "component_context": {
            "purpose": component_data.component_purpose,
            "user_story": component_data.user_story,
            "design_principles": component_data.design_principles
        }
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

def flatten_section_logic(section_logic: Dict[str, Dict[str, str]]) -> str:
    """Flatten multiple sections of JavaScript into a single coherent script."""
    # Lists to store cleaned sections of JavaScript logic
    cleaned_js_sections = []
    cleaned_state_sections = []
    cleaned_event_delegations = []
    cleaned_section_apis = []
    
    # Collect all section APIs
    section_apis = {}

    for section_name, logic in section_logic.items():
        # Process JavaScript logic
        js_content = re.sub(r'```javascript\s*|```\s*', '', logic.get('javascript', '')).strip()
        if js_content:
            cleaned_js_sections.append(f"""
        // {section_name} Section Logic
        {js_content}
        """)
        
        # Process state management logic
        state_content = re.sub(r'```javascript\s*|```\s*', '', logic.get('state_management', '')).strip()
        if state_content:
            cleaned_state_sections.append(f"""
        // {section_name} State Management
        {state_content}
        """)
        
        # Process event delegation logic
        event_delegation_content = re.sub(r'```javascript\s*|```\s*', '', logic.get('event_delegation', '')).strip()
        if event_delegation_content:
            cleaned_event_delegations.append(f"""
        // {section_name} Event Delegation
        {event_delegation_content}
        """)
        
        # Collect section API
        if 'section_api' in logic:
            section_apis[section_name] = logic['section_api']
    
    combined_apis = combine_section_apis(section_apis)
    # Combine all sections into organized JavaScript
    joined_js_sections = "\n".join(cleaned_js_sections)
    joined_state_sections = "\n".join(cleaned_state_sections)
    joined_event_delegations = "\n".join(cleaned_event_delegations)

    # Construct the final JavaScript script
    final_js = f"""
<script>
document.addEventListener('DOMContentLoaded', function() {{
    // Global State Management
    {joined_state_sections}

    // Section-specific Logic
    {joined_js_sections}

    // Event Delegations
    {joined_event_delegations}

    // Section APIs
    {combined_apis}
}});
</script>
"""
    return final_js

def generate_section_style(section, component_type, visual_theme, component_context, global_style_tokens):
    """Generate context-aware styles for a section"""
    try:
        section_style = Predict(SectionStyle)
        style_response = section_style(
            section_details=section,
            visual_theme=visual_theme,
            component_type=component_type,
            component_context=component_context,
            global_style_tokens=global_style_tokens
        )
        return {
            'css_rules': style_response.css_rules,
            'transitions': style_response.transitions,
            'style_dependencies': style_response.style_dependencies
        }
    except Exception as e:
        raise Exception(f"Error generating section styles: {str(e)}")

def build_section_logic(section, component_type, global_interactions, component_context):
    """Generate context-aware logic for a section"""
    try:
        section_logic = Predict(InteractionLogic)
        logic_response = section_logic(
            section_details=section,
            component_type=component_type,
            global_interactions=global_interactions,
            component_context=component_context
        )
        return {
            'javascript': logic_response.javascript,
            'state_management': logic_response.state_management,
            'event_delegation': logic_response.event_delegation,
            'section_api': logic_response.section_api
        }
    except Exception as e:
        raise Exception(f"Error generating section logic: {str(e)}")

def generate_section_image_details(section, component_type, visual_theme, component_context):
    """Generate context-aware image details for a section"""
    try:
        with context(lm=strong_lm):
            image_generator = ChainOfThought(SectionImageDetails)
            image_response = image_generator(
                section_details=section,
                component_type=component_type,
                visual_theme=visual_theme,
                component_context=component_context
            ) 
            detailed_images = {}
            for image in image_response.image_details:
                image_id = f"{section['section_name'].lower()}-{image['image_id']}"
                detailed_images[image_id] = {
                    "alt": image["alt"],
                    "prompt": image["prompt"],
                    "dimensions": image["dimensions"],
                    "position": image["position"],
                    "style_focus": image["style_focus"],
                    "purpose": image["purpose"],
                    "content_strategy": image["content_strategy"]
                }
            return detailed_images
    except Exception as e:
        raise Exception(f"Error generating image details: {str(e)}") 

def build_component_section(
    section, 
    component_type, 
    javascript, 
    section_style=None,
    image_details=None,
    component_context=None
):
    """
    Build a complete section including structure with positioned image placeholders
    and context-aware accessibility features
    """
    try:
        with context(lm=strong_lm):
            structure = ChainOfThought(ComponentStructure) 
            # Prepare section-specific context from global context
            section_context = {
                "purpose": section.get('section_context', ''),
                "dependencies": section.get('dependencies', []),
                "relationships": component_context.section_relationships,
                "state_flow": component_context.state_flow,
                "accessibility": component_context.accessibility_guidelines,
                "strategy": component_context.component_strategy,
                "guidelines": component_context.context_guidelines
            }
            structure_response = structure(
                section_details=section,
                component_type=component_type,
                section_css_rules=section_style['css_rules'],
                section_javascript=javascript,
                image_details=image_details,
                component_context=section_context
            ) 
            # Combine the markup with accessibility features
            cleaned_markup = clean_markup(structure_response.markup) 
            return cleaned_markup 
    except Exception as e:
        logger.error(f"Error in build_component_section: {str(e)}", exc_info=True)
        raise Exception(f"Error building section structure: {str(e)}") 

def combine_section_apis(section_apis: Dict[str, str]) -> str:
    """
    Combines multiple section APIs into a single organized JavaScript object.
    
    Args:
        section_apis: Dictionary with section names as keys and API content as values
    
    Returns:
        String containing JavaScript code for the combined API object
    """
    # Start the combined API object
    combined_js = """
    // Combined Section APIs
    const componentAPI = {
    """
    
    for section_name, api_content in section_apis.items():
        # Clean the section name for use as an object key
        clean_section_name = section_name.lower().replace(' ', '_').replace('-', '_')
        
        # Extract the API object content between curly braces
        match = re.search(r'const\s+sectionAPI\s*=\s*({[\s\S]*?});', api_content)
        if match:
            api_object_content = match.group(1).strip()
            
            # Add the section as a namespace in the combined API
            combined_js += f"""
        // {section_name} API
        {clean_section_name}: {api_object_content},
            """
    
    # Close the combined API object
    combined_js += """
    };
    """
    
    return combined_js