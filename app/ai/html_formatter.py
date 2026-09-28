import html
from typing import Optional
import markdown


def convert_markdown_to_html(markdown_content: str, title: str = "CodePilot AI Report") -> str:
    """Convert Markdown text to full, beautifully styled, responsive HTML."""
    try:
        # Enable standard GitHub-flavored markdown extensions
        md = markdown.Markdown(
            extensions=[
                "fenced_code",
                "tables",
                "toc",
                "nl2br",
                "sane_lists",
            ]
        )
        html_body = md.convert(markdown_content)
    except Exception:
        # Fallback if markdown conversion throws on anomalous syntax
        escaped = html.escape(markdown_content)
        html_body = f"<pre><code>{escaped}</code></pre>"

    return build_styled_html_document(html_body, title=title)


def build_styled_html_document(body_html: str, title: str = "CodePilot AI Report") -> str:
    """Wrap body HTML inside a self-contained, responsive, styled modern document."""
    escaped_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escaped_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-color: #0d1117;
      --card-bg: #161b22;
      --border-color: #30363d;
      --text-primary: #c9d1d9;
      --text-muted: #8b949e;
      --heading-color: #f0f6fc;
      --accent: #58a6ff;
      --accent-hover: #79c0ff;
      --code-bg: #090d13;
      --table-stripe: #1c2128;
      --badge-pass: #238636;
      --badge-warn: #d29922;
      --badge-fail: #da3633;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      background-color: var(--bg-color);
      color: var(--text-primary);
      line-height: 1.6;
      padding: 2rem 1rem;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      background-color: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 2.5rem 3rem;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }}
    header.report-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 1.5rem;
      margin-bottom: 2rem;
    }}
    .logo-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 700;
      color: var(--accent);
      font-size: 1.1rem;
      letter-spacing: -0.5px;
    }}
    h1, h2, h3, h4, h5, h6 {{
      color: var(--heading-color);
      font-weight: 600;
      margin-top: 1.8rem;
      margin-bottom: 0.8rem;
    }}
    h1 {{
      font-size: 2rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.5rem;
    }}
    h2 {{
      font-size: 1.4rem;
      color: var(--accent);
    }}
    h3 {{
      font-size: 1.15rem;
    }}
    p {{
      margin-bottom: 1rem;
      color: var(--text-primary);
    }}
    ul, ol {{
      margin-bottom: 1.2rem;
      padding-left: 1.8rem;
    }}
    li {{
      margin-bottom: 0.4rem;
    }}
    pre {{
      background-color: var(--code-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.2rem;
      overflow-x: auto;
      margin: 1.2rem 0;
      font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
      font-size: 0.9rem;
    }}
    code {{
      font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
      background-color: rgba(110, 118, 129, 0.4);
      padding: 0.2em 0.4em;
      border-radius: 4px;
      font-size: 0.88em;
    }}
    pre code {{
      background-color: transparent;
      padding: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1.5rem 0;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--border-color);
    }}
    th, td {{
      padding: 0.75rem 1rem;
      text-align: left;
      border-bottom: 1px solid var(--border-color);
    }}
    th {{
      background-color: var(--table-stripe);
      color: var(--heading-color);
      font-weight: 600;
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    tr:nth-child(even) {{
      background-color: rgba(255, 255, 255, 0.02);
    }}
    tr:hover {{
      background-color: rgba(88, 166, 255, 0.05);
    }}
    blockquote {{
      border-left: 4px solid var(--accent);
      padding: 0.5rem 1rem;
      color: var(--text-muted);
      background-color: rgba(88, 166, 255, 0.05);
      border-radius: 0 6px 6px 0;
      margin: 1.2rem 0;
    }}
    hr {{
      border: 0;
      border-top: 1px solid var(--border-color);
      margin: 2rem 0;
    }}
    footer {{
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border-color);
      color: var(--text-muted);
      font-size: 0.85rem;
      text-align: center;
    }}
    @media (max-width: 768px) {{
      .container {{
        padding: 1.5rem 1.2rem;
      }}
      h1 {{
        font-size: 1.6rem;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header class="report-header">
      <div class="logo-badge">
        <span>🤖</span>
        <span>CodePilot AI</span>
      </div>
      <div style="font-size: 0.85rem; color: var(--text-muted);">
        Automated Technical Report
      </div>
    </header>
    <main>
      {body_html}
    </main>
    <footer>
      Generated with CodePilot AI Reasoning & Export Engine &bull; Confidential &bull; Phase 7
    </footer>
  </div>
</body>
</html>
"""
