# Technical Documentation: {{ module_name }}

> **File**: `{{ filename }}` | **Language**: {{ language }} | **Generated At**: {{ generated_at }}

---

## 📖 Module Overview

{{ module_overview }}

---

{% if classes %}
## 🏛️ Class Reference

{% for cls in classes %}
### `class {{ cls.name }}`

{{ cls.docstring }}

{% if cls.attributes %}
**Attributes:**
| Attribute | Type | Description |
|---|---|---|
{% for attr in cls.attributes %}
| `{{ attr.name }}` | `{{ attr.type }}` | {{ attr.description }} |
{% endfor %}
{% endif %}

{% if cls.methods %}
**Methods:**
{% for m in cls.methods %}
#### `{{ m.name }}({{ m.params }})`
{{ m.docstring }}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

---

{% if functions %}
## ⚙️ Function Reference

{% for fn in functions %}
### `def {{ fn.name }}({{ fn.signature }})`

{{ fn.docstring }}

**Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
{% for p in fn.parameters %}
| `{{ p.name }}` | `{{ p.type }}` | `{{ p.default | default("None") }}` | {{ p.description }} |
{% endfor %}

**Returns:**
- `{{ fn.return_type }}`: {{ fn.return_description }}

{% if fn.raises %}
**Raises:**
{% for r in fn.raises %}
- `{{ r.exception }}`: {{ r.description }}
{% endfor %}
{% endif %}

{% if fn.example %}
**Example:**
```{{ language }}
{{ fn.example }}
```
{% endif %}

---
{% endfor %}
{% endif %}

## 💡 Practical Usage Examples

```{{ language }}
{{ usage_examples }}
```
