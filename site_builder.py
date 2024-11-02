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
    'sonnet': {'model': 'anthropic/claude-3-5-sonnet-latest', 'max_tokens': 8192},
    'haiku': {'model': 'anthropic/claude-3-haiku-20240307', 'max_tokens': 4096},
    'opus': {'model': 'anthropic/claude-3-opus-latest', 'max_tokens': 4096},
    '4o-mini': {'model': 'openai/gpt-4o-mini', 'max_tokens': 4096},
    '4o': {'model': 'openai/gpt-4o', 'max_tokens': 4096},
}
lm = LM(model_dict['haiku']['model'], max_tokens=model_dict['haiku']['max_tokens'])
strong_lm = LM(model_dict['sonnet']['model'], max_tokens=model_dict['sonnet']['max_tokens'])
configure(lm=lm)

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
    try:
        api_key = os.environ.get('UNSPLASH_ACCESS_KEY')
        if not api_key:
            raise ValueError("Unsplash API key not found in environment variables")

        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {api_key}"}
        params = {
            "query": query,
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()  # Raises HTTPError for bad status codes
        
        return response.json()
        
    except requests.Timeout:
        raise Exception("Timeout while connecting to Unsplash API")
    except requests.RequestException as e:
        raise Exception(f"Error fetching images from Unsplash: {str(e)}")

def extract_image_data(response):
    try:
        if not response or not isinstance(response, dict):
            raise ValueError("Invalid response format")

        results = response.get('results', [])
        if not results:
            raise ValueError("No images found in response")

        image_dict = {}
        for result in results:
            description = result.get('alt_description')
            url = result.get('urls', {}).get('full')

            if description and url:
                image_dict[description] = url
        
        if not image_dict:
            raise ValueError("No valid images found in response")
            
        return image_dict
        
    except (AttributeError, TypeError) as e:
        raise ValueError(f"Error processing image data: {str(e)}")

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

def generate_initial_instructions(prompt):
    """Generate website instructions and initial setup"""
    try:
        with context(lm=strong_lm):
            create_instructions = TypedChainOfThought(CreateInstructions)
            instructions_response = create_instructions(description=prompt)

        return {
            'website_instructions': instructions_response.instructions_list,
            'style_instructions': instructions_response.color_scheme,
            'website_title': instructions_response.website_title,
            'image_query': instructions_response.image_query,
            'need_nav': instructions_response.need_nav.need_nav,
            'section_instructions': instructions_response.instructions_list.model_dump()['section_instructions']
        }
    except Exception as e:
        raise Exception(f"Error generating instructions: {str(e)}")

def generate_css(section_instructions_str, style_instructions):
    """Generate CSS styling for the website"""
    try:
        css_rules = ChainOfThought(CSSRules)
        css_rules_response = css_rules(
            section_instructions=section_instructions_str, 
            color_scheme=style_instructions
        )
        return css_rules_response.css_rules
    except Exception as e:
        raise Exception(f"Error generating CSS: {str(e)}")

def process_images(theme_related_image_query, section_instructions):
    """Handle image fetching and classification"""
    try:
        theme_related_image_results = query_unsplash(theme_related_image_query)
        theme_related_image_dict = extract_image_data(theme_related_image_results)
        theme_related_image_dict_str = json.dumps(theme_related_image_dict)
        
        classify_images = TypedChainOfThought(ClassifyImages)
        section_names_str = json.dumps([section['section_name'] for section in section_instructions])
        classify_imgs_response = classify_images(
            image_descriptions=theme_related_image_dict_str, 
            section_names=section_names_str
        )
        
        return {
            'image_dict': theme_related_image_dict,
            'image_lookup': {
                img.section_name: img.urls 
                for img in classify_imgs_response.image_instructions.image_instructions
            }
        }
    except Exception as e:
        raise Exception(f"Error processing images: {str(e)}")

def add_navigation(section_instructions_str):
    """Add navigation menu if needed"""
    try:
        nav_instructions = TypedChainOfThought(NavInstuctions)
        nav_response = nav_instructions(section_instructions=section_instructions_str)
        return nav_response.updated_instructions.model_dump()['section_instructions']
    except Exception as e:
        raise Exception(f"Error adding navigation: {str(e)}")

def build_section(section, style_instructions, image_lookup):
    """Build individual HTML section"""
    try:
        with context(lm=strong_lm):
            section_html = TypedChainOfThought(HTMLElement)
            section_html_response = section_html(
            css_rules=style_instructions,
            description=section['instructions'],
            class_name=section['class_name'],
            images=','.join(image_lookup.get(section['section_name'], 'None'))
            )
        return clean_html(section_html_response.html)
    except Exception as e:
        raise Exception(f"Error building section {section['section_name']}: {str(e)}")

def page_builder_pipeline(prompt):
    def format_sse(data):
        return f"data: {json.dumps(data)}\n\n"
    # 1. Initial Setup & Instructions Generation
    try:
        yield format_sse({"type": "progress", "message": "📝 Generating website instructions..."})
        instruction_data = generate_initial_instructions(prompt)
        
        yield format_sse({
            "type": "progress",
            "message": f"🏷️ Website Title: {instruction_data['website_title']}"
        })
    except Exception as e:
        yield format_sse({"type": "error", "message": str(e)})
        return

    # 2. CSS Generation
    try:
        yield format_sse({"type": "progress", "message": "🎨 Generating CSS styling..."})
        css_style_element = generate_css(
            json.dumps(instruction_data['section_instructions']), 
            instruction_data['style_instructions']
        )
        current_html = HTML_SCAFFOLD.format(
            website_title=instruction_data['website_title'], 
            css_style_element=css_style_element
        )
    except Exception as e:
        yield format_sse({"type": "error", "message": str(e)})
        return

    # 3. Image Processing
    image_lookup = {}
    try:
        yield format_sse({
            "type": "progress",
            "message": f"🔍 Searching for images..."
        })
        
        image_data = process_images(
            instruction_data['image_query'].model_dump()['theme_related_image'],
            instruction_data['section_instructions']
        )
        image_lookup = image_data['image_lookup']

        # Preview images
        preview_images = list(image_data['image_dict'].items())[:4]
        yield format_sse({
            "type": "progress",
            "message": f"📸 Found {len(image_data['image_dict'])} images. Here are some examples:"
        })
        for desc, url in preview_images:
            yield format_sse({
                "type": "image",
                "url": url,
                "description": desc
            })
    except Exception as e:
        yield format_sse({"type": "error", "message": str(e)})
        # Continue without images

    # 4. Navigation Addition
    section_instructions = instruction_data['section_instructions']
    if instruction_data['need_nav']:
        try:
            yield format_sse({"type": "progress", "message": "🧭 Adding navigation menu..."})
            section_instructions = add_navigation(json.dumps(section_instructions))
        except Exception as e:
            yield format_sse({"type": "error", "message": str(e)})

    # 5. Section Building
    try:
        yield format_sse({
            "type": "progress",
            "message": f"🏗️ Building {len(section_instructions)} sections..."
        })

        for i, section in enumerate(section_instructions, 1):
            try:
                yield format_sse({
                    "type": "progress",
                    "message": f"📄 Creating section {i}/{len(section_instructions)}: {section['section_name']}"
                })
                
                clean_section = build_section(
                    section, 
                    instruction_data['style_instructions'], 
                    image_lookup
                )
                
                body_end_pos = current_html.find('</body>')
                current_html = current_html[:body_end_pos] + clean_section + current_html[body_end_pos:]

                yield format_sse({
                    "type": "html",
                    "content": current_html
                })
            except Exception as e:
                yield format_sse({"type": "error", "message": str(e)})
                continue
    except Exception as e:
        yield format_sse({"type": "error", "message": str(e)})