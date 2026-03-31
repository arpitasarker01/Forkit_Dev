"""
forkit.schemas.pydantic._types
──────────────────────────────
Shared Pydantic v2 models for nested objects used in both ModelPassport
and AgentPassport.

Extracted here to avoid duplication between pydantic/model.py and
pydantic/agent.py — the dataclass counterparts live in schemas/types.py.
"""

from __future__ import annotations

try:
    from pydantic import BaseModel, Field
except ImportError as e:
    raise ImportError("pydantic>=2 is required for forkit.schemas.pydantic") from e


class _CreatorInfoModel(BaseModel):
    name:         str
    organization: str | None = None
    email:        str | None = None
    url:          str | None = None


class _TrainingDataRefModel(BaseModel):
    name:         str
    url:          str | None = None
    hash:         str | None = None
    size_tokens:  int | None = None
    cutoff_date:  str | None = None


class _ModelCapabilitiesModel(BaseModel):
    modalities:                list[str]         = Field(default_factory=list)
    context_length:            int | None        = None
    supports_function_calling: bool              = False
    supports_streaming:        bool              = False
    languages:                 list[str]         = Field(default_factory=list)
    benchmark_scores:          dict[str, float]  = Field(default_factory=dict)


class _AgentCapabilitiesModel(BaseModel):
    max_iterations:      int | None  = None
    supports_streaming:  bool        = False
    supports_multi_turn: bool        = True
    supports_tool_use:   bool        = False
    languages:           list[str]   = Field(default_factory=list)


class _ToolRefModel(BaseModel):
    name:        str
    version:     str | None = None
    description: str | None = None
    source_url:  str | None = None
    hash:        str | None = None


class _SystemPromptRecordModel(BaseModel):
    hash:         str
    length_chars: int
    template_id:  str | None = None
    redacted:     bool       = False
