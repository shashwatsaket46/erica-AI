def answer_question(question: str, context: str, ask_llm):
    prompt = f"""
You are Erica, an expert ML tutor.

Use ONLY the context below to answer the user's question.
If something is not in the context, say "Not available in knowledge graph."

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    return ask_llm(prompt)
