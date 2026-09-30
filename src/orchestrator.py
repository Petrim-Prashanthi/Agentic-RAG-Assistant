import asyncio
import sys
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src import a2a_client
from src.config import ANTHROPIC_API_KEY, MODEL
from src.prompts import ORCHESTRATOR_SYSTEM_PROMPT

A2A_URL = "http://localhost:9000"
llm = Anthropic(api_key=ANTHROPIC_API_KEY)

A2A_TOOL = {
    "name": "delegate_to_summarizer",
    "description": "Delegate to the remote summarizer agent (A2A). Use when the "
                   "user wants text or retrieved content summarized.",
    "input_schema": {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "Text to summarize"}},
        "required": ["text"],
    },
}


async def run_agent(session: ClientSession, question: str, history: list) -> str:
    mcp_tools = (await session.list_tools()).tools
    tools = [
        {"name": t.name, "description": t.description or "", "input_schema": t.inputSchema}
        for t in mcp_tools
    ] + [A2A_TOOL]

    history.append({"role": "user", "content": question})

    for _ in range(6):  # safety cap on reasoning steps
        resp = llm.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=tools,
            messages=history,
        )
        history.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            print(f"  [tool] {block.name}({block.input})")
            if block.name == "delegate_to_summarizer":
                out = await asyncio.to_thread(
                    a2a_client.send_task, A2A_URL, block.input["text"]
                )
            else:
                r = await session.call_tool(block.name, block.input)
                out = "\n".join(c.text for c in r.content if c.type == "text")
            results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": out}
            )
        history.append({"role": "user", "content": results})

    return "Stopped: too many tool steps."


async def main():
    try:
        card = a2a_client.discover(A2A_URL)
        print(f"Discovered A2A agent: {card['name']} - {card['description']}")
    except Exception:
        print("Warning: A2A agent not running (start it on port 9000).")

    params = StdioServerParameters(command=sys.executable, args=["-m", "src.mcp_server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            history: list = []
            print("Agentic RAG Assistant ready. Type 'exit' to quit.")
            while True:
                q = input("\nYou: ").strip()
                if q.lower() in {"exit", "quit"}:
                    break
                print("\nAssistant:", await run_agent(session, q, history))


if __name__ == "__main__":
    asyncio.run(main())
