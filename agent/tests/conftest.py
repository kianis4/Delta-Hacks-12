"""Shared pytest setup for the offline agent tests.

These tests never call Google, MongoDB or the network. The only thing this
file does is give `agent_graph` a placeholder API key, because the module
builds a `ChatGoogleGenerativeAI` client at import time and that client's
validator refuses to construct without *some* key present. Nothing is ever
sent to Google with it.
"""
import os

# Must run before any test module imports `agent.agent_graph`.
os.environ.setdefault("GOOGLE_API_KEY", "test-key-not-real")
