from app.ai.models import AIAnalysisContext


def build_explain_prompt(context: AIAnalysisContext) -> str:
    """Build a code explanation prompt targeting beginner understanding, execution flow, and structural walkthrough."""
    return f"""You are an expert Computer Science educator and senior software architect.
Explain the following {context.language} code clearly for both beginners and experienced developers.

### SOURCE CODE METADATA
- Language: {context.language}
- Filename: {context.filename}
- Cyclomatic Complexity: {context.cyclomatic_complexity if context.cyclomatic_complexity is not None else 'N/A'} (Rank: {context.complexity_rank})

### SOURCE CODE TO EXPLAIN:
```{context.language}
{context.source_code}
```

### INSTRUCTIONS:
Provide a comprehensive explanation.
You MUST output your response in valid JSON format matching this schema:
{{
  "beginner_explanation": "Simple, intuitive explanation of what the program accomplishes in plain English without jargon",
  "line_by_line_summary": [
    {{"lines": "1-5", "explanation": "Importing required modules and configuring environment"}},
    ...
  ],
  "execution_flow": [
    "Step 1: Application starts and initializes ...",
    "Step 2: ...",
    ...
  ],
  "function_explanations": [
    {{"name": "function_name", "purpose": "What it does", "inputs": "Parameters", "output": "Return value", "notes": "Important behavior"}}
  ],
  "class_explanations": [
    {{"name": "ClassName", "purpose": "Role of the class", "key_attributes": "Main state attributes", "key_methods": "Main methods"}}
  ],
  "key_concepts": [
    "Concept 1 (e.g. Asynchronous I/O, Recursion, Context Managers)",
    ...
  ]
}}

Output only the JSON block without markdown fences or outside commentary.
"""
