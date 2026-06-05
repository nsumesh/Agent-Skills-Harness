"""Importable, network-free core: the output contract, renderer, probes, checks, and eval API.

Everything reusable lives here. The MCP server (Layer 2) and the eval/loop import this
package directly; nothing in `core/` reaches for an LLM or a browser at import time.
"""
