import pytest
from src.ingest import chunk_text
from src.mcp_server import calculate


def test_chunk_overlap():
    words = " ".join(str(i) for i in range(100))
    chunks = chunk_text(words, size=50, overlap=10)
    assert chunks[0].split()[-10:] == chunks[1].split()[:10]


def test_calculate_ok():
    assert calculate("49 * 12 * 0.8") == "470.4"


@pytest.mark.parametrize("bad", ["__import__('os').system('dir')", "open('x')", "1 + a"])
def test_calculate_rejects_malicious(bad):
    assert calculate(bad).startswith("Error")