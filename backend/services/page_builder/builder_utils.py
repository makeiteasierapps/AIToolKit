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
    <!-- Bootstrap CSS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    
    <!-- Additional Resource Loading -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Component Styles -->
    {component_styles} 
</head>
<body>
    <!-- Component Container -->
    <div id="component-root">
        {component_markup}
    </div>  
</body>
</html>
'''


def format_sse(data):
    return f"data: {json.dumps(data)}\n\n"

def create_component_scaffold(styles: str, markup: List[str]) -> str:
    cleaned_styles = clean_markup(styles)
    cleaned_markup = [clean_markup(section) for section in markup]
    
    return COMPONENT_SCAFFOLD.format(
        component_title="",
        component_styles=cleaned_styles,
        component_markup="\n".join(cleaned_markup),
        script_imports="",
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
