"""Minimal LangChain quickstart for the forkit passport adapter."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from forkit.sdk import ForkitClient
from forkit.schemas import TaskType
from forkit_langchain import LangChainAdapter


def main() -> None:
    client = ForkitClient(registry_root=".forkit_langchain_demo")
    adapter = LangChainAdapter(client=client)
    creator = {"name": "Hamza", "organization": "ForkIt"}

    model_id = client.models.register(
        name="langchain-demo-model",
        version="1.0.0",
        task_type=TaskType.TEXT_GENERATION,
        architecture="transformer",
        creator=creator,
    )

    agent = create_agent(
        model=FakeListChatModel(responses=["hello from forkit"]),
        system_prompt="Be concise.",
        name="demo-agent",
    )
    bound = adapter.bind_runnable(
        agent,
        name="demo-agent",
        version="1.0.0",
        model_id=model_id,
        creator=creator,
        system_prompt="Be concise.",
    )

    result = bound.invoke({"messages": [{"role": "user", "content": "say hi"}]})

    print("passport_id:", bound.passport_id)
    print("last_message:", result["messages"][-1].content)
    print("runtime_counts:", bound.runtime_summary()["counts"])


if __name__ == "__main__":
    main()
