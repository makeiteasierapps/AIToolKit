from dotenv import load_dotenv
import re
from html_examples import examples
import os
from dspy import ChainOfThought, LM, configure, InputField, OutputField, Signature

load_dotenv()
os.environ.get("OPENAI_API_KEY")
lm = LM('openai/gpt-4o-mini', max_tokens=10000)
configure(lm=lm)

class CSSColorScheme(Signature):
    '''Create a CSS color scheme based on the user's description based on the example provided'''

    description = InputField(desc='The user\'s description of the website')
    example = InputField(desc='An example of what we want')
    color_scheme = OutputField(desc='The CSS color scheme for the website contained within <style> tags')

class HTMLScaffold(Signature):
    '''Create the HEAD and HTML tags for the website'''
    description = InputField(desc='The user\'s description of the website')
    example = InputField(desc='An example of what we want')
    scaffold = OutputField(desc='The HTML scaffold for the website')

class HTMLNavbar(Signature):
    '''Based on the user's description, generate the HTML for a responsive Bootstrap navigation element. 
    Please provide the HTML code in the following format: <nav></nav>'''
    description = InputField(desc='The user\'s description of the website')
    example = InputField(desc='An example Navbar element')
    navbar = OutputField(desc='The HTML code for the navbar')

class HTMLBody(Signature):
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
    color_scheme = ChainOfThought(CSSColorScheme)
    css_rules = color_scheme(description=prompt, example=examples['css'])
    html_scaffold = ChainOfThought(HTMLScaffold)
    scaffold = html_scaffold(description=prompt, example=examples['scaffold'])
    html_navbar = ChainOfThought(HTMLNavbar)
    navbar = html_navbar(description=prompt, example=examples['navbar'])
    html_body = ChainOfThought(HTMLBody)
    body = html_body(css_rules=css_rules.color_scheme, description=prompt)
    
    # Clean up scaffold by removing any existing style or body tags
    scaffold = scaffold.scaffold
    scaffold = re.sub(r'<style>.*?</style>', '', scaffold, flags=re.DOTALL)
    scaffold = re.sub(r'<body>.*?</body>', '', scaffold, flags=re.DOTALL)
    
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
    
    return final_html
