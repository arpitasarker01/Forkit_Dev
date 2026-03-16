"""
forkit.domain
─────────────
Pure Python domain logic with zero external dependencies.

  identity   — deterministic passport ID derivation and field validation
  hashing    — HashEngine: SHA-256 fingerprinting for files, dirs, dicts, strings
  lineage    — LineageGraph: directed acyclic provenance graph
  integrity  — verify_passport_id, compute_metadata_hash
"""

from .hashing import HashEngine, engine as hash_engine
from .identity import compute_id, validate_hash, validate_version, to_json_safe
from .lineage import (
    LineageGraph,
    LineageNode,
    LineageEdge,
    NodeType,
    EdgeType,
)
from .integrity import verify_passport_id, compute_metadata_hash

__all__ = [
    "HashEngine",
    "hash_engine",
    "compute_id",
    "validate_hash",
    "validate_version",
    "to_json_safe",
    "LineageGraph",
    "LineageNode",
    "LineageEdge",
    "NodeType",
    "EdgeType",
    "verify_passport_id",
    "compute_metadata_hash",
]
