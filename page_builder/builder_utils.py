import json
import re
from typing import Dict, List

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


def format_sse(data):
    return f"data: {json.dumps(data)}\n\n"

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

