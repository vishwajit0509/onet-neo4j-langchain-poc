from typing import List,Dict,Any

def format_link_section(title: str, items: List[Dict[str, str]], empty_msg: str) -> str:
    """Formats a list of dicts into clickable Markdown links."""
    if not items: return ""
    lines = [f"### {title}"]
    for item in items:
        snippet = item.get("snippet", "").strip()
        link = f"- [{item['title']}]({item['url']})"
        lines.append(f"{link} — {snippet}" if snippet else link)
    return "\n".join(lines)

def format_gaps(gaps: List[Dict[str, Any]]) -> str:
    """Formats numerical skill gap data into a human-readable list."""
    if not gaps: return "No major gaps found."
    lines = []
    for g in gaps:
        skill = g.get('skill', 'Unknown')
        try:
            val = round(float(g.get('gap', 0)), 1)
            lines.append(f"- {skill} (+{val})")
        except:
            lines.append(f"- {skill}")
    return "\n".join(lines)



