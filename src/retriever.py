from src.ingest import get_collection


def retrieve(query: str, k: int = 4):
    res = get_collection().query(query_texts=[query], n_results=k)
    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append(
            {"text": doc, "source": meta["source"], "score": round(1 - dist, 3)}
        )
    return hits


def format_context(hits) -> str:
    return "\n\n".join(
        f'<doc id="{i+1}" source="{h["source"]}">\n{h["text"]}\n</doc>'
        for i, h in enumerate(hits)
    )
