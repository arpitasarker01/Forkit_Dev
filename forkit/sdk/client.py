"""
forkit.sdk.client
─────────────────
High-level Python SDK — thin wrapper around LocalRegistry with convenience
methods for common workflows.

MVP scope
─────────
  - register a model or agent passport
  - look up a passport by ID
  - list / search passports
  - retrieve lineage for a passport
  - verify passport integrity

Future (post-MVP)
─────────────────
  - Remote registry HTTP client (same interface, different transport)
  - Batch registration
  - Webhook / event hooks
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.hashing import HashEngine
from ..domain.integrity import verify_passport_id
from ..domain.lineage import LineageGraph, LineageNode
from ..registry.local import LocalRegistry
from ..schemas import AgentPassport, ModelPassport


class ForkitClient:
    """
    Convenience SDK for forkit-core.

    Usage::

        from forkit.sdk import ForkitClient
        from forkit.schemas import ModelPassport, TaskType, Architecture

        client = ForkitClient()
        passport = ModelPassport(
            name         = "my-model",
            version      = "1.0.0",
            task_type    = TaskType.TEXT_GENERATION,
            architecture = Architecture.DECODER_ONLY,
            creator      = {"name": "Alice", "organization": "Acme"},
        )
        passport_id = client.register_model(passport)
        retrieved   = client.get(passport_id)
    """

    def __init__(self, registry_root: str | Path = "~/.forkit/registry") -> None:
        self._registry = LocalRegistry(root=registry_root)
        self._hash     = HashEngine()

    # ── Registration ───────────────────────────────────────────────────────────

    def register_model(self, passport: ModelPassport) -> str:
        """Register a ModelPassport. Returns its ID."""
        return self._registry.register_model(passport)

    def register_agent(self, passport: AgentPassport) -> str:
        """Register an AgentPassport. Returns its ID."""
        return self._registry.register_agent(passport)

    # ── Retrieval ──────────────────────────────────────────────────────────────

    def get(self, passport_id: str) -> ModelPassport | AgentPassport | None:
        return self._registry.get(passport_id)

    def get_model(self, passport_id: str) -> ModelPassport | None:
        return self._registry.get_model(passport_id)

    def get_agent(self, passport_id: str) -> AgentPassport | None:
        return self._registry.get_agent(passport_id)

    # ── Queries ────────────────────────────────────────────────────────────────

    def list(
        self,
        passport_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        return self._registry.list(passport_type=passport_type, status=status)

    def search(self, query: str) -> list[dict[str, Any]]:
        return self._registry.search(query)

    def stats(self) -> dict[str, Any]:
        return self._registry.stats()

    # ── Lineage ────────────────────────────────────────────────────────────────

    def ancestors(self, passport_id: str) -> list[LineageNode]:
        return self._registry.lineage.ancestors(passport_id)

    def descendants(self, passport_id: str) -> list[LineageNode]:
        return self._registry.lineage.descendants(passport_id)

    # ── Integrity ──────────────────────────────────────────────────────────────

    def verify(self, passport_id: str) -> dict[str, Any]:
        return self._registry.verify_passport(passport_id)

    def hash_artifact(self, path: str | Path) -> str:
        return self._hash.hash_artifact(path)

    def hash_config(self, config: dict[str, Any]) -> str:
        return self._hash.hash_config(config)

    # ── Maintenance ────────────────────────────────────────────────────────────

    def rebuild_index(self) -> int:
        return self._registry.rebuild_index()

    def delete(self, passport_id: str) -> bool:
        return self._registry.delete(passport_id)
