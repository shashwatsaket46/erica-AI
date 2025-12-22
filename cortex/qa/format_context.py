def format_context(rows):

    context_lines = []
    citations = {}

    for idx, row in enumerate(rows):
        ref = f"[R{idx+1}]"
        citations[ref] = row

        context_lines.append(f"{ref} Concept: {row['concept']}")
        context_lines.append(f"{ref} Chunk ID: {row['chunk_id']}")
        context_lines.append(f"{ref} Span: {row.get('span', '')}")
        context_lines.append("")

    return "\n".join(context_lines), citations
