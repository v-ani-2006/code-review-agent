from app.ai.models import AIAnalysisContext


def build_optimize_prompt(context: AIAnalysisContext) -> str:
    """Build a code optimization prompt focusing on time complexity, memory allocation, and Pythonic idioms."""
    return f"""You are a High-Performance Python Systems Engineer and algorithmic optimization specialist.
Analyze and optimize the following {context.language} code for maximum performance, minimal memory footprint, and idiomatic clarity.

### SOURCE CODE METADATA
- Language: {context.language}
- Filename: {context.filename}
- Static Complexity: {context.cyclomatic_complexity if context.cyclomatic_complexity is not None else 'N/A'} (Rank: {context.complexity_rank})
- Maintainability Score: {context.maintainability_score if context.maintainability_score is not None else 'N/A'}/100

### SOURCE CODE TO OPTIMIZE:
```{context.language}
{context.source_code}
```

### INSTRUCTIONS:
Produce fully optimized code while preserving the exact same public API, behavior, and expected outputs.
You MUST output your response in valid JSON format matching this schema:
{{
  "optimized_code": "Complete, production-ready optimized Python source code",
  "performance_improvements": [
    "Explanation of time complexity reduction (e.g. O(N^2) to O(N))",
    ...
  ],
  "memory_improvements": [
    "Explanation of memory allocation reduction (e.g. generator expression instead of list, slots)",
    ...
  ],
  "pythonic_improvements": [
    "Use of built-in idioms (e.g. list comprehension, itertools, collections, walrus operator)",
    ...
  ],
  "time_complexity_before": "e.g. O(N^2)",
  "time_complexity_after": "e.g. O(N)",
  "space_complexity_before": "e.g. O(N)",
  "space_complexity_after": "e.g. O(1)"
}}

Output only the JSON block without markdown fences or outside commentary.
"""
