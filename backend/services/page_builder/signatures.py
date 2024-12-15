from dspy import InputField, OutputField, Signature
from typing import List, Dict, Literal

class PageBuilderSignatures:
    class ComplexityAnalyzer(Signature):
        """Simple examples: Forms, Tables, Cards, individual components, etc.
        Complex examples: Landing Pages, entire Apps, Dashboards, multiple components etc."""
        description = InputField(desc="User prompt")
        complexity_level = OutputField(desc="simple or complex")
    class WebComponentArchitect(Signature):
        """Design a modern, responsive web component using Bootstrap 5 components and classes.
        Focus on:
        - Using Bootstrap's preset component classes (like btn, card, etc.)
        - Responsive design patterns""" 
        description = InputField(desc='The user\'s requirements')
        global_css = OutputField(desc='CSS and Animations should be simple and elegant')
        component_spec: Dict[Literal[
            'component_name',
            "layout_structure",
            "image_requirements",
            "css_style_and_animation_instructions",
        ], str] = OutputField(desc='CSS and Animations should be simple and elegant')
    class WebAppArchitect(Signature):
        """Design a modern, responsive web app UI using Bootstrap 5 components and classes.
        Focus on:
        - Using Bootstrap's preset component classes (like btn, card, etc.)
        - Responsive design patterns"""
        description = InputField(desc='The user\'s requirements')
        sections: List[Dict[Literal[
            "section_name",
            "layout_structure",
            "image_requirements",
            "css_style_and_animation_instructions",
        ], str]] = OutputField(desc='CSS and Animations should be simple and elegant. image_requirements should contain how many images are needed') 
        global_css = OutputField(desc='CSS and Animations should be simple and elegant')
    class SectionImageDetails(Signature):
        """Create image details that will be used to generate images"""
        image_instructions = InputField()
        image_details: List[Dict[Literal[
            "image_name",
            "alt",
            "prompt",
        ], str]] = OutputField(desc='prompt should be detailed and verbose, avoid Icons') 
    class SectionStyle(Signature):
        """Define section styles with awareness of global context"""
        style_instructions = InputField()
        global_css = InputField()
        css_rules = OutputField()
        transitions = OutputField(desc='CSS transitions and keyframe animations')
    class ComponentStructure(Signature):
        """Create semantic HTML5 markup with Bootstrap 5 components and classes.
        Include:
        - Semantic HTML5 elements with Bootstrap classes
        - Clean, readable markup structure
        - Use Font Awesome version 6 Icons"""
        layout_structure = InputField()
        section_css_rules = InputField()
        image_details = InputField(desc='use the image paths provided, use all of the images in your response')
        markup = OutputField(desc='Response should contain HTML with Bootstrap components and classes')
