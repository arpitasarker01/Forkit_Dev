"""
forkit.schemas
──────────────
Public schema interface.  Selects the Pydantic v2 backend when available,
otherwise falls back to the pure-Python dataclass backend.

Exported names are identical in both backends so application code does not
need to branch on `_PYDANTIC_AVAILABLE`.

Usage
─────
    from forkit.schemas import ModelPassport, AgentPassport, TaskType, Architecture
    from forkit.schemas import _PYDANTIC_AVAILABLE   # True / False
"""

from __future__ import annotations

# ── Attempt Pydantic v2 backend ────────────────────────────────────────────────
_PYDANTIC_AVAILABLE: bool = False

try:
    import pydantic as _pydantic
    if int(_pydantic.__version__.split(".")[0]) < 2:
        raise ImportError("forkit requires Pydantic v2+")
    _PYDANTIC_AVAILABLE = True
except ImportError:
    pass

# ── Schema classes ─────────────────────────────────────────────────────────────
if _PYDANTIC_AVAILABLE:
    from .pydantic.model import ModelPassport     # noqa: F401
    from .pydantic.agent import AgentPassport     # noqa: F401
else:
    from .model import ModelPassport              # noqa: F401
    from .agent import AgentPassport              # noqa: F401

# ── Enums and types (same source regardless of backend) ───────────────────────
from .enums import (                              # noqa: F401
    AgentArchitecture,
    AgentRole,
    AgentTaskType,
    Architecture,
    LicenseType,
    MemoryType,
    Modality,
    PassportStatus,
    TaskType,
)
from .types import (                              # noqa: F401
    AgentCapabilities,
    CreatorInfo,
    ModelCapabilities,
    SystemPromptRecord,
    ToolRef,
    TrainingDataRef,
)

# ── Re-export base for advanced use ───────────────────────────────────────────
from .base import BasePassport                    # noqa: F401

__all__ = [
    # Passports
    "ModelPassport",
    "AgentPassport",
    "BasePassport",
    # Enums
    "AgentArchitecture",
    "AgentRole",
    "AgentTaskType",
    "Architecture",
    "LicenseType",
    "MemoryType",
    "Modality",
    "PassportStatus",
    "TaskType",
    # Types
    "AgentCapabilities",
    "CreatorInfo",
    "ModelCapabilities",
    "SystemPromptRecord",
    "ToolRef",
    "TrainingDataRef",
    # Flag
    "_PYDANTIC_AVAILABLE",
]
