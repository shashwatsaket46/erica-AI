import requests
from bs4 import BeautifulSoup
from cortex.loader.html_loader import load_html
from cortex.loader.text_cleaner import clean_text

# ==========================================
# WEBSITE LOADER
# This function downloads a webpage and extracts readable text.
# ==========================================
def load_website(url: str) -> str:
    """Download a webpage and extract readable text."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return ""

    text = load_html(r.content)
    cleaned = clean_text(text)
    return cleaned
