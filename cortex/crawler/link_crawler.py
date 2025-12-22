import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time


# ==========================================
# WEBSITE LINK CRAWLER
# This function crawls a website starting from start_url,
# following internal links up to max_depth, with a delay between requests.
# ==========================================
def crawl_website(start_url, max_depth=3, delay=0.5):

    visited = set()
    domain = urlparse(start_url).netloc

    def crawl(url, depth):
        if depth > max_depth:
            return
        if url in visited:
            return
        if urlparse(url).netloc != domain:
            return

        visited.add(url)

        try:
            print(f"[CRAWL] {url}")
            time.sleep(delay)
            r = requests.get(url, timeout=10)
        except Exception as e:
            print(f"[ERROR] Could not open {url}: {e}")
            return

        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup.find_all("a", href=True):
            link = urljoin(url, tag["href"])
            if "#" in link:
                link = link.split("#")[0]
            if link.endswith((".pdf", ".jpg", ".png", ".zip", ".pptx")):
                continue
            crawl(link, depth + 1)

    crawl(start_url, 0)
    return sorted(visited)
