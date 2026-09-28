# Code Review & Quality Audit Report

**Target File**: `{{ filename }}`  
**Language**: {{ language }}  
**Generated At**: {{ generated_at }}  
**Model**: {{ model_used }}

---

## 📊 Executive Summary

{{ summary }}

---

## 🎯 Quality Score Dashboard

| Metric | Score / Value | Status |
|---|---|---|
| **Overall Quality Score** | **{{ scores.overall | default(0) }} / 100** | {{ "🟢 PASS" if (scores.overall | default(0)) >= 80 else "🟡 WARNING" if (scores.overall | default(0)) >= 60 else "🔴 CRITICAL" }} |
| Readability Score | {{ scores.readability | default(0) }} / 100 | {{ "Optimal" if (scores.readability | default(0)) >= 75 else "Needs Improvement" }} |
| Security Score | {{ scores.security | default(0) }} / 100 | {{ "Secure" if (scores.security | default(0)) >= 85 else "Action Required" }} |
| Maintainability Score | {{ scores.maintainability | default(0) }} / 100 | Grade: {{ complexity.rank | default("A") }} |
| Cyclomatic Complexity | {{ complexity.cyclomatic_complexity | default(1.0) }} | Rank {{ complexity.rank | default("A") }} |

---

## 🛡️ Security Vulnerabilities & Findings

{% if security_findings %}
{% for sec in security_findings %}
- **[{{ sec.severity }}] {{ sec.title }}** (Line {{ sec.line_number | default("?") }}): {{ sec.description }}  
  *Remediation*: `{{ sec.suggestion | default("Inspect and sanitize input.") }}`
{% endfor %}
{% else %}
*No security vulnerabilities detected by static or AI security scans.*
{% endif %}

---

## 🔍 Priority Issues & Code Smells

{% if issues %}
{% for issue in issues %}
- **[{{ issue.severity }}] {{ issue.title }}** (Line {{ issue.line_number | default("?") }}): {{ issue.description }}
{% endfor %}
{% else %}
*No critical code smells detected.*
{% endif %}

---

## ✨ Key Strengths

{% for strength in strengths %}
- {{ strength }}
{% endfor %}

---

## 🚀 Recommended Optimization & Refactoring Roadmap

{% for step in next_steps %}
1. {{ step }}
{% endfor %}

---
*Report generated automatically by CodePilot AI (Phase 7 Export Engine).*
