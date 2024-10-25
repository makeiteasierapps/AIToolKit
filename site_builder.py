import re
import json
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import requests
from html_examples import examples
import os
from dspy import ChainOfThought, LM, configure, InputField, OutputField, Signature

load_dotenv()
os.environ.get("OPENAI_API_KEY")
lm = LM('openai/gpt-4o-mini', max_tokens=5000)
configure(lm=lm)

class Images(BaseModel):
    instructions: str
    url: str

class ImageInstructions(BaseModel):
    image_instructions: List[Images]

class ClassifyImages(Signature):
    '''You are given a dictionary that contains image descriptions as keys and urls as values.
    You are also given a set of web site design instructions.
    Your job is to return a string that contains the image urls and instructions on where or how to use them in the web site.'''
    image_descriptions = InputField()
    design_instructions = InputField()
    image_instructions: ImageInstructions = OutputField(desc="A list of image objects that contain the instructions and urls")

class CreateInstructions(Signature):
    '''
        The user is giving you what they want for a website. Your job is to take their description and organize it into a set of instructions.
        If they don't provide a lot of detail then please expand on what they want. Here is a list of Bootstrap 5 components that you can use:
        Accordion
        Alerts
        Badge
        Breadcrumb
        Buttons
        Button group
        Card
        Carousel
        Close button
        Collapse
        Dropdowns
        List group
        Modal
        Navbar
        Navs & tabs
        Offcanvas
        Pagination
        Placeholders
        Popovers
        Progress
        Scrollspy
        Spinners
        Toasts
        Tooltips
        Use the image query to find images to be used in the website design.
    '''
    description = InputField(desc='The user\'s description of the website')
    image_query = OutputField(desc='1-3 word key phrase used to search for images to be used in the website design.')
    website_title = OutputField(desc='The title of the website')
    instructions_list = OutputField()

class CSSColorScheme(Signature):
    '''Create a CSS color scheme based on the user's description.'''

    description = InputField(desc='The user\'s description of the website')
    color_scheme = OutputField(desc='The CSS color scheme for the website contained within <style> tags')

class HTMLNavbar(Signature):
    '''Based on the user's description, generate the HTML for a responsive Bootstrap navigation element. 
    Please provide the HTML code in the following format: <nav></nav>'''
    description = InputField(desc='The user\'s description of the website')

    navbar = OutputField(desc='The HTML code for the navbar')

class HTMLBody(Signature):
    '''
        Please create the <body> section of a website using Bootstrap 5 elements and classes, based on the user's instructions. 
        Generate meaningful and relevant text based on the user's description to use in the page.

        Ensure you are using modern Bootstrap elements and classes for the layout.
        
        If you include images only use the ones provided in the design instructions.
        Include the following bootstrap cdn in the <body>:     
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

        Wrap your response with <body></body> tags.
        The output should contain meaningful content that corresponds to the user's description.
    '''

    css_rules = InputField(desc='The CSS color scheme for the website contained within <style> tags')
    description = InputField(desc='The user\'s description of the website')
    html = OutputField(desc='The HTML code for the website')

def query_unsplash(query, per_page=10, page=1):
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

def replace_keys_with_values(image_instructions, image_dict):
    print('Image Instructions: ', image_instructions)
    # Iterate over the dictionary and replace each description (key) with its corresponding URL (value)
    for title, url in image_dict.items():
        print('Title: ', title)
        if title in image_instructions:
            print('Title: ', title)
            image_instructions = image_instructions.replace(title, url)
    return image_instructions

def clean_html(html):
    clean_text = re.sub(r'```html|```', '', html)
    return clean_text

def promptify(prompt):
    # Create instructions
    create_instructions = ChainOfThought(CreateInstructions)
    instructions_response = create_instructions(description=prompt)
    website_instructions = instructions_response.instructions_list
    website_title = instructions_response.website_title
    image_query = instructions_response.image_query
    
    # Get images
    image_results = query_unsplash(image_query)
    image_dict = extract_image_data(image_results)
    image_dict_str = json.dumps(image_dict)
    classify_images = ChainOfThought(ClassifyImages)
    classify_imgs_response = classify_images(image_descriptions=image_dict_str, design_instructions=website_instructions)
    image_instructions = classify_imgs_response.image_instructions
    image_instructions_json = json.dumps(image_instructions.model_dump())
    print('Image Instructions', image_instructions_json)
    final_instructions = website_instructions + '\nImage Instructions: \n' + image_instructions_json
    print('Final Instructions: ', final_instructions)

    # Create CSS color scheme
    color_scheme = ChainOfThought(CSSColorScheme)
    css_rules = color_scheme(description=final_instructions)

    # Create HTML scaffold
    html_scaffold = examples['scaffold']
    scaffold = html_scaffold.format(website_title=website_title)

    # Create HTML navbar
    html_navbar = ChainOfThought(HTMLNavbar)
    navbar = html_navbar(description=final_instructions)
    html_body = ChainOfThought(HTMLBody)
    body = html_body(css_rules=css_rules.color_scheme, description=final_instructions)

    # Remove any nav elements from the body content
    body_content = re.sub(r'<nav\b[^>]*>.*?</nav>', '', body.html, flags=re.DOTALL)

    # Find or create head section
    head_start = scaffold.find('<head>')
    head_end = scaffold.find('</head>')
    
    if head_start == -1 or head_end == -1:
        # If no head tags exist, create them after html tag
        html_tag_end = scaffold.find('>') + 1
        scaffold = scaffold[:html_tag_end] + '\n<head>\n</head>' + scaffold[html_tag_end:]
        head_start = scaffold.find('<head>')
        head_end = scaffold.find('</head>')
    
    # Insert CSS rules into head
    head_content_insert = head_start + len('<head>')
    scaffold = (
        scaffold[:head_content_insert] +
        f'\n{css_rules.color_scheme}\n' +
        scaffold[head_content_insert:]
    )
    
    # Find or create body section
    body_tag_pos = scaffold.find('</head>') + len('</head>')
    final_html = (
        scaffold[:body_tag_pos] +
        '\n<body>\n' +
        f'{navbar.navbar}\n' +
        f'{body_content}\n' +
        '</body>\n' +
        scaffold[body_tag_pos:]
    )
    final_html = clean_html(final_html)
    return final_html
