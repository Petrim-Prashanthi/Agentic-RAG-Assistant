import ast
import operator as op
from mcp.server.fastmcp import FastMCP
from src.retriever import retrieve, format_context

mcp = FastMCP("kb-tools")

OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


@mcp.tool()
def search_knowledge_base(query: str, k: int = 4) -> str:
    """Semantic search over the company knowledge base. Use for any factual
    question about products, pricing, policies, or support."""
    hits = retrieve(query, k)
    return format_context(hits) if hits else "No results found."


@mcp.tool()
def calculate(expression: str) -> str:
    """Safely evaluate an arithmetic expression, e.g. '49 * 12 * 0.8'."""
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run()  # stdio transport