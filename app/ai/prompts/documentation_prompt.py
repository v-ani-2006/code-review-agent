from app.ai.models import AIAnalysisContext


def build_documentation_prompt(context: AIAnalysisContext) -> str:
    """Build a prompt to generate comprehensive Google/Sphinx/PEP 257 docstrings and usage examples."""
    return f"""You are a Lead Technical Writer and Senior Python Architect.
Generate complete, professional, Google-style docstrings and usage examples for the following {context.language} code.

### SOURCE CODE METADATA
- Language: {context.language}
- Filename: {context.filename}

### SOURCE CODE TO DOCUMENT:
```{context.language}
{context.source_code}
```

### INSTRUCTIONS:
Ensure every module, class, method, and function has exhaustive docstrings with Args, Returns, Raises, and practical examples.
You MUST output your response in valid JSON format matching this schema:
{{
  "documented_code": "Complete source code containing all inserted docstrings and comments",
  "module_docstring": "High-level module docstring explaining package context and features",
  "class_docstrings": [
    {{"class_name": "ClassName", "docstring": "Detailed class docstring explaining attributes and purpose"}}
  ],
  "function_docstrings": [
    {{"function_name": "function_name", "docstring": "Detailed function docstring with Args, Returns, and Raises"}}
  ],
  "parameter_descriptions": [
    {{"parameter": "param_name", "type": "str / int / etc", "description": "Purpose and valid values"}}
  ],
  "usage_examples": [
    "```python\n# Example usage snippet\nresult = function_name(arg1, arg2)\n```"
  ]
}}

Output only the JSON block without markdown fences or outside commentary.
"""
