"""
forkit.domain.integrity
───────────────────────
Passport integrity helpers: verify stored IDs and compute stable metadata hashes.

These functions are schema-agnostic — they work on plain dicts so they can be
called without instantiating a passport object.
"""

from __future__ import annotations

from typing import Any

from .hashing import HashEngine
from .identity import compute_id

__all__ = [
    "verify_passport_id",
    "compute_metadata_hash",
]


def verify_passport_id(passport_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Verify that a passport dict's stored `id` is consistent with its content.

    Recomputes the ID from: passport_type, name, version, creator, artifact_hash.
    Returns a result dict with keys:
      - valid       (bool)
      - stored_id   (str)
      - derived_id  (str)
      - reason      ("ok" | "id_mismatch" | "missing_id")
    """
    stored_id = passport_dict.get("id", "")
    if not stored_id:
        return {
            "valid":      False,
            "stored_id":  stored_id,
            "derived_id": "",
            "reason":     "missing_id",
        }

    creator = passport_dict.get("creator") or {}
    if not isinstance(creator, dict):
        # Handle CreatorInfo objects that were passed as objects
        creator_name = getattr(creator, "name", "")
        creator_org  = getattr(creator, "organization", None)
    else:
        creator_name = creator.get("name", "")
        creator_org  = creator.get("organization")

    derived_id = compute_id(
        passport_type = passport_dict.get("passport_type", ""),
        name          = passport_dict.get("name", ""),
        version       = passport_dict.get("version", ""),
        creator_name  = creator_name,
        creator_org   = creator_org,
        artifact_hash = passport_dict.get("artifact_hash"),
    )

    match = derived_id == stored_id
    return {
        "valid":      match,
        "stored_id":  stored_id,
        "derived_id": derived_id,
        "reason":     "ok" if match else "id_mismatch",
    }


def compute_metadata_hash(passport_dict: dict[str, Any]) -> str:
    """
    Compute a stable hash of a passport's substantive fields.

    Excludes: id, created_at, updated_at.
    Use this to detect whether a passport's content has changed.
    """
    return HashEngine.hash_metadata(passport_dict)
