"""Offline tests for the router node and the research node's jurisdiction filter.

The real LLM (`agent_graph.llm`) and the real vector store
(`agent_graph.MongoDBAtlasVectorSearch`) are swapped out with tiny fakes via
pytest's `monkeypatch`, so these tests run with no API keys and no network.
"""
import pytest
from langchain_core.messages import HumanMessage
from pydantic import ValidationError

from agent import agent_graph
from agent.agent_graph import LegalTopic, RouterOutput, UserIntent


# --- Fakes -----------------------------------------------------------------

class FakeStructuredLLM:
    """Stands in for `llm.with_structured_output(...)`; `.invoke` returns a canned object."""

    def __init__(self, result):
        self.result = result

    def invoke(self, messages):
        return self.result


class FakeLLM:
    """Stands in for the module-level `agent_graph.llm`."""

    def __init__(self, result):
        self.result = result

    def with_structured_output(self, schema):
        return FakeStructuredLLM(self.result)


class FakeDoc:
    """Minimal stand-in for a LangChain Document returned by similarity_search."""

    def __init__(self, source, content):
        self.metadata = {"source": source}
        self.page_content = content


class FakeVectorStore:
    """Stands in for `MongoDBAtlasVectorSearch`; records the kwargs passed to similarity_search."""

    calls = []

    def __init__(self, collection, embeddings, index_name=None):
        pass

    def similarity_search(self, query, k=4, pre_filter=None):
        FakeVectorStore.calls.append({"query": query, "k": k, "pre_filter": pre_filter})
        return [FakeDoc("ontario_rta.html", "Section 48: landlord's own use.")]


# --- Router node -------------------------------------------------------------

def test_router_node_returns_valid_intent_and_jurisdiction(monkeypatch):
    """With a stubbed LLM, router_node emits a typed intent and the detected jurisdiction."""
    canned = RouterOutput(
        detected_jurisdiction="BC",
        intent=UserIntent.ADVICE,
        topic=LegalTopic.TENANCY,
        legal_issue="Landlord raised rent by 10 percent.",
        missing_info_question=None,
    )
    monkeypatch.setattr(agent_graph, "llm", FakeLLM(canned))

    state = {"messages": [HumanMessage(content="I am in BC. My landlord raised my rent 10%.")]}
    updates = agent_graph.router_node(state)

    # The intent must be the plain string value, not the enum object
    # (a str-Enum compares equal to its value, so check the type too).
    assert type(updates["user_intent"]) is str
    assert updates["user_intent"] in [i.value for i in UserIntent]
    assert updates["user_intent"] == "ADVICE"
    assert type(updates["topic"]) is str
    assert updates["topic"] in [t.value for t in LegalTopic]
    assert updates["topic"] == "TENANCY"
    assert updates["jurisdiction"] == "BC"
    assert updates["legal_issue"] == "Landlord raised rent by 10 percent."


def test_router_output_rejects_invalid_intent():
    """RouterOutput is a typed schema: an unknown intent string fails validation."""
    with pytest.raises(ValidationError):
        RouterOutput(
            detected_jurisdiction="ON",
            intent="NOT_A_REAL_INTENT",
            legal_issue="Anything.",
            missing_info_question=None,
        )


# --- Research node: jurisdiction filter --------------------------------------

@pytest.mark.parametrize("province", ["BC", "ON"])
def test_research_node_filters_by_province_and_federal(monkeypatch, province):
    """research_node must search with pre_filter = {jurisdiction: {$in: [province, FEDERAL]}}."""
    FakeVectorStore.calls = []
    monkeypatch.setattr(agent_graph, "get_db_connection", lambda: object())
    monkeypatch.setattr(agent_graph, "get_embeddings", lambda: None)
    monkeypatch.setattr(agent_graph, "MongoDBAtlasVectorSearch", FakeVectorStore)

    state = {
        "user_intent": "ADVICE",
        "legal_issue": "My landlord raised my rent by 10 percent this year.",
        "jurisdiction": province,
    }
    result = agent_graph.research_node(state)

    assert len(FakeVectorStore.calls) == 1
    assert FakeVectorStore.calls[0]["pre_filter"] == {"jurisdiction": {"$in": [province, "FEDERAL"]}}
    assert FakeVectorStore.calls[0]["k"] == 3
    # The fake doc was turned into a research string, so the vector path really ran.
    assert result["relevant_laws"][0].startswith("Source: ontario_rta.html")
