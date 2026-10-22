import re

def slugify_text(text: str) -> str:
    text = text.lower().strip()

    text = re.sub(r'[^a-z0-9]+', '-', text)

    return text.strip('-')
