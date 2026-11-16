"""Small pure helpers for generated text content."""


def normalize_text_content(content: str) -> str:
    """Convert escaped line-break sequences emitted by a model into real newlines."""
    return content.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")
