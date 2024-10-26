import re
import json
import pprint
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import requests
from html_examples import examples
import os
from dspy import  LM, configure, InputField, OutputField, Signature, TypedChainOfThought, ChainOfThought

load_dotenv()
os.environ.get("OPENAI_API_KEY")
lm = LM('openai/gpt-4o-mini', max_tokens=5000)
configure(lm=lm)

class ImageQuery(BaseModel):
    background_image_query: str
    related_image_query: str

class Images(BaseModel):
    instructions: str
    url: str

class ImageInstructions(BaseModel):
    image_instructions: List[Images]

class SectionInstruction(BaseModel):
    section_name: str
    instructions: str
    class_name: str
    style_instructions: str

class SectionInstructions(BaseModel):
    section_instructions: List[SectionInstruction]

class ClassifyImages(Signature):
    '''You are given a dictionary that contains image descriptions as keys and urls as values.
    You are also given a set of web site design instructions.
    Your job is to return a string that contains the image urls and instructions on where or how to use them in the web site.'''
    image_descriptions = InputField()
    design_instructions = InputField()
    image_instructions: ImageInstructions = OutputField(desc="A list of image objects that contain the instructions and urls")

class CreateInstructions(Signature):
    '''
        The user will provide a description of the website they want. Your task is to analyze this description and generate a clean, responsive HTML layout using Bootstrap 5 components. 
        Ensure the site has a visually appealing structure by following established design principles such as hierarchy, spacing, alignment, contrast, and consistency. 

        Here’s how to approach the design:
        1. Organize the Content Layout:
        Start by defining the sections needed based on the user's description. These might include a hero section, an about section, services, testimonials, contact, footer, and any other specific requirements the user has mentioned.
        Responsive Layouts: Ensure each section is responsive, adapting to different screen sizes using Bootstrap’s grid system (e.g., col-lg-6, col-md-4, etc.).
        
        2. Use Visual Hierarchy and Contrast:
        Establish clear section headings, subheadings, and body text. Use h1, h2, h3, and paragraph tags, and style them with Bootstrap's utility classes (e.g., .text-primary, .text-muted) to create visual contrast.
        3. Bootstrap Components Selection:
        Choose components that align with the website’s purpose. Here are a few examples based on section type:

        Hero Section: Use a jumbotron or a centered Card component with a large image or background video. Add a title, subtitle, and Button components for calls-to-action.
        About Section: Use Card components or Accordion to display the company's history, mission, or services. Style with a slight box-shadow (e.g., shadow-sm or shadow-lg) for a polished look.
        Services Section: Create Cards within a grid layout. Use icons or small images in the cards, Badges for highlights, and Tooltips for additional information on hover.
        Testimonials Section: Use a Carousel component or Card group to rotate client testimonials. Style each card with soft shadows and use muted backgrounds to make it visually appealing.
        Contact Section: Utilize Form components for a contact form, and include Alerts for error/success messages. Ensure each form field has form-control for styling consistency.
        Footer: Structure the footer with columns for links, social media icons, and contact information. Use List group or Nav classes to organize links.
        
        4. Add Subtle Enhancements for a Polished Look:
        Drop Shadows: Use Bootstrap’s built-in shadow classes (shadow-sm, shadow, shadow-lg) on Cards, Buttons, and images to give a soft, professional look.
        Rounded Corners: Add a subtle border-radius (rounded, rounded-circle for avatars) to buttons, images, and cards to soften the visual impact.
        Hover Effects: Utilize hover states for interactive elements. For example, :hover effects on buttons can include slight darkening (btn-outline-*) or shadow increase (shadow-lg).
        Spacing: Use Bootstrap’s spacing utilities (mb-4, mt-3, py-2, etc.) to ensure consistent padding and margins across elements, enhancing readability and visual flow.

        5. Bootstrap Components and Utilities:
        Below are some Bootstrap 5 components to consider based on the section and function:

        Call-to-Action Buttons: Use Button with .btn-primary for primary actions and .btn-outline-secondary for secondary actions.
        Icons: Integrate Font Awesome icons for enhanced visual appeal and functionality.
        Loading Elements: Spinner components for loading states and Progress bars for file uploads or process indicators.
        Additional Interactions: Add Modal windows for pop-up messages, Toast for notifications, and Tooltip for extra details.
        6. Images and Media:
        Image Selection: Use high-quality images that align with the user’s brand or purpose. Images should be responsive (img-fluid) and optionally styled with borders (border) or rounded edges (rounded).
        Responsive Embeds: For videos or iframes, use Bootstrap’s ratio classes (e.g., ratio-16x9) to maintain a responsive aspect ratio.
    '''
    description = InputField(desc='The user\'s description of the website')
    image_query: ImageQuery = OutputField(desc='1-3 word key phrase used to search images.')
    website_title = OutputField(desc='The title of the website')
    instructions_list: SectionInstructions = OutputField(desc='A list of verbose section instructions that contain the section name, instructions, and class name')
    color_scheme = OutputField(desc='A guide to the color scheme for the website')

class CSSRules(Signature):
    '''Create a CSS color scheme based on the user's description.'''

    section_instructions = InputField()
    color_scheme = InputField()
    css_rules = OutputField(desc='The CSS color scheme and rules for the website contained within <style> tags')

class HTMLBody(Signature):
    '''
        Please create the <section> of a website using Bootstrap 5 elements and classes, based on the user's instructions. 
        Generate meaningful and relevant text based on the user's description to use in the page.

        - Ensure you are using modern Bootstrap elements and classes for the layout.
        - The output should contain meaningful content that corresponds to the user's description.
    '''
    description = InputField(desc='The user\'s description of the website')
    class_name = InputField(desc='The class name for the section')
    html = OutputField(desc='The HTML code for the given section')

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

def clean_html(html):
    clean_text = re.sub(r'```html|```', '', html)
    return clean_text

def promptify(prompt):
    # Create instructions
    create_instructions = TypedChainOfThought(CreateInstructions)
    instructions_response = create_instructions(description=prompt)
    website_instructions = instructions_response.instructions_list
    style_instructions = instructions_response.color_scheme
    website_dict = website_instructions.model_dump()
    section_instructions = website_dict['section_instructions']
    pprint.pprint(section_instructions)
    section_instructions_str = json.dumps(section_instructions)
    
    css_rules = ChainOfThought(CSSRules)
    css_rules_response = css_rules(section_instructions=section_instructions_str, color_scheme=style_instructions)
    css_style_element = css_rules_response.css_rules

    website_title = instructions_response.website_title
    image_query = instructions_response.image_query
    image_query_dict = image_query.model_dump()
    background_image_query = image_query_dict['background_image_query']
    related_image_query = image_query_dict['related_image_query']
    
    # # Get images
    # image_results = query_unsplash(image_query)
    # image_dict = extract_image_data(image_results)
    # image_dict_str = json.dumps(image_dict)
    # classify_images = ChainOfThought(ClassifyImages)
    # classify_imgs_response = classify_images(image_descriptions=image_dict_str, design_instructions=website_instructions)
    # image_instructions = classify_imgs_response.image_instructions
    # image_instructions_json = json.dumps(image_instructions.model_dump())
    
    # Create HTML scaffold
    html_scaffold = examples['scaffold']
    current_html = html_scaffold.format(website_title=website_title, css_style_element=css_style_element, body='')
    
    # Build and insert each section progressively
    for section in section_instructions:
        section_html = TypedChainOfThought(HTMLBody)
        section_html_response = section_html(css_rules=style_instructions, description=section['instructions'], class_name=section['class_name'])
        clean_section = clean_html(section_html_response.html)
        
        # Find the closing body tag and insert the new section before it
        body_end_pos = current_html.find('</body>')
        current_html = current_html[:body_end_pos] + clean_section + current_html[body_end_pos:]

        yield current_html