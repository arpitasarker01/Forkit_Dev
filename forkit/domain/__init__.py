"""
forkit.domain
─────────────
Pure Python domain logic with zero external dependencies.

  identity   — deterministic passport ID derivation and field validation
  hashing    — HashEngine: SHA-256 fingerprinting for files, dirs, dicts, strings
  lineage    — LineageGraph: directed acyclic provenance graph
  integrity  — verify_passport_id, compute_metadata_hash
"""

from .hashing import HashEngine
from .hashing import engine as hash_engine
from .identity import compute_id, to_json_safe, validate_hash, validate_version
from .integrity import compute_metadata_hash, verify_passport_id
from .lineage import (
    EdgeType,
    LineageEdge,
    LineageGraph,
    LineageNode,
    NodeType,
)

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
