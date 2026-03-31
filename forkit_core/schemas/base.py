"""
Base schema — shared fields and ID-derivation logic for all passport types.

ID contract
-----------
Every passport has a deterministic SHA-256 `id` computed from a canonical
set of fields.  Priority:

  1. If `artifact_hash` is set → id = sha256(artifact_hash + "|" + canonical)
     Two passports with the same name/version but different artifacts get
     different IDs — correct behaviour for provenance tracking.
  2. Otherwise                 → id = sha256(canonical)
     Useful during authoring before an artifact exists.

IDs are stable across registries as long as the same artifact is used,
and automatically change when the artifact changes.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# ──────────────────────────────────────────────────────────────────────────────
# Shared enumerations
# ──────────────────────────────────────────────────────────────────────────────

class PassportStatus(str, Enum):
    DRAFT       = "draft"
    ACTIVE      = "active"
    DEPRECATED  = "deprecated"
    REVOKED     = "revoked"


class LicenseType(str, Enum):
    APACHE_2    = "Apache-2.0"
    MIT         = "MIT"
    GPL_3       = "GPL-3.0"
    CC_BY       = "CC-BY-4.0"
    CC_BY_NC    = "CC-BY-NC-4.0"
    LLAMA_3     = "llama3"
    GEMMA       = "gemma"
    PROPRIETARY = "proprietary"
    OTHER       = "other"


# ──────────────────────────────────────────────────────────────────────────────
# Sub-models
# ──────────────────────────────────────────────────────────────────────────────

class CreatorInfo(BaseModel):
    """Who built or owns this model / agent."""

    name: str         = Field(..., description="Individual or team name")
    organization: str | None = Field(None, description="Company or institution")
    email: str | None = Field(None, description="Contact email — never used as an ID")
    url: str | None   = Field(None, description="Homepage, profile, or repo URL")

    model_config = {"extra": "forbid"}


# ──────────────────────────────────────────────────────────────────────────────
# Base passport
# ──────────────────────────────────────────────────────────────────────────────

class BasePassport(BaseModel):
    """
    Common identity and provenance fields shared by ModelPassport and AgentPassport.

    Required fields
    ───────────────
    name            Human-readable display name.
    version         Semantic version string ("1.0.0").
    creator         Who created this passport / artifact.

    Provenance fields
    ─────────────────
    artifact_hash   SHA-256 of the primary artifact (weights file, agent bundle).
                    When set, the passport `id` is derived from it — changing
                    the artifact always produces a new, distinct passport ID.
    parent_hash     SHA-256 of the *artifact* this was derived from.
                    Enables hash-chain provenance without requiring the parent
                    to be registered in the same registry.
    license         Distribution or usage license.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    id: str = Field(
        default="",
        description="Deterministic SHA-256 passport fingerprint. Auto-computed.",
    )
    name: str = Field(..., description="Human-readable display name")
    version: str = Field(
        ...,
        description="Semantic version of this passport record, e.g. '1.0.0'",
        examples=["1.0.0", "2.3.1"],
    )
    description: str | None = Field(None, description="Optional longer description")

    # ── Provenance (hash chain) ───────────────────────────────────────────────
    artifact_hash: str | None = Field(
        None,
        description=(
            "SHA-256 hex digest of the primary artifact file or bundle "
            "(model weights, agent config tarball, etc.). "
            "When set, this value is mixed into the passport `id`."
        ),
    )
    parent_hash: str | None = Field(
        None,
        description=(
            "SHA-256 hex digest of the *parent* artifact this was derived from. "
            "Fine-tuned model → hash of base model weights. "
            "Forked agent    → hash of parent agent config bundle. "
            "Enables trustless hash-chain provenance without a central registry."
        ),
    )

    # ── Authorship & legal ────────────────────────────────────────────────────
    creator: CreatorInfo = Field(..., description="Author / owning entity")
    license: LicenseType = Field(
        LicenseType.OTHER,
        description="Distribution or usage license",
    )
    license_url: str | None = Field(None, description="Full license text URL")

    # ── Registry metadata ─────────────────────────────────────────────────────
    status: PassportStatus = Field(
        PassportStatus.DRAFT,
        description="Lifecycle status of this passport",
    )
    tags: list[str] = Field(default_factory=list, description="Free-form labels")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value extension bag",
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("artifact_hash", "parent_hash", mode="before")
    @classmethod
    def _validate_hash(cls, v: str | None) -> str | None:
        """Hashes must be 64-character lowercase hex strings when provided."""
        if v is None:
            return v
        v = str(v).lower().strip()
        if len(v) != 64 or not all(c in "0123456789abcdef" for c in v):
            raise ValueError(
                f"Hash must be a 64-char lowercase hex string (SHA-256). Got: {v!r}"
            )
        return v

    @field_validator("version", mode="before")
    @classmethod
    def _validate_version(cls, v: str) -> str:
        parts = str(v).split(".")
        if not (2 <= len(parts) <= 3):
            raise ValueError(
                f"Version must be semver (e.g. '1.0' or '1.0.0'). Got: {v!r}"
            )
        return v

    @model_validator(mode="after")
    def _assign_id(self) -> BasePassport:
        if not self.id:
            self.id = self._compute_id()
        return self

    # ── ID derivation ─────────────────────────────────────────────────────────

    def _compute_id(self) -> str:
        """
        Deterministic SHA-256 passport ID.

        Canonical fields are always included.  When artifact_hash is present
        it is prepended so different artifacts yield different IDs even when
        name / version / creator are identical.
        """
        canonical = {
            "passport_type": getattr(self, "passport_type", self.__class__.__name__),
            "name":          self.name,
            "version":       self.version,
            "creator_name":  self.creator.name,
            "creator_org":   self.creator.organization,
        }
        payload = json.dumps(canonical, sort_keys=True)
        if self.artifact_hash:
            payload = self.artifact_hash + "|" + payload
        return hashlib.sha256(payload.encode()).hexdigest()

    # ── Serialisation helpers ─────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BasePassport:
        return cls(**data)

    def short_id(self, length: int = 12) -> str:
        """Return a short human-readable prefix of the passport ID."""
        return self.id[:length]

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name={self.name!r} version={self.version!r} "
            f"id={self.short_id()}...>"
        )
