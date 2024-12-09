from dspy import InputField, OutputField, Signature
from typing import List, Dict, Literal

class PageBuilderSignatures:
    class ComplexityAnalyzer(Signature):
        """Simple examples: Forms, Tables, Cards, individual components, etc.
        Complex examples: Landing Pages, entire Apps, Dashboards, multiple components etc."""
        description = InputField(desc="User prompt")
        complexity_level = OutputField(desc="simple or complex")
    class WebComponentArchitect(Signature):
        """Design a modern, responsive web component using Tailwind's component classes.
        Focus on:
        - Using Tailwind's preset component classes (like btn, card, etc.)
        - Vanilla JavaScript for interactivity
        - Responsive design patterns
        """ 
        description = InputField(desc='The user\'s requirements')
        global_css = OutputField(desc='CSS and Animations should be simple and elegant')
        component_spec: Dict[Literal[
            'component_name',
            "layout_structure",
            "image_requirements",
            "css_style_and_animation_instructions",
            "javascript_instructions"
        ], str] = OutputField(desc='CSS and Animations should be simple and elegant')
    class WebAppArchitect(Signature):
        """Design a modern, responsive web app UI using Tailwind's component classes.
        Focus on:
        - Using Tailwind's preset component classes (like btn, card, etc.)
        - Vanilla JavaScript for interactivity
        - Responsive design patterns"""
        description = InputField(desc='The user\'s requirements')
        sections: List[Dict[Literal[
            "section_name",
            "layout_structure",
            "image_requirements",
            "css_style_and_animation_instructions",
            "javascript_instructions"
        ], str]] = OutputField(desc='CSS and Animations should be simple and elegant') 
        global_css = OutputField(desc='CSS and Animations should be simple and elegant')
    class InteractionLogic(Signature):
        """Define interactive behaviors with awareness of component-wide context"""
        javascript_instructions = InputField()
        needs_javascript: bool = OutputField(desc='Whether the section needs JavaScript')
        javascript = OutputField(desc='Non-style related JavaScript functionality')
        need_state_management: bool = OutputField(desc='Whether the section needs state management')
        need_event_delegation: bool = OutputField(desc='Whether the section needs event delegation')
        state_management = OutputField(desc='JS code for Data and state handling logic')
        event_delegation = OutputField(desc='JS code for event handling')
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
        """Create semantic HTML5 markup with Tailwind component classes.
        Include:
        - Semantic HTML5 elements with Tailwind classes
        - Data attributes for JavaScript interactions
        - Clean, readable markup structure
        - Use Font Awesome version 6 Icons"""
        layout_structure = InputField()
        section_css_rules = InputField()
        section_javascript = InputField()
        image_details = InputField(desc='use the image paths provided, use all of the images in your response')
        markup = OutputField(desc='Response should contain HTML with Tailwind classes')
