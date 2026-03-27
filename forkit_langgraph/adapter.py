"""Minimal LangGraph adapter for building and registering agent passports."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from forkit.domain.hashing import HashEngine
from forkit.sdk import ForkitClient
from forkit.schemas import (
    AgentArchitecture,
    AgentPassport,
    AgentTaskType,
    CreatorInfo,
    SystemPromptRecord,
)


class LangGraphPassportAdapter:
    """
    Minimal bridge between LangGraph-style configs and forkit agent passports.

    The current skeleton intentionally avoids importing LangGraph at runtime.
    Callers pass a serializable ``graph_spec`` dict, which becomes the stable
    artifact hash for the derived agent passport unless an explicit
    ``artifact_hash`` is provided.
    """

    def __init__(
        self,
        client: ForkitClient | None = None,
        registry_root: str | Path = "~/.forkit/registry",
    ) -> None:
        self.client = client or ForkitClient(registry_root=registry_root)

    def hash_graph(self, graph_spec: Mapping[str, Any]) -> str:
        """Derive a stable hash for a LangGraph-style configuration payload."""
        return HashEngine.hash_config(dict(graph_spec))

    def build_agent_passport(
        self,
        *,
        name: str,
        version: str,
        model_id: str,
        creator: dict[str, Any] | CreatorInfo,
        graph_spec: Mapping[str, Any] | None = None,
        task_type: str | AgentTaskType = AgentTaskType.OTHER,
        architecture: str | AgentArchitecture = AgentArchitecture.REACT,
        system_prompt: str | SystemPromptRecord | dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AgentPassport:
        """Build an AgentPassport from a LangGraph-oriented configuration."""
        creator_payload = self._normalise_creator(creator)
        system_prompt_payload = self._normalise_system_prompt(system_prompt)

        artifact_hash = kwargs.pop("artifact_hash", None)
        metadata_payload = dict(metadata or {})

        if graph_spec is not None:
            graph_hash = self.hash_graph(graph_spec)
            if artifact_hash is None:
                artifact_hash = graph_hash
            langgraph_metadata = dict(metadata_payload.get("langgraph") or {})
            langgraph_metadata["graph_hash"] = graph_hash
            metadata_payload["langgraph"] = langgraph_metadata

        return AgentPassport(
            name=name,
            version=version,
            model_id=model_id,
            task_type=task_type,
            architecture=architecture,
            creator=creator_payload,
            system_prompt=system_prompt_payload,
            artifact_hash=artifact_hash,
            metadata=metadata_payload or None,
            **kwargs,
        )

    def register_agent(self, **kwargs: Any) -> str:
        """Build and persist an AgentPassport derived from LangGraph inputs."""
        passport = self.build_agent_passport(**kwargs)
        return self.client.register_agent(passport)

    @staticmethod
    def _normalise_creator(creator: dict[str, Any] | CreatorInfo) -> dict[str, Any]:
        if isinstance(creator, CreatorInfo):
            return creator.to_dict()
        return CreatorInfo.from_dict(creator).to_dict()

    @staticmethod
    def _normalise_system_prompt(
        system_prompt: str | SystemPromptRecord | dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        if system_prompt is None:
            return None
        if isinstance(system_prompt, str):
            return SystemPromptRecord(
                hash=HashEngine.hash_system_prompt(system_prompt),
                length_chars=len(system_prompt),
            ).to_dict()
        if isinstance(system_prompt, SystemPromptRecord):
            return system_prompt.to_dict()
        return dict(system_prompt)


LangGraphAdapter = LangGraphPassportAdapter
