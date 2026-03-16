"""
forkit.domain.hashing
─────────────────────
Deterministic SHA-256 fingerprinting for files, directories, dicts, and strings.

Design principles
─────────────────
1. Reproducibility
   - Canonical JSON (sort_keys=True, default=str) → same bytes on all platforms.
   - Directory hashing sorts files by relative path before hashing.
   - File hashing reads in 64 KB chunks — safe for multi-GB weight files.

2. Separation of concerns
   hash_artifact()      → primary entry point for model weight files / agent bundles
   hash_metadata()      → passport dicts, excludes volatile fields
   hash_file()          → single file, any size
   hash_directory()     → multi-file directory (e.g. HuggingFace model folder)
   hash_string()        → raw text (system prompts, config YAML, etc.)
   hash_bytes()         → raw bytes

3. Verification
   verify_file(), verify_artifact(), verify_dict(), verify_metadata()
   all return bool — safe to use in assertions and conditional checks.

4. is_valid_hash() is a STRICT check — uppercase hex is rejected.
   validate_hash() in identity.py normalises first; use that on user input.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

__all__ = [
    "HASH_HEX_LENGTH",
    "HashEngine",
    "engine",
]

CHUNK_SIZE: int = 65_536        # 64 KB
HASH_HEX_LENGTH: int = 64       # SHA-256 → 32 bytes → 64 hex chars

_MODEL_WEIGHT_EXTS: frozenset[str] = frozenset({
    ".safetensors", ".bin", ".pt", ".pth", ".ckpt",
    ".gguf", ".ggml", ".ot", ".npz",
})
_MODEL_CONFIG_EXTS: frozenset[str] = frozenset({
    ".json", ".yaml", ".yml", ".txt",
})


class HashEngine:
    """
    Stateless utility for deterministic SHA-256 fingerprints.

    All methods are @staticmethod so the class can be used either as a
    namespace (HashEngine.hash_file(...)) or via the module-level singleton
    (hash_engine.hash_file(...)).
    """

    algorithm: str = "sha256"

    # ── Primitive ──────────────────────────────────────────────────────────────

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """SHA-256 over raw bytes → 64-char lowercase hex."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_string(text: str, encoding: str = "utf-8") -> str:
        """SHA-256 over a string."""
        return HashEngine.hash_bytes(text.encode(encoding))

    @staticmethod
    def hash_dict(data: dict[str, Any]) -> str:
        """
        Canonical SHA-256 over a dict.

        Keys are sorted recursively.  Non-serialisable values are coerced with
        default=str.  Result is identical across Python 3.10+ on all platforms.
        """
        canonical = json.dumps(data, sort_keys=True, default=str)
        return HashEngine.hash_string(canonical)

    @staticmethod
    def hash_file(path: str | Path) -> str:
        """
        SHA-256 of a file, read in 64 KB chunks.
        Never loads the full file into memory — safe for multi-GB weight files.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
        h = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def hash_directory(
        path: str | Path,
        extensions: list[str] | None = None,
        include_filenames: bool = True,
    ) -> str:
        """
        Deterministic hash of a directory.

        Files are sorted by relative path before hashing so the result is stable
        regardless of filesystem ordering (ext4, APFS, NTFS, etc.).

        Args:
            path:              Directory to hash.
            extensions:        If provided, only files with these extensions
                               are included.
            include_filenames: Mix each file's relative path into the hash
                               so renaming a file changes the directory hash.
        """
        root = Path(path)
        if not root.is_dir():
            raise NotADirectoryError(f"Not a directory: {root}")

        files = sorted(f for f in root.rglob("*") if f.is_file())
        if extensions:
            exts = {e.lower() for e in extensions}
            files = [f for f in files if f.suffix.lower() in exts]

        combined = hashlib.sha256()
        for fp in files:
            if include_filenames:
                combined.update(str(fp.relative_to(root)).encode())
            combined.update(HashEngine.hash_file(fp).encode())
        return combined.hexdigest()

    # ── High-level artifact hashing ────────────────────────────────────────────

    @staticmethod
    def hash_artifact(path: str | Path) -> str:
        """
        Hash a model or agent artifact — file or directory.

        This is the recommended method to produce the `artifact_hash` field for
        ModelPassport and AgentPassport.  Uses hash_file for a single file and
        hash_directory (all files, sorted) for a directory.
        """
        p = Path(path)
        if p.is_file():
            return HashEngine.hash_file(p)
        if p.is_dir():
            return HashEngine.hash_directory(p)
        raise FileNotFoundError(f"Path does not exist: {p}")

    @staticmethod
    def hash_model_artifact(
        path: str | Path,
        include_config: bool = True,
    ) -> str:
        """
        Hash a model artifact directory with opinionated extension filtering.

        Includes weight files (.safetensors, .bin, .pt, .pth, .ckpt, .gguf, …)
        and optionally config files (.json, .yaml, .yml, .txt).

        Note: hash_artifact() hashes ALL files; this method is selective.
        Use the same method for both creation and verification.
        """
        p = Path(path)
        if p.is_file():
            return HashEngine.hash_file(p)
        exts = set(_MODEL_WEIGHT_EXTS)
        if include_config:
            exts |= _MODEL_CONFIG_EXTS
        return HashEngine.hash_directory(p, extensions=list(exts))

    # ── Metadata hashing ───────────────────────────────────────────────────────

    @staticmethod
    def hash_metadata(data: dict[str, Any]) -> str:
        """
        Hash a passport dict, excluding volatile fields.

        Excludes `id`, `created_at`, `updated_at` so the metadata hash is stable
        even after the passport is stored or the timestamps are refreshed.
        """
        _VOLATILE = {"id", "created_at", "updated_at"}
        stable = {k: v for k, v in data.items() if k not in _VOLATILE}
        return HashEngine.hash_dict(stable)

    @staticmethod
    def hash_config(config: dict[str, Any]) -> str:
        """Hash any configuration dict canonically."""
        return HashEngine.hash_dict(config)

    @staticmethod
    def hash_system_prompt(prompt_text: str) -> str:
        """Hash a system prompt string."""
        return HashEngine.hash_string(prompt_text)

    # ── Verification ───────────────────────────────────────────────────────────

    @staticmethod
    def verify_file(path: str | Path, expected_hash: str) -> bool:
        """True if the file's SHA-256 matches expected_hash (case-insensitive)."""
        return HashEngine.hash_file(path) == expected_hash.lower()

    @staticmethod
    def verify_artifact(path: str | Path, expected_hash: str) -> bool:
        """True if the artifact hash (file or directory) matches expected_hash."""
        return HashEngine.hash_artifact(path) == expected_hash.lower()

    @staticmethod
    def verify_dict(data: dict[str, Any], expected_hash: str) -> bool:
        """True if the dict's canonical hash matches expected_hash."""
        return HashEngine.hash_dict(data) == expected_hash.lower()

    @staticmethod
    def verify_metadata(passport_dict: dict[str, Any], expected_hash: str) -> bool:
        """True if the passport's stable metadata hash matches expected_hash."""
        return HashEngine.hash_metadata(passport_dict) == expected_hash.lower()

    # ── Utilities ──────────────────────────────────────────────────────────────

    @staticmethod
    def short_id(full_hash: str, length: int = 12) -> str:
        """Human-readable prefix of a hash."""
        return full_hash[:length]

    @staticmethod
    def is_valid_hash(value: str) -> bool:
        """
        Strict check: True only for a 64-char lowercase hex SHA-256 digest.

        Uppercase hex returns False.  Use validate_hash() from domain.identity
        if you want normalisation before checking.
        """
        v = str(value).strip()
        return len(v) == HASH_HEX_LENGTH and all(c in "0123456789abcdef" for c in v)


# Module-level singleton
engine = HashEngine()
