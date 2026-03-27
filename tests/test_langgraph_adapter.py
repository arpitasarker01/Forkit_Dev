"""Tests for the LangGraph integration skeleton."""

from forkit.sdk import ForkitClient
from forkit.schemas import AgentTaskType, TaskType
from forkit_langgraph import LangGraphAdapter


CREATOR = {"name": "Hamza", "organization": "ForkIt"}


class TestLangGraphAdapter:
    def test_register_agent_uses_graph_hash_as_artifact_hash(self, tmp_path):
        client = ForkitClient(registry_root=tmp_path / "registry")
        adapter = LangGraphAdapter(client=client)

        model_id = client.models.register(
            name="demo-model",
            version="1.0.0",
            task_type=TaskType.TEXT_GENERATION,
            architecture="transformer",
            creator=CREATOR,
        )
        graph_spec = {
            "entrypoint": "router",
            "nodes": ["router", "writer"],
            "edges": [["router", "writer"]],
        }

        agent_id = adapter.register_agent(
            name="writer-graph",
            version="1.0.0",
            model_id=model_id,
            creator=CREATOR,
            task_type=AgentTaskType.OTHER,
            system_prompt="Draft the response before sending it.",
            graph_spec=graph_spec,
        )

        agent = client.agents.get(agent_id)
        graph_hash = adapter.hash_graph(graph_spec)

        assert agent is not None
        assert agent.artifact_hash == graph_hash
        assert agent.metadata["langgraph"]["graph_hash"] == graph_hash
        assert client.verify(agent_id)["valid"] is True

    def test_graph_spec_changes_agent_id(self, tmp_path):
        adapter = LangGraphAdapter(registry_root=tmp_path / "registry")

        graph_a = {"nodes": ["router", "search"], "edges": [["router", "search"]]}
        graph_b = {"nodes": ["router", "summarize"], "edges": [["router", "summarize"]]}

        passport_a = adapter.build_agent_passport(
            name="search-graph",
            version="1.0.0",
            model_id="m" * 64,
            creator=CREATOR,
            graph_spec=graph_a,
        )
        passport_b = adapter.build_agent_passport(
            name="search-graph",
            version="1.0.0",
            model_id="m" * 64,
            creator=CREATOR,
            graph_spec=graph_b,
        )

        assert passport_a.artifact_hash != passport_b.artifact_hash
        assert passport_a.id != passport_b.id
