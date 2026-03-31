"""
forkit.schemas.pydantic
───────────────────────
Optional Pydantic v2 backend for ModelPassport and AgentPassport.

Install pydantic >= 2.0 to enable:
    pip install pydantic>=2.0

When available the Pydantic models provide:
  - JSON Schema / OpenAPI generation
  - Field-level description metadata
  - .model_validate() / .model_dump() compatibility

The public interface (constructor kwargs, field names, enum values, to_dict(),
from_dict(), short_id()) is identical to the dataclass backend so application
code does not need to know which backend is active.

Usage
─────
  from forkit.schemas import ModelPassport, _PYDANTIC_AVAILABLE
  # _PYDANTIC_AVAILABLE is True when pydantic>=2 is installed

  # Or force the pydantic backend explicitly:
  from forkit.schemas.pydantic.model import ModelPassport
"""

# Guard: only expose symbols if pydantic is actually available
try:
    import pydantic as _p
    if int(_p.__version__.split(".")[0]) < 2:
        raise ImportError("forkit requires Pydantic v2+")

    from ..enums import (  # noqa: F401
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
    from ..types import (  # noqa: F401
        AgentCapabilities,
        CreatorInfo,
        ModelCapabilities,
        SystemPromptRecord,
        ToolRef,
        TrainingDataRef,
    )
    from .agent import AgentPassport  # noqa: F401
    from .model import ModelPassport  # noqa: F401

    _PYDANTIC_AVAILABLE: bool = True

except ImportError:
    _PYDANTIC_AVAILABLE: bool = False         # type: ignore[assignment]
