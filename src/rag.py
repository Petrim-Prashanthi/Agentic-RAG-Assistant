from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY, MODEL
from src.prompts import RAG_SYSTEM_PROMPT
from src.retriever import retrieve, format_context

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def answer(query: str) -> str:
    context = format_context(retrieve(query))
    msg = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=RAG_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"<context>\n{context}\n</context>\n\nQuestion: {query}"}
        ],
    )
    return msg.content[0].text


if __name__ == "__main__":
    while True:
        q = input("Ask: ")
        if q.lower() in {"exit", "quit"}:
            break
        print(answer(q), "\n")
