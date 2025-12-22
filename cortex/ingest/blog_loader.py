import requests
from bs4 import BeautifulSoup
from cortex.loader.text_cleaner import clean_text

# ==========================================
# BLOG LOADER
# This function fetches and cleans text from a blog URL.
# ==========================================
def load_blog(url: str) -> str:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Blog fetch failed: {url}: {e}")
        return ""

    soup = BeautifulSoup(r.text, "html.parser")
    article = soup.find("article")
    text = article.get_text(separator="\n") if article else soup.get_text(separator="\n")

    return clean_text(text)
