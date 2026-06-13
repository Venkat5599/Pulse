"""Pulse RAG agent — retrieval-augmented Q&A over the Pulse skill knowledge base.

Retrieves the most relevant passages from the Pulse docs/skill/scripts with BM25,
then has DeepSeek V4 Flash answer grounded in those passages with inline citations.
"""

__version__ = "1.0.0"
