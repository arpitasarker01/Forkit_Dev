"""
Schema package — exports ModelPassport, AgentPassport and all supporting types.

Import strategy
───────────────
1. Try to import Pydantic v2.  If available, use the full Pydantic models
   from base.py / model_passport.py / agent_passport.py.
2. If Pydantic is not installed, fall back to the pure-Python dataclass
   implementations in _compat.py.  The public API is identical in both cases.

Callers never need to branch on _PYDANTIC_AVAILABLE — the same names work
regardless of which backend is active.
"""

_PYDANTIC_AVAILABLE: bool = False

try:
    import pydantic as _pydantic  # noqa: F401
    if int(_pydantic.__version__.split(".")[0]) < 2:
        raise ImportError("forkit-core requires Pydantic v2+")
    _PYDANTIC_AVAILABLE = True
except ImportError:
    pass

if _PYDANTIC_AVAILABLE:
    from .base import (
        BasePassport,
        CreatorInfo,
        LicenseType,
        PassportStatus,
    )
    from .model_passport import (
        Architecture,
        ModelCapabilities,
        ModelPassport,
        Modality,
        TaskType,
        TrainingDataRef,
    )
    from .agent_passport import (
        AgentArchitecture,
        AgentCapabilities,
        AgentPassport,
        AgentRole,
        AgentTaskType,
        MemoryType,
        SystemPromptRecord,
        ToolRef,
    )
else:
    from ._compat import (  # type: ignore[assignment]
        AgentArchitecture,
        AgentCapabilities,
        AgentPassport,
        AgentRole,
        AgentTaskType,
        Architecture,
        BasePassport,
        CreatorInfo,
        LicenseType,
        MemoryType,
        ModelCapabilities,
        ModelPassport,
        Modality,
        PassportStatus,
        SystemPromptRecord,
        TaskType,
        ToolRef,
        TrainingDataRef,
    )

__all__ = [
    "_PYDANTIC_AVAILABLE",
    # Base
    "BasePassport",
    "CreatorInfo",
    "LicenseType",
    "PassportStatus",
    # Model
    "ModelPassport",
    "ModelCapabilities",
    "TrainingDataRef",
    "Architecture",
    "Modality",
    "TaskType",
    # Agent
    "AgentPassport",
    "AgentCapabilities",
    "AgentRole",
    "AgentTaskType",
    "AgentArchitecture",
    "MemoryType",
    "SystemPromptRecord",
    "ToolRef",
]
