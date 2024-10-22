from dotenv import load_dotenv
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

class HTML_Outline(Signature):
    '''
        Given a set of CSS rules and a users description create a website in HTML using the Bootstrap framework
        For the <script>'s, use this Bootstrap script: <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ENjdO4Dr2bkBIFxQpeoTz1HIcje39Wm4jDKdf19U8gI4ddQ3GYNS7NTKfAdVQSZe" crossorigin="anonymous"></script>
        For the <link>'s, use these Bootstrap CDN links: <linkhref="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"rel="stylesheet"/>, <linkhref="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css"rel="stylesheet"integrity="sha384-KK94CHFLLe+nY2dmCWGMq91rCGa5gtU4mk92HdvYe+M/SXH301p5ILy+dN9+nJOZ"crossorigin="anonymous"/>
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