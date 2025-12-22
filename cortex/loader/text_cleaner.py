import re

# =========================================================
# TEXT CLEANER
# This module provides a basic text cleaning function.
# =========================================================
def clean_text(text: str) -> str:
    """Basic cleaning."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
