from typing import Any, Dict, Optional
from app.ai.models import AIAnalysisContext


def build_review_prompt(context: AIAnalysisContext) -> str:
    """Build a comprehensive code review prompt combining AST, complexity, security, and readability findings."""
    issues_summary = "\n".join(
        f"- [{issue.get('severity', 'INFO')}] {issue.get('title', '')} (Line {issue.get('line_number', '?')}): {issue.get('description', '')}"
        for issue in context.issues[:20]
    ) or "None detected."

    security_summary = "\n".join(
        f"- [{sec.get('severity', 'CRITICAL')}] {sec.get('title', '')} (Line {sec.get('line_number', '?')}): {sec.get('description', '')} | Suggestion: {sec.get('suggestion', '')}"
        for sec in context.security_findings
    ) or "No security vulnerabilities detected by static analyzer."

    return f"""You are CodePilot AI, a Principal Software Engineer and Staff Security Reviewer.
Analyze the following source code along with its Phase 5 Static AST Analysis Report.

### SOURCE CODE METADATA
- Language: {context.language}
- Filename: {context.filename}
- Static Overall Score: {context.overall_score if context.overall_score is not None else 'N/A'}/100
- Readability Score: {context.readability_score if context.readability_score is not None else 'N/A'}/100
- Maintainability Score: {context.maintainability_score if context.maintainability_score is not None else 'N/A'}/100
- Security Score: {context.security_score if context.security_score is not None else 'N/A'}/100
- Cyclomatic Complexity: {context.cyclomatic_complexity if context.cyclomatic_complexity is not None else 'N/A'} (Rank: {context.complexity_rank})

### STATIC AST & SECURITY FINDINGS
Static Issues Detected:
{issues_summary}

Security Findings:
{security_summary}

### SOURCE CODE TO REVIEW:
```{context.language}
{context.source_code}
```

### INSTRUCTIONS:
Perform a deep semantic code review. Enrich the static analysis with your reasoning.
You MUST output your response in valid JSON format matching this schema:
{{
  "summary": "High-level summary of the code and its quality",
  "overall_assessment": "Comprehensive assessment of code structure, design patterns, and engineering quality",
  "strengths": ["Strength 1", "Strength 2", ...],
  "critical_issues": ["Issue 1 with impact and line reference", ...],
  "security_analysis": "Detailed evaluation of security posture, data flow, and threat modeling",
  "complexity_analysis": "Evaluation of cyclomatic complexity, cognitive load, and algorithmic efficiency",
  "readability_analysis": "Review of naming conventions, modularity, and PEP 8 / style conventions",
  "maintainability_analysis": "Assessment of extensibility, testability, and refactoring needs",
  "optimization_suggestions": ["Performance / memory optimization 1", ...],
  "refactoring_suggestions": ["Refactoring suggestion 1", ...],
  "best_practices": ["Best practice recommendation 1", ...],
  "next_steps": ["Priority action item 1", "Priority action item 2", ...]
}}

Output only the JSON block without markdown fences or outside commentary.
"""
