"""
Task instruction variations for accessibility testing prompts.
These define different ways to frame the core task of analyzing HTML for accessibility issues.
"""

# Baseline: Simple, direct instruction
simple_instruction = """Analyze the provided HTML content for accessibility issues and generate a report of all problems found."""

# Detailed: More specific about what to look for
detailed_instruction = """You are an accessibility testing expert. Analyze the provided HTML content for WCAG compliance issues.

Your task:
1. Review the HTML structure, semantics, and ARIA attributes
2. Identify accessibility violations including:
   - Missing or improper semantic markup
   - Insufficient alternative text for images
   - Form elements without proper labels
   - Keyboard navigation issues
   - Missing ARIA roles, states, or properties
   - Heading hierarchy problems
   - Missing language attributes
   - Table accessibility issues
   - Color contrast problems (if detectable from markup)
   - Any other WCAG violations

3. For each issue found, provide:
   - The specific element or location in the HTML
   - A clear description of the problem
   - The WCAG success criterion violated
   - Recommended fix

Generate a comprehensive accessibility report."""

# Step-by-step: Breaking down the analysis process
step_by_step_instruction = """Perform a comprehensive accessibility audit of the provided HTML by following these steps:

Step 1: Semantic Structure Analysis
- Check page title presence and quality
- Verify language attributes
- Examine landmark regions (header, nav, main, footer)
- Review heading hierarchy (h1-h6)
- Validate list structures

Step 2: Interactive Elements Review  
- Analyze form inputs for proper labels and associations
- Check button and link semantics
- Verify ARIA roles and attributes
- Examine keyboard accessibility patterns
- Review focus management

Step 3: Non-Text Content Evaluation
- Check images for alternative text
- Review SVG and icon accessibility
- Examine multimedia elements
- Validate canvas elements

Step 4: Navigation and Structure
- Verify skip links
- Check navigation consistency
- Review reading/tab order
- Examine iframe accessibility

Step 5: Report Generation
For each issue identified, document it in the report format specified."""

# Chain-of-thought: Encouraging explicit reasoning
cot_instruction = """You are conducting an accessibility audit. For the provided HTML:

First, scan through the entire HTML structure and identify the main components (navigation, forms, content sections, images, etc.).

Then, for each component type:
- Consider what accessibility requirements apply
- Check whether the HTML meets those requirements  
- If violations exist, determine the severity and impact
- Formulate specific, actionable recommendations

Think through each issue carefully:
- What is the exact problem?
- Which WCAG success criterion does it violate?
- How would this affect users with different disabilities?
- What is the correct implementation?

Generate a complete accessibility report with your findings."""

# Persona-based: Framing from user perspective
persona_instruction = """You are an accessibility consultant conducting a WCAG audit for a client's website.

The client needs to understand:
- What accessibility barriers exist in their HTML
- How these barriers affect real users (screen reader users, keyboard-only users, low vision users, etc.)
- Which WCAG success criteria are violated
- Exactly how to fix each issue

Analyze the provided HTML as you would for a professional accessibility audit. Be thorough, specific, and actionable in your findings. Focus on issues that have real impact on users with disabilities.

Provide a detailed report that the development team can use to remediate all accessibility issues."""

# Minimal: Bare minimum instruction (test if less is more)
minimal_instruction = """Identify all WCAG accessibility violations in the provided HTML and report them in the specified format."""