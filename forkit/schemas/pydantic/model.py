"""
forkit.schemas.pydantic.model
──────────────────────────────
Pydantic v2 ModelPassport — same public interface as the dataclass version.

Provides JSON Schema generation and .model_dump() / .model_validate() support
in addition to the standard to_dict() / from_dict() interface.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from pydantic import BaseModel, Field, field_validator, model_validator
except ImportError as e:
    raise ImportError("pydantic>=2 is required for forkit.schemas.pydantic") from e

from ..enums import Architecture, LicenseType, PassportStatus, TaskType
from ...domain.identity import compute_id, validate_hash, validate_version
from ._types import _CreatorInfoModel, _ModelCapabilitiesModel, _TrainingDataRefModel


class ModelPassport(BaseModel):
    """Pydantic v2 ModelPassport — same public interface as the dataclass version."""

    model_config = {"arbitrary_types_allowed": True}

    # ── Frozen ────────────────────────────────────────────────────────────────
    passport_type: str = Field(default="model", frozen=True, exclude=False)

    # ── Required ──────────────────────────────────────────────────────────────
    name:         str
    version:      str
    creator:      _CreatorInfoModel | dict[str, Any]
    task_type:    TaskType
    architecture: Architecture

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

    # ── Model-specific ────────────────────────────────────────────────────────
    model_id:           str | None                  = None  # external ID (HuggingFace path etc.)
    base_model_id:      str | None                  = None  # passport ID of parent model for lineage
    artifact_files:     list[str]                   = Field(default_factory=list)
    quantization:       str | None                  = None
    base_model_name:    str | None                  = None  # human-readable parent name
    fine_tuning_method: str | None                  = None
    training_data:      list[_TrainingDataRefModel] = Field(default_factory=list)
    parameter_count:    int | None                  = None
    capabilities:       _ModelCapabilitiesModel     = Field(default_factory=_ModelCapabilitiesModel)
    usage_restrictions: list[str]                   = Field(default_factory=list)
    hub_url:            str | None                  = None
    paper_url:          str | None                  = None

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("artifact_hash", "parent_hash", mode="before")
    @classmethod
    def _val_hash(cls, v: Any) -> Any:
        return validate_hash(v)

    @field_validator("base_model_id", mode="before")
    @classmethod
    def _val_base_model_id(cls, v: Any) -> Any:
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

    @model_validator(mode="after")
    def _compute_id(self) -> "ModelPassport":
        if not self.id:
            creator = self.creator
            org  = creator.organization if hasattr(creator, "organization") else None
            name = creator.name         if hasattr(creator, "name")         else ""
            self.id = compute_id(
                passport_type = "model",
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
    def from_dict(cls, d: dict[str, Any]) -> "ModelPassport":
        d = dict(d)
        d.pop("passport_type", None)
        return cls.model_validate(d)
