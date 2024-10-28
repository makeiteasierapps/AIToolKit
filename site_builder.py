import re
from typing import List
import json
import os
from dspy import  LM, configure, InputField, OutputField, Signature, TypedChainOfThought, ChainOfThought, context
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
HTML_SCAFFOLD = '''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{website_title}</title>
        {css_style_element}
        <!-- Bootstrap CSS & JS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        
        <!-- Font Awesome CSS -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    </body>
    </html>'''

load_dotenv()
os.environ.get("OPENAI_API_KEY")
os.environ.get("ANTHROPIC_API_KEY")
model_dict = {
    'sonnet': 'anthropic/claude-3-5-sonnet-latest',
    'haiku': 'anthropic/claude-3-haiku-20240307',
    'opus': 'anthropic/claude-3-opus-latest',
    '4o-mini': 'openai/gpt-4o-mini',
    '4o': 'openai/gpt-4o',
}
lm = LM(model_dict['haiku'], max_tokens=4096)
configure(lm=lm)
strong_lm = LM(model_dict['4o-mini'], max_tokens=4096)

class Nav(BaseModel):
    need_nav: bool

class ImageQuery(BaseModel):
    design_related_image: str
    theme_related_image: str

class Images(BaseModel):
    section_name: str
    urls: List[str]

class ImageInstructions(BaseModel):
    image_instructions: List[Images]

class SectionInstruction(BaseModel):
    section_name: str
    instructions: str
    class_name: str

class SectionInstructions(BaseModel):
    section_instructions: List[SectionInstruction]

class ClassifyImages(Signature):
    '''You are given a dictionary that contains image descriptions as keys and urls as values.
    You are also given a section names of a website, ie. hero, about, services, etc.
    '''
    image_descriptions = InputField()
    section_names = InputField()
    image_instructions: ImageInstructions = OutputField(desc="A list of images that contain the section name, and urls for 3-4 images")

class CreateInstructions(Signature):
    '''Analyze the website description and generate a clean, responsive HTML layout using Bootstrap 5 components.
    Focus on creating a logical structure that matches the website's purpose.

    Guidelines:
    1. Identify Core Components:
    - For content-heavy sites: Include hero, about, services, testimonials, contact sections as needed
    - For functional pages (login, signup, etc.): Focus on the primary component only
    - Add navigation if multiple sections are present
    
    2. Component Structure:
    - Each section should serve a distinct purpose
    - IMPORTANT: Never split single functional components (forms, pricing tables, etc.) into multiple sections
    - Use appropriate Bootstrap components (Cards, Forms, Carousel, etc.)
    
    3. Design Principles:
    - Ensure responsive layouts using Bootstrap's grid system
    - Maintain visual hierarchy with proper heading levels
    - Use consistent spacing and alignment
    - Apply appropriate shadows and borders for depth
    
    4. Component Examples:
    - Landing Page: Hero (with CTA) → About → Services → Contact
    - Login Page: Single form section with header and inputs
    - Product Page: Product showcase → Details → Related items
    
    Remember: Keep the structure as simple as possible while meeting all functional requirements.
    '''
    description = InputField(desc='The user\'s description of the website')
    image_query: ImageQuery = OutputField(desc='usually 1-3 words')
    website_title = OutputField(desc='The title of the website')
    need_nav: Nav = OutputField()
    instructions_list: SectionInstructions = OutputField()
    color_scheme = OutputField(desc='A guide to the color scheme for the website')

class CSSRules(Signature):
    '''Create a CSS color scheme based on the user's description.'''

    section_instructions = InputField()
    color_scheme = InputField()
    css_rules = OutputField(desc='The CSS color scheme and rules for the website contained within <style> tags')

class NavInstuctions(Signature):
    '''
    You are given JSON of section instructions. Please return the updated list with a navigation section added to the beginning.
    '''
    section_instructions = InputField(desc='The JSON of section instructions')
    updated_instructions: SectionInstructions = OutputField()

class HTMLElement(Signature):
    '''
        Please create the needed HTML element wrapping your response in the necessary tag, ie <nav> or <section>. 
        Use Bootstrap 5 elements and classes, based on the user's instructions. 
        Generate meaningful and relevant text based on the user's description to use in the page.

        - If you use images only use the urls provided.
        - Ensure you are using modern Bootstrap elements and classes for the layout.
        - The output should contain meaningful content that corresponds to the user's description.
    '''
    description = InputField(desc='The user\'s description of the website')
    class_name = InputField()
    images = InputField(desc='List of images or None')
    html = OutputField(desc='The HTML code for the given section')

def query_unsplash(query, per_page=30, page=1):
    url = "https://api.unsplash.com/search/photos"
    headers = {
        "Authorization": f"Client-ID {os.environ.get('UNSPLASH_ACCESS_KEY')}"
    }
    params = {
        "query": query,
        "per_page": per_page,
        "page": page
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=60)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def extract_image_data(response):
    image_dict = {}
    for result in response.get('results', []):
        description = result.get('alt_description')  # Ensure description is a string
        url = result.get('urls', {}).get('full')  # Handle case where 'urls' or 'full' could be missing

        if description and url:  # Only add if both description and url are not None
            image_dict[description] = url
        
    return image_dict

def clean_html(html):
    clean_text = re.sub(r'```html|```', '', html)
    return clean_text

def promptify(prompt):
    def format_sse(data):
        return f"data: {json.dumps(data)}\n\n"
    print(prompt)
    # Create HTML scaffold
    current_html = HTML_SCAFFOLD.format(website_title='', css_style_element='')
    yield current_html
    
    # Create instructions
    yield format_sse({
        "type": "progress",
        "message": "📝 Generating website instructions and design guidelines..."
    })
    with context(lm=strong_lm):    
        create_instructions = TypedChainOfThought(CreateInstructions)
        instructions_response = create_instructions(description=prompt)

    website_instructions = instructions_response.instructions_list
    style_instructions = instructions_response.color_scheme
    website_title = instructions_response.website_title
    yield format_sse({
        "type": "progress",
        "message": f"🏷️ Website Title: {website_title}"
    })
    image_query = instructions_response.image_query
    need_nav = instructions_response.need_nav.need_nav
    website_dict = website_instructions.model_dump()

    section_instructions = website_dict['section_instructions']
    section_instructions_str = json.dumps(section_instructions)
    
    yield format_sse({
        "type": "progress",
        "message": "🎨 Generating CSS styling..."
    })
    css_rules = ChainOfThought(CSSRules)
    css_rules_response = css_rules(section_instructions=section_instructions_str, color_scheme=style_instructions)
    css_style_element = css_rules_response.css_rules
    
    current_html = HTML_SCAFFOLD.format(website_title=website_title, css_style_element=css_style_element)
    
    image_query_dict = image_query.model_dump()
    theme_related_image_query = image_query_dict['theme_related_image']
    
    # Get images
    yield format_sse({
        "type": "progress",
        "message": f"🔍 Searching for images related to: {theme_related_image_query}"
    })
    theme_related_image_results = query_unsplash(theme_related_image_query)
    theme_related_image_dict = extract_image_data(theme_related_image_results)

    theme_related_image_dict_str = json.dumps(theme_related_image_dict)
    classify_images = TypedChainOfThought(ClassifyImages)
    section_names_str = json.dumps([section['section_name'] for section in section_instructions])
    classify_imgs_response = classify_images(image_descriptions=theme_related_image_dict_str, section_names=section_names_str)
    image_instructions = classify_imgs_response.image_instructions
    
    # Get image instructions as a dictionary for easier lookup
    image_lookup = {img.section_name: img.urls for img in image_instructions.image_instructions}
    
    # Preview some of the found images
    preview_images = list(theme_related_image_dict.items())[:3]  # Show first 3 images
    yield format_sse({
        "type": "progress",
        "message": f"📸 Found {len(theme_related_image_dict)} images. Here are some examples:"
    })
    for desc, url in preview_images:
        yield format_sse({
            "type": "image",
            "url": url,
            "description": desc
        })

    if need_nav:
        yield format_sse({
            "type": "progress",
            "message": "🧭 Adding navigation menu..."
        })
        nav_instructions = TypedChainOfThought(NavInstuctions)
        nav_instructions_response = nav_instructions(section_instructions=section_instructions_str)
        section_instructions = nav_instructions_response.updated_instructions.model_dump()['section_instructions']
    # Build and insert each section progressively
    
    yield format_sse({
        "type": "progress",
        "message": f"🏗️ Building {len(section_instructions)} sections..."
    })

    print(section_instructions)
    with context(lm=strong_lm):
        for i, section in enumerate(section_instructions, 1):
            yield format_sse({
                "type": "progress",
                "message": f"📄 Creating section {i}/{len(section_instructions)}: {section['section_name']}"
            })
            section_html = TypedChainOfThought(HTMLElement)
            section_html_response = section_html(css_rules=style_instructions, description=section['instructions'], class_name=section['class_name'], images=','.join(image_lookup.get(section['section_name'], 'None')))
            clean_section = clean_html(section_html_response.html)
            
            body_end_pos = current_html.find('</body>')
            current_html = current_html[:body_end_pos] + clean_section + current_html[body_end_pos:]

            yield format_sse({
                "type": "html",
                "content": current_html
            })