# Changelog

All notable changes to `{{ filename }}` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [{{ version | default("Unreleased") }}] - {{ date }}

### 🚀 Added
{% if added %}
{% for item in added %}
- {{ item }}
{% endfor %}
{% else %}
- *No new features added.*
{% endif %}

### 🔄 Changed
{% if changed %}
{% for item in changed %}
- {{ item }}
{% endfor %}
{% else %}
- *No existing functionality modified.*
{% endif %}

### 🗑️ Removed
{% if removed %}
{% for item in removed %}
- {{ item }}
{% endfor %}
{% else %}
- *No deprecated or unused code removed.*
{% endif %}

### 🐛 Fixed
{% if fixed %}
{% for item in fixed %}
- {{ item }}
{% endfor %}
{% else %}
- *No bug fixes in this release.*
{% endif %}

### 🔒 Security
{% if security %}
{% for item in security %}
- {{ item }}
{% endfor %}
{% else %}
- *No security-critical patches applied.*
{% endif %}
