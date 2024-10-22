from dotenv import load_dotenv
from .html_examples import examples
import os
from dspy import ChainOfThought, LM, configure, InputField, OutputField, Signature

load_dotenv()
os.environ.get("OPENAI_API_KEY")
lm = LM('openai/gpt-4o', max_tokens=10000)
configure(lm=lm)

class CSS_Color_Scheme(Signature):
    '''Create a CSS color scheme based on the user's description'''

    description = InputField(desc='The user\'s description of the website')
    color_scheme = OutputField(desc='The CSS color scheme for the website contained within <style> tags')

class HTML_Scaffold(Signature):
    '''Create a basic HTML scaffold for the website'''
    description = InputField(desc='The user\'s description of the website')
    example = InputField(desc='An example of the website')
    scaffold = OutputField(desc='The HTML scaffold for the website')

class HTML_Navbar(Signature):
    '''Based on the user's description, generate the HTML for a responsive Bootstrap navigation element. 
    Please provide the HTML code in the following format: <nav></nav>'''
    description = InputField(desc='The user\'s description of the website')
    example = InputField(desc='An example Navbar element')
    navbar = OutputField(desc='The HTML code for the navbar')

class HTML_Body(Signature):
    '''
        Please create the body of a website using Bootstrap 5 elements and classes, based on the user's description. 
        Generate meaningful and relevant text based on the user's description to use in the page.

        Ensure you are using modern Bootstrap elements and classes for the layout.
        
        Use the following image source, replacing "portrait" with a keyword related to the user's description:
        <img src="https://source.unsplash.com/900x600/?portrait">

        Wrap your response with <body></body> tags.
        The output should contain meaningful content that corresponds to the user's description.
    '''

    css_rules = InputField(desc='The CSS color scheme for the website contained within <style> tags')
    description = InputField(desc='The user\'s description of the website')
    html = OutputField(desc='The HTML code for the website')

def promptify(prompt):
    color_scheme = ChainOfThought(CSS_Color_Scheme)
    css_rules = color_scheme(description=prompt)
    print(css_rules.color_scheme)
    html_outline = ChainOfThought(HTML_Outline)
    html = html_outline(css_rules=css_rules.color_scheme, description=prompt)
    print(html.html)
    return(html.html)