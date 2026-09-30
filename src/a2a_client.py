import uuid
import httpx


def discover(base_url: str) -> dict:
    return httpx.get(f"{base_url}/.well-known/agent.json", timeout=10).json()


def send_task(base_url: str, text: str) -> str:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tasks/send",
        "params": {
            "id": str(uuid.uuid4()),
            "message": {"role": "user", "parts": [{"type": "text", "text": text}]},
        },
    }
    r = httpx.post(base_url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        return f"A2A error: {data['error']['message']}"
    return data["result"]["artifacts"][0]["parts"][0]["text"]
