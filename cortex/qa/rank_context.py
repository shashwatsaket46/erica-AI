def rank_context(query: str, rows: list, top_k: int = 10):
    
    scored = []
    q = query.lower()
    for row in rows:
        text = row["concept"].lower()
        score = 0
        for w in q.split():
            if w in text:
                score += 2
        if row.get("type") == "pdf":
            score += 1

        scored.append((score, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    top_rows = [r for _, r in scored[:top_k]]

    return top_rows
