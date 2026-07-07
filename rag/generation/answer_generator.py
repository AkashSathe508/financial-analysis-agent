# Answer generation logic lives in rag/nodes/answer_generation_node.py
# This module re-exports it for convenience.
from rag.nodes.answer_generation_node import answer_generation_node

__all__ = ["answer_generation_node"]
