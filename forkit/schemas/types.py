"""
forkit.schemas.types
────────────────────
Supporting dataclasses used inside ModelPassport and AgentPassport.

All classes:
  - use @dataclass(kw_only=True) for clean keyword-only construction
  - provide to_dict()  → JSON-safe dict
  - provide from_dict() → reconstructs from a plain dict (ignores unknown keys)
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any


@dataclass(kw_only=True)
class CreatorInfo:
    """Who built or owns this passport."""

    name:         str
    organization: str | None = None
    email:        str | None = None
    url:          str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CreatorInfo:
        known = {"name", "organization", "email", "url"}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass(kw_only=True)
class TrainingDataRef:
    """Lightweight reference to a training dataset."""

    name:         str
    url:          str | None = None
    hash:         str | None = None
    size_tokens:  int | None = None
    cutoff_date:  str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TrainingDataRef:
        known = {"name", "url", "hash", "size_tokens", "cutoff_date"}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass(kw_only=True)
class ModelCapabilities:
    """What the model can do at runtime."""

    modalities:                list[str]         = field(default_factory=list)
    context_length:            int | None        = None
    supports_function_calling: bool              = False
    supports_streaming:        bool              = False
    languages:                 list[str]         = field(default_factory=list)
    benchmark_scores:          dict[str, float]  = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ModelCapabilities:
        known = {
            "modalities", "context_length", "supports_function_calling",
            "supports_streaming", "languages", "benchmark_scores",
        }
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass(kw_only=True)
class ToolRef:
    """Reference to an external tool the agent can call."""

    name:        str
    version:     str | None = None
    description: str | None = None
    source_url:  str | None = None
    hash:        str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ToolRef:
        known = {"name", "version", "description", "source_url", "hash"}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass(kw_only=True)
class AgentCapabilities:
    """What the agent supports at runtime."""

    max_iterations:      int | None  = None
    supports_streaming:  bool        = False
    supports_multi_turn: bool        = True
    supports_tool_use:   bool        = False
    languages:           list[str]   = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AgentCapabilities:
        known = {
            "max_iterations", "supports_streaming",
            "supports_multi_turn", "supports_tool_use", "languages",
        }
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass(kw_only=True)
class SystemPromptRecord:
    """Non-reversible audit record of a system prompt."""

    hash:          str
    length_chars:  int
    template_id:   str | None = None
    redacted:      bool       = False

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SystemPromptRecord:
        known = {"hash", "length_chars", "template_id", "redacted"}
        return cls(**{k: v for k, v in d.items() if k in known})
