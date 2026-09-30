from anthropic import Anthropic
from fastapi import FastAPI
from src.config import ANTHROPIC_API_KEY, MODEL
from src.prompts import SUMMARIZER_SYSTEM_PROMPT

app = FastAPI(title="Summarizer Agent")
client = Anthropic(api_key=ANTHROPIC_API_KEY)

AGENT_CARD = {
    "name": "summarizer-agent",
    "description": "Summarizes text into concise, faithful bullet points.",
    "url": "http://localhost:9000",
    "version": "1.0.0",
    "capabilities": {"streaming": False},
    "skills": [
        {
            "id": "summarize",
            "name": "Summarize text",
            "description": "Condenses long text into 3-5 bullets.",
        }
    ],
}


@app.get("/.well-known/agent.json")
def agent_card():
    return AGENT_CARD


@app.post("/")
def rpc(req: dict):
    if req.get("method") != "tasks/send":
        return {
            "jsonrpc": "2.0",
            "id": req.get("id"),
            "error": {"code": -32601, "message": "Method not found"},
        }
    params = req["params"]
    text = params["message"]["parts"][0]["text"]
    msg = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SUMMARIZER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    summary = msg.content[0].text
    return {
        "jsonrpc": "2.0",
        "id": req.get("id"),
        "result": {
            "id": params["id"],
            "status": {"state": "completed"},
            "artifacts": [{"parts": [{"type": "text", "text": summary}]}],
        },
    }