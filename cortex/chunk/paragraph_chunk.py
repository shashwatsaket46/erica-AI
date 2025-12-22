import re

def normalize_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\s*\.\s*\.', '…', text)
    text = re.sub(r'\(\s*([0-9]+)\s*\)', r'(\1)', text)
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'(CHAPTER\s+\d+)', r'\n\n\1\n\n', text)
    text = re.sub(r'(\d+\.\d+)', r'\n\n\1\n\n', text)

    return text


def split_sentences(text: str):
    pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if len(s.strip()) > 0]


def paragraph_chunk(text: str, target_size: int = 450) -> list:
    """
    Final chunker:
    - Normalizes raw giant-line text
    - Splits into sentences using robust heuristics
    - Merges into chunks of controlled size
    """

    text = normalize_text(text)
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        tokens = text.split()
        chunks = []
        for i in range(0, len(tokens), 80):
            chunks.append(" ".join(tokens[i:i+80]))
        return chunks

    chunks = []
    buffer = ""

    for s in sentences:
        if len(buffer) + len(s) < target_size:
            buffer += " " + s
        else:
            chunks.append(buffer.strip())
            buffer = s

    if buffer:
        chunks.append(buffer.strip())

    return chunks
