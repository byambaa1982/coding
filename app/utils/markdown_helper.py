"""Markdown rendering utilities for instructor panel."""
import markdown2
import bleach
from flask import Markup


# Allowed HTML tags and attributes for security
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'hr', 'div', 'span',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img', 'abbr', 'acronym', 'b', 'i',
    'sup', 'sub', 'del', 'ins'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class'],
    'div': ['class']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def render_markdown(content):
    """
    Convert markdown to safe HTML.
    
    Args:
        content (str): Markdown content
        
    Returns:
        Markup: Safe HTML ready for display
    """
    if not content:
        return Markup("")
    
    # Convert markdown to HTML with extras
    html = markdown2.markdown(
        content,
        extras=[
            'fenced-code-blocks',  # ```python code ```
            'tables',              # GitHub-style tables
            'code-friendly',       # Better code handling
            'cuddled-lists',       # Better list handling
            'header-ids',          # Auto-generate header IDs
            'footnotes',           # Footnote support
            'strike',              # ~~strikethrough~~
            'task_list',           # - [ ] task lists
            'smarty-pants',        # Smart quotes
            'link-patterns',       # Auto-link URLs
        ]
    )
    
    # Sanitize HTML for security
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )
    
    return Markup(clean_html)


def extract_first_paragraph(content, max_length=200):
    """
    Extract first paragraph from markdown content.
    
    Args:
        content (str): Markdown content
        max_length (int): Maximum length of excerpt
        
    Returns:
        str: Plain text excerpt
    """
    if not content:
        return ""
    
    # Remove markdown formatting
    text = content.split('\n\n')[0]  # Get first paragraph
    text = text.replace('#', '').replace('*', '').replace('_', '')
    text = text.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
    text = text.strip()
    
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text


def count_words(content):
    """
    Count words in markdown content.
    
    Args:
        content (str): Markdown content
        
    Returns:
        int: Word count
    """
    if not content:
        return 0
    
    # Remove code blocks
    text = content
    import re
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    
    # Remove markdown syntax
    text = re.sub(r'[#*_\[\]()~`]', '', text)
    
    # Count words
    words = text.split()
    return len(words)


def estimate_reading_time(content):
    """
    Estimate reading time in minutes (avg 200 words/min).
    
    Args:
        content (str): Markdown content
        
    Returns:
        int: Estimated reading time in minutes
    """
    word_count = count_words(content)
    minutes = max(1, round(word_count / 200))
    return minutes
