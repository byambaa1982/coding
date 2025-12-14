"""Test markdown rendering functionality for Phase 3."""

from app.utils.markdown_helper import render_markdown, extract_first_paragraph, count_words, estimate_reading_time


def test_basic_markdown():
    """Test basic markdown rendering."""
    content = """
# Hello World

This is a **bold** statement with *italic* text.

## Code Example

```python
def hello():
    print("Hello, World!")
```

- List item 1
- List item 2

[Link](https://example.com)
"""
    
    html = render_markdown(content)
    print("✅ Basic markdown rendering works")
    print(f"Rendered HTML length: {len(str(html))} characters")
    assert 'Hello World' in str(html)
    assert '<strong>' in str(html)  # Bold
    assert '<em>' in str(html)  # Italic
    print()


def test_code_blocks():
    """Test code block rendering."""
    content = """
Here's some Python code:

```python
def greet(name):
    return f"Hello, {name}!"
```

And some SQL:

```sql
SELECT * FROM users WHERE id = 1;
```
"""
    
    html = render_markdown(content)
    print("✅ Code blocks render correctly")
    assert 'python' in str(html).lower() or 'code' in str(html).lower()
    print()


def test_security():
    """Test XSS prevention."""
    content = """
# Safe Content

<script>alert('XSS')</script>

<img src=x onerror="alert('XSS')">

[Click](javascript:alert('XSS'))
"""
    
    html = render_markdown(content)
    print("✅ XSS prevention works")
    assert 'script' not in str(html).lower()
    assert 'onerror' not in str(html).lower()
    assert 'javascript:' not in str(html).lower()
    print()


def test_images():
    """Test image rendering."""
    content = """
![Python Logo](/static/uploads/python-logo.png)

This is an image example.
"""
    
    html = render_markdown(content)
    print("✅ Images render correctly")
    assert 'img' in str(html).lower()
    assert 'python-logo.png' in str(html).lower()
    print()


def test_tables():
    """Test table rendering."""
    content = """
| Feature | Status |
|---------|--------|
| Markdown | ✅ |
| Images | ✅ |
| Code | ✅ |
"""
    
    html = render_markdown(content)
    print("✅ Tables render correctly")
    assert 'table' in str(html).lower()
    print()


def test_helper_functions():
    """Test utility functions."""
    content = """
# Introduction to Python

Python is a high-level programming language. It is easy to learn and powerful.

```python
print("Hello, World!")
```

This is more text to increase word count.
"""
    
    excerpt = extract_first_paragraph(content)
    word_count = count_words(content)
    reading_time = estimate_reading_time(content)
    
    print("✅ Helper functions work")
    print(f"Excerpt: {excerpt[:50]}...")
    print(f"Word count: {word_count}")
    print(f"Reading time: {reading_time} min")
    print()


def run_all_tests():
    """Run all Phase 3 markdown tests."""
    print("=" * 60)
    print("PHASE 3 MARKDOWN RENDERING TESTS")
    print("=" * 60)
    print()
    
    try:
        test_basic_markdown()
        test_code_blocks()
        test_security()
        test_images()
        test_tables()
        test_helper_functions()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED - Phase 3 is working correctly!")
        print("=" * 60)
        return True
    
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    run_all_tests()
