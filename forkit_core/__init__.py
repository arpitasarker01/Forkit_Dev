"""
forkit-core — Identity and provenance infrastructure for AI models and agents.
"""

__version__ = "0.1.0"

# These modules have no Pydantic dependency — always importable.
from .hashing import HashEngine, engine as hash_engine
from .lineage import LineageGraph

# Schemas handle the Pydantic/compat switch internally.
from .schemas import (
    ModelPassport,
    AgentPassport,
    CreatorInfo,
    PassportStatus,
    _PYDANTIC_AVAILABLE,
)

# Registry and SDK require Pydantic (they import schemas internally).
# Import gracefully so the package is still usable without Pydantic.
try:
    from .registry import LocalRegistry
    from .sdk import ForkitClient
except Exception:
    LocalRegistry = None  # type: ignore[assignment,misc]
    ForkitClient  = None  # type: ignore[assignment]

__all__ = [
    "__version__",
    "_PYDANTIC_AVAILABLE",
    # Core schemas
    "ModelPassport",
    "AgentPassport",
    "CreatorInfo",
    "PassportStatus",
    # Hashing
    "HashEngine",
    "hash_engine",
    # Lineage
    "LineageGraph",
    # Registry + SDK (None when Pydantic unavailable)
    "LocalRegistry",
    "ForkitClient",
]
