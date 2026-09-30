import json
from pathlib import Path
from src.retriever import retrieve
from src.rag import answer

EVAL_PATH = Path(__file__).resolve().parent.parent / "data" / "eval_set.json"
K = 4
REFUSAL = "don't have that information"


def main():
    cases = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    answerable = [c for c in cases if c["expected_source"]]
    unanswerable = [c for c in cases if not c["expected_source"]]

    hits_at_k, rr_total, ans_correct = 0, 0.0, 0
    for c in answerable:
        hits = retrieve(c["question"], K)
        sources = [h["source"] for h in hits]
        # Retrieval: is a chunk containing the keyword from the right file in the top-k?
        rank = next(
            (i + 1 for i, h in enumerate(hits)
             if h["source"] == c["expected_source"]
             and c["expected_keyword"].lower() in h["text"].lower()),
            None,
        )
        if rank:
            hits_at_k += 1
            rr_total += 1 / rank
        # Generation: does the final answer contain the expected fact?
        reply = answer(c["question"])
        ok = c["expected_keyword"].lower() in reply.lower()
        ans_correct += ok
        print(f"[{'PASS' if ok else 'FAIL'}] rank={rank} {c['question']}")

    refused = 0
    for c in unanswerable:
        reply = answer(c["question"])
        ok = REFUSAL in reply.lower()
        refused += ok
        print(f"[{'PASS' if ok else 'FAIL'}] (refusal) {c['question']}")

    n = len(answerable)
    print("\n--- Results ---")
    print(f"Retrieval Hit@{K}:      {hits_at_k}/{n} = {hits_at_k/n:.0%}")
    print(f"Retrieval MRR:         {rr_total/n:.3f}")
    print(f"Answer accuracy:       {ans_correct}/{n} = {ans_correct/n:.0%}")
    if unanswerable:
        print(f"Correct refusals:      {refused}/{len(unanswerable)}")


if __name__ == "__main__":
    main()