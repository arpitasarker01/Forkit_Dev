"""
forkit.schemas.model
────────────────────
ModelPassport — full identity and provenance document for an AI model.

Fields
──────
  Required:
    name, version, creator, task_type, architecture

  Provenance (from base):
    artifact_hash  — SHA-256 of the model weights/directory
    parent_hash    — SHA-256 of the parent artifact (for fine-tunes)

  External identity:
    model_id       — HuggingFace path or other external ID (not the passport id)

  Optional:
    quantization, base_model_name, fine_tuning_method, training_data,
    parameter_count, capabilities, usage_restrictions, hub_url, paper_url
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..domain.identity import validate_hash
from .base import BasePassport
from .enums import Architecture, TaskType
from .types import ModelCapabilities, TrainingDataRef


@dataclass(kw_only=True)
class ModelPassport(BasePassport):
    """Identity and provenance document for an AI model."""

    # frozen init=False field — set before __post_init__ runs
    passport_type: str = field(default="model", init=False)

    # ── Required ──────────────────────────────────────────────────────────────
    task_type:    TaskType | str
    architecture: Architecture | str

    # ── External ID ───────────────────────────────────────────────────────────
    model_id: str | None = None   # HuggingFace path etc., separate from passport.id

    # ── Artifact ──────────────────────────────────────────────────────────────
    artifact_files: list[str]  = field(default_factory=list)
    quantization:   str | None = None

    # ── Fine-tune lineage ─────────────────────────────────────────────────────
    base_model_id:      str | None = None   # passport ID of the parent model (for lineage)
    base_model_name:    str | None = None   # human-readable display name of the parent
    fine_tuning_method: str | None = None

    # ── Training ──────────────────────────────────────────────────────────────
    training_data:   list[TrainingDataRef | dict] = field(default_factory=list)
    parameter_count: int | None                   = None

    # ── Capabilities & restrictions ───────────────────────────────────────────
    capabilities:       ModelCapabilities | dict = field(default_factory=ModelCapabilities)
    usage_restrictions: list[str]                = field(default_factory=list)

    # ── Links ─────────────────────────────────────────────────────────────────
    hub_url:   str | None = None
    paper_url: str | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def __post_init__(self) -> None:
        # Coerce model-specific enums
        if isinstance(self.task_type, str):
            self.task_type = TaskType(self.task_type)
        if isinstance(self.architecture, str):
            self.architecture = Architecture(self.architecture)

        # Coerce nested objects
        if isinstance(self.capabilities, dict):
            self.capabilities = ModelCapabilities.from_dict(self.capabilities)
        self.training_data = [
            TrainingDataRef.from_dict(t) if isinstance(t, dict) else t
            for t in self.training_data
        ]

        # Validate lineage passport ID (must be a valid hash if provided)
        self.base_model_id = validate_hash(self.base_model_id)

        # Delegate to base: hash/version validation + id derivation
        super().__post_init__()

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ModelPassport":
        d = dict(d)
        d.pop("passport_type", None)
        if isinstance(d.get("creator"), dict):
            from .types import CreatorInfo
            d["creator"] = CreatorInfo.from_dict(d["creator"])
        if isinstance(d.get("capabilities"), dict):
            d["capabilities"] = ModelCapabilities.from_dict(d["capabilities"])
        if "training_data" in d:
            d["training_data"] = [
                TrainingDataRef.from_dict(t) if isinstance(t, dict) else t
                for t in d["training_data"]
            ]
        return cls(**d)
