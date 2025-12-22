import re
import os
from urllib.parse import urlparse

# ==========================================
# FILE UTILITIES
# This module provides utility functions for sanitizing filenames
# and saving text content to files.
# ==========================================
def sanitize_filename(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace(".", "_")
    path = parsed.path.strip("/")
    if path == "":
        path = "index"
    parts = path.split("/")
    if len(parts) > 2:
        parts = parts[-2:]
    path = "_".join(parts)
    name = f"{domain}_{path}"
    name = re.sub(r"[^a-zA-Z0-9_\.-]", "_", name)
    return name[:120]

# ==========================================
# SAVE TEXT TO FILE
# This function saves the given text content to a specified path
# with the given filename.
# ==========================================
def save_text(path: str, name: str, text: str):
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, f"{name}.txt")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(text)
    return full_path
