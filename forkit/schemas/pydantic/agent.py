"""
forkit.schemas.pydantic.agent
──────────────────────────────
Pydantic v2 AgentPassport — same public interface as the dataclass version.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from pydantic import BaseModel, Field, field_validator, model_validator
except ImportError as e:
    raise ImportError("pydantic>=2 is required for forkit.schemas.pydantic") from e

from ...domain.identity import compute_id, validate_hash, validate_version
from ..enums import (
    AgentArchitecture,
    AgentRole,
    AgentTaskType,
    LicenseType,
    MemoryType,
    PassportStatus,
)
from ._types import (
    _AgentCapabilitiesModel,
    _CreatorInfoModel,
    _SystemPromptRecordModel,
    _ToolRefModel,
)


class AgentPassport(BaseModel):
    """Pydantic v2 AgentPassport — same public interface as the dataclass version."""

    model_config = {"arbitrary_types_allowed": True}

    passport_type: str = Field(default="agent", frozen=True, exclude=False)

    # ── Required ──────────────────────────────────────────────────────────────
    name:         str
    version:      str
    creator:      _CreatorInfoModel | dict[str, Any]
    model_id:     str                # full 64-char passport ID of the base model
    task_type:    AgentTaskType
    architecture: AgentArchitecture

    # ── Provenance ────────────────────────────────────────────────────────────
    artifact_hash: str | None = None
    parent_hash:   str | None = None

    # ── Legal ─────────────────────────────────────────────────────────────────
    license:     LicenseType = LicenseType.OTHER
    license_url: str | None  = None

    # ── Identity (auto-computed) ───────────────────────────────────────────────
    id:          str        = Field(default="")
    description: str | None = None

    # ── Registry ──────────────────────────────────────────────────────────────
    status:   PassportStatus = PassportStatus.DRAFT
    tags:     list[str]      = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # ── Agent-specific ────────────────────────────────────────────────────────
    model_version:      str | None                      = None
    role:               AgentRole                       = AgentRole.ASSISTANT
    capabilities:       _AgentCapabilitiesModel         = Field(default_factory=_AgentCapabilitiesModel)
    system_prompt:      _SystemPromptRecordModel | None = None
    temperature:        float | None                    = None
    top_p:              float | None                    = None
    max_tokens:         int | None                      = None
    tools:              list[_ToolRefModel]              = Field(default_factory=list)
    memory_type:        MemoryType                      = MemoryType.NONE
    memory_config:      dict[str, Any]                  = Field(default_factory=dict)
    parent_agent_id:    str | None                      = None  # passport ID of parent agent
    parent_agent_name:  str | None                      = None  # human-readable parent name
    fork_reason:        str | None                      = None
    deployment_env:     str | None                      = None
    endpoint_hash:      str | None                      = None  # hash of deployment endpoint config

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("artifact_hash", "parent_hash", "endpoint_hash", mode="before")
    @classmethod
    def _val_hash(cls, v: Any) -> Any:
        return validate_hash(v)

    @field_validator("parent_agent_id", mode="before")
    @classmethod
    def _val_parent_agent_id(cls, v: Any) -> Any:
        return validate_hash(v)  # must be a passport ID if provided

    @field_validator("version", mode="before")
    @classmethod
    def _val_version(cls, v: Any) -> Any:
        return validate_version(str(v))

    @field_validator("creator", mode="before")
    @classmethod
    def _coerce_creator(cls, v: Any) -> Any:
        if isinstance(v, dict):
            return _CreatorInfoModel(**{k: vv for k, vv in v.items()
                                        if k in {"name", "organization", "email", "url"}})
        return v

    @field_validator("tools", mode="before")
    @classmethod
    def _coerce_tools(cls, v: Any) -> Any:
        return [_ToolRefModel(**t) if isinstance(t, dict) else t for t in (v or [])]

    @field_validator("system_prompt", mode="before")
    @classmethod
    def _coerce_spr(cls, v: Any) -> Any:
        if isinstance(v, dict):
            return _SystemPromptRecordModel(**v)
        return v

    @model_validator(mode="after")
    def _compute_id(self) -> AgentPassport:
        if not self.id:
            creator = self.creator
            org  = creator.organization if hasattr(creator, "organization") else None
            name = creator.name         if hasattr(creator, "name")         else ""
            self.id = compute_id(
                passport_type = "agent",
                name          = self.name,
                version       = self.version,
                creator_name  = name,
                creator_org   = org,
                artifact_hash = self.artifact_hash,
            )
        return self

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        import json
        return json.loads(self.model_dump_json())

    def short_id(self, length: int = 12) -> str:
        return self.id[:length]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AgentPassport:
        d = dict(d)
        d.pop("passport_type", None)
        return cls.model_validate(d)
