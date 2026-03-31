"""
forkit.schemas.agent
────────────────────
AgentPassport — full identity and provenance document for an AI agent.

Fields
──────
  Required:
    name, version, creator, model_id, task_type, architecture

  model_id is the full 64-char passport ID of the underlying ModelPassport,
  not an external model path.  This creates a hard link between agent and model
  that can be verified without a registry.

  Provenance (from base):
    artifact_hash  — SHA-256 of the agent's config bundle
    parent_hash    — SHA-256 of the parent agent's config (for forks)

  Optional:
    role, capabilities, system_prompt, temperature, top_p, max_tokens,
    tools, memory_type, memory_config, parent_agent_name, fork_reason,
    deployment_env, endpoint_hash
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..domain.identity import validate_hash
from .base import BasePassport
from .enums import AgentArchitecture, AgentRole, AgentTaskType, MemoryType
from .types import AgentCapabilities, SystemPromptRecord, ToolRef


@dataclass(kw_only=True)
class AgentPassport(BasePassport):
    """Identity and provenance document for an AI agent."""

    passport_type: str = field(default="agent", init=False)

    # ── Required ──────────────────────────────────────────────────────────────
    model_id:     str                    # full 64-char passport ID of the base model
    task_type:    AgentTaskType | str
    architecture: AgentArchitecture | str

    # ── Model binding ─────────────────────────────────────────────────────────
    model_version: str | None = None

    # ── Identity / role ───────────────────────────────────────────────────────
    role:         AgentRole | str       = AgentRole.ASSISTANT
    capabilities: AgentCapabilities | dict = field(default_factory=AgentCapabilities)

    # ── Configuration fingerprints ────────────────────────────────────────────
    system_prompt: SystemPromptRecord | dict | None = None
    temperature:   float | None = None
    top_p:         float | None = None
    max_tokens:    int | None   = None

    # ── Tools and memory ──────────────────────────────────────────────────────
    tools:         list[ToolRef | dict] = field(default_factory=list)
    memory_type:   MemoryType | str     = MemoryType.NONE
    memory_config: dict[str, Any]       = field(default_factory=dict)

    # ── Fork lineage ──────────────────────────────────────────────────────────
    parent_agent_id:   str | None = None   # passport ID of the parent agent (for lineage)
    parent_agent_name: str | None = None   # human-readable display name of the parent
    fork_reason:       str | None = None

    # ── Deployment ────────────────────────────────────────────────────────────
    deployment_env: str | None = None
    endpoint_hash:  str | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def __post_init__(self) -> None:
        # Coerce agent-specific enums
        if isinstance(self.task_type, str):
            self.task_type = AgentTaskType(self.task_type)
        if isinstance(self.architecture, str):
            self.architecture = AgentArchitecture(self.architecture)
        if isinstance(self.role, str):
            self.role = AgentRole(self.role)
        if isinstance(self.memory_type, str):
            self.memory_type = MemoryType(self.memory_type)

        # Coerce nested objects
        if isinstance(self.capabilities, dict):
            self.capabilities = AgentCapabilities.from_dict(self.capabilities)
        if isinstance(self.system_prompt, dict):
            self.system_prompt = SystemPromptRecord.from_dict(self.system_prompt)
        self.tools = [
            ToolRef.from_dict(t) if isinstance(t, dict) else t
            for t in self.tools
        ]

        # Validate lineage and deployment hash fields
        self.parent_agent_id = validate_hash(self.parent_agent_id)
        self.endpoint_hash   = validate_hash(self.endpoint_hash)

        # Delegate to base
        super().__post_init__()

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AgentPassport:
        d = dict(d)
        d.pop("passport_type", None)
        if isinstance(d.get("creator"), dict):
            from .types import CreatorInfo
            d["creator"] = CreatorInfo.from_dict(d["creator"])
        if isinstance(d.get("capabilities"), dict):
            d["capabilities"] = AgentCapabilities.from_dict(d["capabilities"])
        if isinstance(d.get("system_prompt"), dict):
            d["system_prompt"] = SystemPromptRecord.from_dict(d["system_prompt"])
        if "tools" in d:
            d["tools"] = [
                ToolRef.from_dict(t) if isinstance(t, dict) else t
                for t in d["tools"]
            ]
        return cls(**d)
