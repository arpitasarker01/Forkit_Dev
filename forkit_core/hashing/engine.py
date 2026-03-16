"""
Hashing Engine — deterministic SHA-256 fingerprinting for passports, artifacts,
and configuration objects.

Design principles
─────────────────
1. Reproducibility across environments
   - Canonical JSON serialisation (keys sorted, default=str) ensures the same
     dict always produces the same bytes regardless of Python version or OS.
   - File hashing reads in fixed 64 KB chunks so large weight files are handled
     without loading them into memory.
   - Directory hashing sorts files by relative path before hashing so the result
     is stable regardless of filesystem ordering (ext4, APFS, NTFS, etc.).

2. Separation of concerns
   hash_artifact()     → primary method for model weight files / agent bundles
   hash_metadata()     → primary method for passport dicts and config objects
   hash_file()         → single file, any size
   hash_directory()    → multi-file artifact (e.g. HuggingFace model folder)
   hash_string()       → raw text (system prompts, config YAML, etc.)
   hash_bytes()        → raw bytes

3. Verification helpers
   verify_file() / verify_dict() return bool — safe to use in assertions.

Usage
─────
    from forkit_core.hashing import engine

    # Hash a weights file before registering a ModelPassport
    artifact_hash = engine.hash_artifact("/models/llama-3-8b/model.safetensors")

    # Hash passport metadata to produce a stable document fingerprint
    meta_hash = engine.hash_metadata(passport.to_dict())

    # Verify at load time
    assert engine.verify_file("/models/llama-3-8b/model.safetensors", artifact_hash)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CHUNK_SIZE: int = 65_536  # 64 KB — efficient for large weight files
HASH_HEX_LENGTH: int = 64  # SHA-256 produces 32 bytes = 64 hex chars

# Canonical file extensions for model weight files
_MODEL_WEIGHT_EXTENSIONS: frozenset[str] = frozenset({
    ".safetensors", ".bin", ".pt", ".pth", ".ckpt",
    ".gguf", ".ggml", ".ot", ".npz",
})

# Files always included in a model artifact hash even if not weights
_MODEL_CONFIG_EXTENSIONS: frozenset[str] = frozenset({
    ".json", ".yaml", ".yml", ".txt",
})


class HashEngine:
    """
    Stateless utility for producing deterministic SHA-256 fingerprints.

    All methods are @staticmethod so the class can be used either as a
    namespace (HashEngine.hash_file(...)) or via the module-level singleton
    (`engine.hash_file(...)`).
    """

    algorithm: str = "sha256"

    # ──────────────────────────────────────────────────────────────────────────
    # Primitive hashing
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """SHA-256 over raw bytes → 64-char lowercase hex string."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_string(text: str, encoding: str = "utf-8") -> str:
        """SHA-256 over a UTF-8 (or specified) encoded string."""
        return HashEngine.hash_bytes(text.encode(encoding))

    @staticmethod
    def hash_dict(data: dict[str, Any]) -> str:
        """
        Canonical SHA-256 over a dict.

        Guarantees:
        - Keys are sorted recursively via json.dumps(sort_keys=True).
        - Non-serialisable values are coerced with default=str.
        - Output is identical across Python 3.10+ on all platforms.
        """
        canonical = json.dumps(data, sort_keys=True, default=str)
        return HashEngine.hash_string(canonical)

    @staticmethod
    def hash_file(path: str | Path) -> str:
        """
        SHA-256 of a file, read in 64 KB chunks.
        Safe for multi-GB weight files — never loads the full file into memory.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Cannot hash — file not found: {path}")

        h = hashlib.sha256()
        with open(path, "rb") as f:
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
        Deterministic hash of a directory's contents.

        Files are sorted by *relative path* before hashing so the result is
        stable regardless of filesystem ordering.

        Args:
            path:              Directory to hash.
            extensions:        If provided, only files with these extensions are
                               included (e.g. ['.safetensors', '.json']).
            include_filenames: When True (default), each file's relative path is
                               mixed into the hash so renaming a file changes the
                               directory hash even if bytes are identical.
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
                rel = str(fp.relative_to(root)).encode()
                combined.update(rel)
            combined.update(HashEngine.hash_file(fp).encode())

        return combined.hexdigest()

    # ──────────────────────────────────────────────────────────────────────────
    # High-level artifact hashing
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def hash_artifact(path: str | Path) -> str:
        """
        Hash a model or agent *artifact* — either a single file or a directory.

        For a single file (e.g. a GGUF or SafeTensors file):
            Returns SHA-256 of that file.

        For a directory (e.g. a HuggingFace model folder):
            Hashes all files sorted by relative path.  The hash covers both
            file content and relative filenames to catch renames.

        This is the recommended method to produce the `artifact_hash` field
        for ModelPassport and AgentPassport.

        Example:
            artifact_hash = engine.hash_artifact("/models/llama-3-8b/")
            passport = ModelPassport(artifact_hash=artifact_hash, ...)
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

        Includes:
        - Weight files: .safetensors, .bin, .pt, .pth, .ckpt, .gguf, .ggml, .npz
        - Config files (if include_config=True): .json, .yaml, .yml, .txt

        This produces a hash that changes when either weights or config change,
        but ignores unrelated files (logs, readmes, etc.).

        Args:
            path:           Path to model directory.
            include_config: Whether to include config/tokenizer JSON files.
        """
        p = Path(path)
        if p.is_file():
            return HashEngine.hash_file(p)

        exts = set(_MODEL_WEIGHT_EXTENSIONS)
        if include_config:
            exts |= _MODEL_CONFIG_EXTENSIONS

        return HashEngine.hash_directory(p, extensions=list(exts))

    # ──────────────────────────────────────────────────────────────────────────
    # Metadata hashing
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def hash_metadata(data: dict[str, Any]) -> str:
        """
        Canonical SHA-256 hash of a passport metadata dict.

        Excludes volatile fields (`id`, `created_at`, `updated_at`) that
        should not change the document fingerprint when the content has not
        actually changed.

        Use this to detect when a passport's *substantive* fields have changed,
        e.g. to decide whether to issue a new version.

        Example:
            meta_hash = engine.hash_metadata(passport.to_dict())
        """
        VOLATILE = {"id", "created_at", "updated_at"}
        stable = {k: v for k, v in data.items() if k not in VOLATILE}
        return HashEngine.hash_dict(stable)

    @staticmethod
    def hash_passport(passport_dict: dict[str, Any]) -> str:
        """
        Compute a stable ID for a passport from its canonical identity fields.

        Uses only: passport_type, name, version, creator (name + org).
        Does NOT include artifact_hash — this is the content-agnostic ID.
        For the content-aware ID (which changes when the artifact changes),
        use BasePassport._compute_id() or the auto-assigned `id` field.
        """
        canonical = {
            k: passport_dict[k]
            for k in ("passport_type", "name", "version", "creator")
            if k in passport_dict
        }
        return HashEngine.hash_dict(canonical)

    @staticmethod
    def hash_config(config: dict[str, Any]) -> str:
        """Hash an agent or model configuration dict."""
        return HashEngine.hash_dict(config)

    @staticmethod
    def hash_system_prompt(prompt_text: str) -> str:
        """Hash a system prompt string."""
        return HashEngine.hash_string(prompt_text)

    # ──────────────────────────────────────────────────────────────────────────
    # Verification
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def verify_file(path: str | Path, expected_hash: str) -> bool:
        """Return True if the file's SHA-256 matches expected_hash (case-insensitive)."""
        return HashEngine.hash_file(path) == expected_hash.lower()

    @staticmethod
    def verify_artifact(path: str | Path, expected_hash: str) -> bool:
        """
        Return True if the artifact's hash matches expected_hash.
        Works for both single files and directories.
        """
        return HashEngine.hash_artifact(path) == expected_hash.lower()

    @staticmethod
    def verify_dict(data: dict[str, Any], expected_hash: str) -> bool:
        """Return True if the dict's canonical hash matches expected_hash."""
        return HashEngine.hash_dict(data) == expected_hash.lower()

    @staticmethod
    def verify_metadata(
        passport_dict: dict[str, Any],
        expected_hash: str,
    ) -> bool:
        """
        Return True if the passport's stable metadata hash matches expected_hash.
        Uses hash_metadata() which excludes volatile fields.
        """
        return HashEngine.hash_metadata(passport_dict) == expected_hash.lower()

    # ──────────────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def short_id(full_hash: str, length: int = 12) -> str:
        """Return a short human-readable prefix of a full hash."""
        return full_hash[:length]

    @staticmethod
    def is_valid_hash(value: str) -> bool:
        """Return True if value is a valid 64-char lowercase SHA-256 hex string."""
        v = str(value).strip()
        return len(v) == HASH_HEX_LENGTH and all(c in "0123456789abcdef" for c in v)


# Module-level singleton for convenient import
engine = HashEngine()
