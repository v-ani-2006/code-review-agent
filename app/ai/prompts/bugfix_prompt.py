from app.ai.models import AIAnalysisContext


def build_bugfix_prompt(context: AIAnalysisContext) -> str:
    """Build a bugfix prompt targeting logic bugs, syntax errors, edge-case crashes, and security vulnerabilities."""
    issues_summary = "\n".join(
        f"- [{issue.get('severity', 'INFO')}] {issue.get('title', '')} (Line {issue.get('line_number', '?')}): {issue.get('description', '')}"
        for issue in context.issues
    ) or "No static syntax/AST bugs reported."

    security_summary = "\n".join(
        f"- [{sec.get('severity', 'CRITICAL')}] {sec.get('title', '')} (Line {sec.get('line_number', '?')}): {sec.get('description', '')}"
        for sec in context.security_findings
    ) or "None."

    return f"""You are a Principal Software Engineer and debugging expert.
Detect all logic bugs, runtime errors, off-by-one errors, unhandled exceptions, and security vulnerabilities in the following {context.language} code, and provide the definitive fix.

### SOURCE CODE METADATA
- Language: {context.language}
- Filename: {context.filename}

### STATIC FINDINGS:
Issues:
{issues_summary}

Security Findings:
{security_summary}

### SOURCE CODE TO FIX:
```{context.language}
{context.source_code}
```

### INSTRUCTIONS:
Fix all bugs while preserving intended functionality.
You MUST output your response in valid JSON format matching this schema:
{{
  "corrected_code": "Complete, working, and fully corrected source code",
  "identified_bugs": [
    {{"bug": "Description of bug", "line_number": 12, "severity": "HIGH", "type": "Logic / Syntax / Security / Resource Leak"}}
  ],
  "changed_sections": [
    {{"line_range": "10-15", "before": "original code fragment", "after": "fixed code fragment"}}
  ],
  "reasons_for_changes": [
    "Detailed explanation of why each change was made and how it resolves the failure mode"
  ],
  "verification_steps": [
    "How to verify the fix (e.g. run test with boundary input X)"
  ]
}}

Output only the JSON block without markdown fences or outside commentary.
"""
