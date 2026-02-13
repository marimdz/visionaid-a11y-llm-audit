#!/usr/bin/env python3
"""
Generate accessibility testing prompts from modular components.

This script combines different prompt elements to create variations for testing:
- Task instructions (how to frame the task)
- WCAG guidelines (how much context to provide)
- Report formatting (output structure requirements)

Usage:
    python generate_prompt.py --task simple --wcag zero_shot --format csv_report_minimum
    python generate_prompt.py --task detailed --wcag principle --format csv_report_minimum
    python generate_prompt.py --list  # Show all available options
    python generate_prompt.py --all   # Generate all combinations
"""

import argparse
import sys
import os
from pathlib import Path

# Add prompts directory to path
SCRIPT_DIR = Path(__file__).parent
PROMPTS_DIR = SCRIPT_DIR.parent / "prompts"
sys.path.insert(0, str(PROMPTS_DIR))

# Import all prompt components
from task_instructions import (
    simple_instruction,
    detailed_instruction,
    step_by_step_instruction,
    cot_instruction,
    persona_instruction,
    minimal_instruction
)

from guideline_variations import (
    zero_shot_wcag,
    principle_wcag,
    full_wcag
)

from report_formatting import (
    csv_report_minimum
)

# Map names to variables for easy access
TASK_INSTRUCTIONS = {
    "simple": simple_instruction,
    "detailed": detailed_instruction,
    "step_by_step": step_by_step_instruction,
    "cot": cot_instruction,
    "persona": persona_instruction,
    "minimal": minimal_instruction
}

WCAG_GUIDELINES = {
    "zero_shot": zero_shot_wcag,
    "principle": principle_wcag,
    "full": full_wcag
}

REPORT_FORMATS = {
    "csv_report_minimum": csv_report_minimum
}


def build_prompt(task_key, wcag_key, format_key, html_placeholder="{{HTML_CONTENT}}"):
    """
    Build a complete prompt from component keys.
    
    Args:
        task_key: Key for task instruction variant
        wcag_key: Key for WCAG guideline variant
        format_key: Key for report format variant
        html_placeholder: Placeholder text for where HTML will be inserted
        
    Returns:
        Complete prompt string
    """
    task = TASK_INSTRUCTIONS[task_key]
    wcag = WCAG_GUIDELINES[wcag_key]
    format_spec = REPORT_FORMATS[format_key]
    
    # Build prompt sections
    sections = []
    
    # Add task instruction
    sections.append(task)
    
    # Add WCAG guidelines if not zero-shot
    if wcag:
        sections.append("\n---\n")
        sections.append(wcag)
    
    # Add format specification
    sections.append("\n---\n")
    sections.append(format_spec)
    
    # Add HTML content placeholder
    sections.append("\n---\n")
    sections.append(f"HTML to analyze:\n\n{html_placeholder}")
    
    return "\n".join(sections)


def get_prompt_name(task_key, wcag_key, format_key):
    """Generate a descriptive filename for a prompt combination."""
    return f"{task_key}_{wcag_key}_{format_key}.txt"


def list_options():
    """Print all available prompt component options."""
    print("Available Prompt Components:")
    print("\nTask Instructions:")
    for key in TASK_INSTRUCTIONS.keys():
        print(f"  - {key}")
    
    print("\nWCAG Guideline Levels:")
    for key in WCAG_GUIDELINES.keys():
        print(f"  - {key}")
    
    print("\nReport Formats:")
    for key in REPORT_FORMATS.keys():
        print(f"  - {key}")


def generate_all_combinations(output_dir=None):
    """Generate all possible prompt combinations and optionally save to files."""
    combinations = []
    
    for task_key in TASK_INSTRUCTIONS.keys():
        for wcag_key in WCAG_GUIDELINES.keys():
            for format_key in REPORT_FORMATS.keys():
                prompt = build_prompt(task_key, wcag_key, format_key)
                name = get_prompt_name(task_key, wcag_key, format_key)
                combinations.append((name, prompt))
                
                if output_dir:
                    output_path = Path(output_dir) / name
                    output_path.write_text(prompt)
                    print(f"Generated: {output_path}")
    
    return combinations


def main():
    parser = argparse.ArgumentParser(
        description="Generate accessibility testing prompts from modular components"
    )
    
    parser.add_argument(
        "--task",
        choices=list(TASK_INSTRUCTIONS.keys()),
        help="Task instruction variant to use"
    )
    
    parser.add_argument(
        "--wcag",
        choices=list(WCAG_GUIDELINES.keys()),
        help="WCAG guideline level to include"
    )
    
    parser.add_argument(
        "--format",
        choices=list(REPORT_FORMATS.keys()),
        help="Report format specification to use"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available component options"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all possible combinations"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save generated prompts (use with --all)"
    )
    
    parser.add_argument(
        "--html",
        type=str,
        default="{{HTML_CONTENT}}",
        help="HTML content or placeholder (default: {{HTML_CONTENT}})"
    )
    
    parser.add_argument(
        "--save",
        type=str,
        help="Save generated prompt to this file path"
    )
    
    args = parser.parse_args()
    
    # Handle list command
    if args.list:
        list_options()
        return
    
    # Handle generate all combinations
    if args.all:
        output_dir = args.output_dir or "generated_prompts"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        generate_all_combinations(output_dir)
        print(f"\nGenerated {len(TASK_INSTRUCTIONS) * len(WCAG_GUIDELINES) * len(REPORT_FORMATS)} prompt combinations")
        return
    
    # Validate that all required arguments are present for single prompt generation
    if not (args.task and args.wcag and args.format):
        parser.error("Must specify --task, --wcag, and --format (or use --list or --all)")
    
    # Generate single prompt
    prompt = build_prompt(args.task, args.wcag, args.format, args.html)
    
    # Output prompt
    if args.save:
        Path(args.save).write_text(prompt)
        print(f"Prompt saved to: {args.save}")
    else:
        print(prompt)


if __name__ == "__main__":
    main()