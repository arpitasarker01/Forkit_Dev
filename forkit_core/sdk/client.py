"""
Python SDK — high-level client for forkit-core.

Designed for programmatic use in agent frameworks, pipelines, and notebooks.
The SDK wraps the local registry and exposes a clean, typed interface.

Example:
    from forkit_core.sdk import ForkitClient
    from forkit_core.schemas import ModelPassport, CreatorInfo

    client = ForkitClient()

    model_id = client.models.register(
        name="my-model",
        version="1.0.0",
        architecture="transformer",
        creator={"name": "Hamza", "organization": "ForkIt"},
        license="Apache-2.0",
    )

    passport = client.models.get(model_id)
    print(passport.name)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..hashing import HashEngine
from ..lineage import LineageGraph, NodeType
from ..registry import LocalRegistry
from ..schemas import AgentPassport, CreatorInfo, ModelPassport, PassportStatus


class ModelClient:
    """Fluent interface for ModelPassport operations."""

    def __init__(self, registry: LocalRegistry):
        self._reg = registry

    def register(
        self,
        name: str,
        version: str,
        architecture: str,
        creator: dict[str, Any] | CreatorInfo,
        **kwargs: Any,
    ) -> str:
        """Register a model passport. Returns the passport ID."""
        if isinstance(creator, dict):
            creator = CreatorInfo(**creator)
        passport = ModelPassport(
            name=name,
            version=version,
            architecture=architecture,
            creator=creator,
            **kwargs,
        )
        return self._reg.register_model(passport)

    def register_passport(self, passport: ModelPassport) -> str:
        return self._reg.register_model(passport)

    def get(self, passport_id: str) -> ModelPassport | None:
        return self._reg.get_model(passport_id)

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        return self._reg.list(passport_type="model", status=status)

    def delete(self, passport_id: str) -> bool:
        return self._reg.delete(passport_id)

    def hash_weights_file(self, path: str | Path) -> str:
        """Compute SHA-256 of a weights file for use as weights_hash."""
        return HashEngine.hash_file(path)

    def hash_weights_dir(
        self,
        path: str | Path,
        extensions: list[str] | None = None,
    ) -> str:
        """Compute a stable hash over a directory of weight files."""
        return HashEngine.hash_directory(path, extensions=extensions)


class AgentClient:
    """Fluent interface for AgentPassport operations."""

    def __init__(self, registry: LocalRegistry):
        self._reg = registry

    def register(
        self,
        name: str,
        version: str,
        model_id: str,
        creator: dict[str, Any] | CreatorInfo,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Register an agent passport. Returns the passport ID."""
        if isinstance(creator, dict):
            creator = CreatorInfo(**creator)

        extra: dict[str, Any] = {}
        if system_prompt is not None:
            from ..schemas.agent_passport import SystemPromptRecord
            extra["system_prompt"] = SystemPromptRecord(
                hash=HashEngine.system_prompt_hash(system_prompt),
                length_chars=len(system_prompt),
            )

        passport = AgentPassport(
            name=name,
            version=version,
            model_id=model_id,
            creator=creator,
            **extra,
            **kwargs,
        )
        return self._reg.register_agent(passport)

    def register_passport(self, passport: AgentPassport) -> str:
        return self._reg.register_agent(passport)

    def get(self, passport_id: str) -> AgentPassport | None:
        return self._reg.get_agent(passport_id)

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        return self._reg.list(passport_type="agent", status=status)

    def delete(self, passport_id: str) -> bool:
        return self._reg.delete(passport_id)

    def hash_config(self, config: dict[str, Any]) -> str:
        """Hash an agent config dict for use as config_hash."""
        return HashEngine.config_hash(config)

    def hash_system_prompt(self, prompt_text: str) -> str:
        return HashEngine.system_prompt_hash(prompt_text)


class LineageClient:
    """Read-only access to the lineage graph."""

    def __init__(self, registry: LocalRegistry):
        self._reg = registry

    @property
    def graph(self) -> LineageGraph:
        return self._reg.lineage

    def ancestors(self, passport_id: str) -> list[dict[str, Any]]:
        return [n.to_dict() for n in self.graph.ancestors(passport_id)]

    def descendants(self, passport_id: str) -> list[dict[str, Any]]:
        return [n.to_dict() for n in self.graph.descendants(passport_id)]

    def models(self) -> list[dict[str, Any]]:
        return [n.to_dict() for n in self.graph.nodes_by_type(NodeType.MODEL)]

    def agents(self) -> list[dict[str, Any]]:
        return [n.to_dict() for n in self.graph.nodes_by_type(NodeType.AGENT)]

    def to_dict(self) -> dict[str, Any]:
        return self.graph.to_dict()


class ForkitClient:
    """
    Top-level SDK client for forkit-core.

    All operations go through this class. The underlying registry is
    lazily initialized on first use.

    Args:
        registry_root: Path to the local registry directory.
                       Defaults to ~/.forkit/registry
    """

    def __init__(self, registry_root: str | Path = "~/.forkit/registry"):
        self._registry = LocalRegistry(root=registry_root)
        self.models = ModelClient(self._registry)
        self.agents = AgentClient(self._registry)
        self.lineage = LineageClient(self._registry)

    def search(self, query: str) -> list[dict[str, Any]]:
        """Full-text search across all passport names and creators."""
        return self._registry.search(query)

    def get(self, passport_id: str) -> ModelPassport | AgentPassport | None:
        """Get any passport by ID, regardless of type."""
        return self._registry.get(passport_id)

    def delete(self, passport_id: str) -> bool:
        """Delete a passport by ID."""
        return self._registry.delete(passport_id)

    def verify(self, passport_id: str) -> dict[str, Any]:
        """Verify the integrity of a stored passport."""
        return self._registry.verify_passport(passport_id)

    def stats(self) -> dict[str, Any]:
        """Return registry statistics."""
        return self._registry.stats()

    def rebuild_index(self) -> int:
        """Rebuild the SQLite index from JSON files."""
        return self._registry.rebuild_index()

    @property
    def registry(self) -> LocalRegistry:
        return self._registry
