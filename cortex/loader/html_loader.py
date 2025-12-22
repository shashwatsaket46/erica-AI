from bs4 import BeautifulSoup

# =========================================================
# HTML LOADER
# This function extracts readable text from raw HTML bytes.
# =========================================================
def load_html(html_bytes: bytes) -> str:
    soup = BeautifulSoup(html_bytes, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return soup.get_text(separator="\n")
