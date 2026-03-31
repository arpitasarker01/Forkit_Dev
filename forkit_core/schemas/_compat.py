"""
Pure-Python fallback implementations of ModelPassport and AgentPassport.

Used automatically when Pydantic v2 is not installed.  Provides the exact
same public interface as the Pydantic versions so all downstream code —
demos, tests, scripts — works without modification.

Interface contract preserved
────────────────────────────
  - Identical constructor keyword arguments
  - Identical field names and enum values
  - Identical hash validation  (64-char lowercase SHA-256)
  - Identical version validation (semver 2 or 3 parts)
  - Identical _compute_id logic  (artifact_hash|canonical when present)
  - .to_dict()   → JSON-safe dict  (enums serialised as their .value)
  - .from_dict() → reconstructs instance; re-derives id if omitted
  - .short_id()  → first N chars of the passport id

Not provided (pydantic-only features)
──────────────────────────────────────
  - JSON Schema generation
  - OpenAPI integration
  - Field-level description metadata
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

_PYDANTIC_AVAILABLE: bool = False


# ──────────────────────────────────────────────────────────────────────────────
# Enumerations  (exact mirror of base.py + model_passport.py + agent_passport.py)
# ──────────────────────────────────────────────────────────────────────────────

class PassportStatus(str, Enum):
    DRAFT      = "draft"
    ACTIVE     = "active"
    DEPRECATED = "deprecated"
    REVOKED    = "revoked"


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


class TaskType(str, Enum):
    TEXT_GENERATION          = "text-generation"
    TEXT_CLASSIFICATION      = "text-classification"
    TEXT_SUMMARIZATION       = "text-summarization"
    QUESTION_ANSWERING       = "question-answering"
    TRANSLATION              = "translation"
    NAMED_ENTITY_RECOGNITION = "named-entity-recognition"
    SENTIMENT_ANALYSIS       = "sentiment-analysis"
    CODE_GENERATION          = "code-generation"
    CODE_COMPLETION          = "code-completion"
    IMAGE_GENERATION         = "image-generation"
    IMAGE_CLASSIFICATION     = "image-classification"
    IMAGE_CAPTIONING         = "image-captioning"
    VISUAL_QA                = "visual-question-answering"
    SPEECH_TO_TEXT           = "speech-to-text"
    TEXT_TO_SPEECH           = "text-to-speech"
    EMBEDDING                = "embedding"
    RERANKING                = "reranking"
    REASONING                = "reasoning"
    FUNCTION_CALLING         = "function-calling"
    INSTRUCTION_FOLLOWING    = "instruction-following"
    OTHER                    = "other"


class Architecture(str, Enum):
    TRANSFORMER        = "transformer"
    ENCODER_ONLY       = "encoder-only"
    DECODER_ONLY       = "decoder-only"
    ENCODER_DECODER    = "encoder-decoder"
    MAMBA              = "mamba"
    DIFFUSION          = "diffusion"
    CNN                = "cnn"
    RNN                = "rnn"
    HYBRID             = "hybrid"
    MIXTURE_OF_EXPERTS = "mixture-of-experts"
    OTHER              = "other"


class Modality(str, Enum):
    TEXT       = "text"
    IMAGE      = "image"
    AUDIO      = "audio"
    VIDEO      = "video"
    MULTIMODAL = "multimodal"
    CODE       = "code"
    EMBEDDING  = "embedding"


class AgentTaskType(str, Enum):
    CUSTOMER_SUPPORT   = "customer-support"
    PERSONAL_ASSISTANT = "personal-assistant"
    SALES_ASSISTANT    = "sales-assistant"
    CODE_ASSISTANT     = "code-assistant"
    CODE_REVIEW        = "code-review"
    DEVOPS_AUTOMATION  = "devops-automation"
    DATA_ANALYST       = "data-analyst"
    RESEARCH_ASSISTANT = "research-assistant"
    DOCUMENT_QA        = "document-qa"
    ORCHESTRATOR       = "orchestrator"
    PLANNER            = "planner"
    EVALUATOR          = "evaluator"
    LEGAL_ASSISTANT    = "legal-assistant"
    MEDICAL_ASSISTANT  = "medical-assistant"
    FINANCE_ASSISTANT  = "finance-assistant"
    OTHER              = "other"


class AgentArchitecture(str, Enum):
    REACT        = "ReAct"
    COT          = "CoT"
    PLAN_EXECUTE = "Plan-Execute"
    RAG          = "RAG"
    TOOL_USE     = "Tool-Use"
    MULTI_AGENT  = "Multi-Agent"
    REFLEXION    = "Reflexion"
    SELF_ASK     = "Self-Ask"
    CODE_ACT     = "CodeAct"
    CUSTOM       = "Custom"


class AgentRole(str, Enum):
    ASSISTANT    = "assistant"
    PLANNER      = "planner"
    EXECUTOR     = "executor"
    REVIEWER     = "reviewer"
    ORCHESTRATOR = "orchestrator"
    EVALUATOR    = "evaluator"
    CUSTOM       = "custom"


class MemoryType(str, Enum):
    NONE         = "none"
    IN_CONTEXT   = "in_context"
    VECTOR_STORE = "vector_store"
    EXTERNAL_DB  = "external_db"


# ──────────────────────────────────────────────────────────────────────────────
# Validation helpers  (mirrors base.py field_validators)
# ──────────────────────────────────────────────────────────────────────────────

_SHA_CHARS: frozenset[str] = frozenset("0123456789abcdef")


def _validate_hash(v: str | None) -> str | None:
    """Normalise and validate a SHA-256 hex digest.  Accepts uppercase (normalises)."""
    if v is None:
        return v
    v = str(v).lower().strip()
    if len(v) != 64 or not all(c in _SHA_CHARS for c in v):
        raise ValueError(
            f"Hash must be a 64-char lowercase hex string (SHA-256). Got: {v!r}"
        )
    return v


def _validate_version(v: str) -> str:
    parts = str(v).split(".")
    if not (2 <= len(parts) <= 3):
        raise ValueError(
            f"Version must be semver (e.g. '1.0' or '1.0.0'). Got: {v!r}"
        )
    return v


def _compute_id(
    passport_type: str,
    name: str,
    version: str,
    creator_name: str,
    creator_org: str | None,
    artifact_hash: str | None = None,
) -> str:
    """
    Deterministic SHA-256 passport ID.

    Mirrors BasePassport._compute_id exactly:
      - canonical JSON (sorted keys) is always included
      - when artifact_hash is present it is prepended with a '|' separator
        so different artifacts yield different IDs
    """
    canonical = json.dumps(
        {
            "passport_type": passport_type,
            "name":          name,
            "version":       version,
            "creator_name":  creator_name,
            "creator_org":   creator_org,
        },
        sort_keys=True,
    )
    payload = (artifact_hash + "|" + canonical) if artifact_hash else canonical
    return hashlib.sha256(payload.encode()).hexdigest()


def _to_json_safe(obj: Any) -> Any:
    """JSON-default function: serialise enums as their .value."""
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, "isoformat"):          # datetime / date
        return obj.isoformat()
    return str(obj)


# ──────────────────────────────────────────────────────────────────────────────
# Supporting dataclasses
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(kw_only=True)
class CreatorInfo:
    """Who built or owns this model / agent."""

    name: str
    organization: str | None = None
    email: str | None = None
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CreatorInfo:
        valid = {"name", "organization", "email", "url"}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass(kw_only=True)
class TrainingDataRef:
    """Lightweight reference to a training dataset."""

    name: str
    url: str | None = None
    hash: str | None = None
    size_tokens: int | None = None
    cutoff_date: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TrainingDataRef:
        return cls(**{k: v for k, v in d.items()
                      if k in {"name", "url", "hash", "size_tokens", "cutoff_date"}})


@dataclass(kw_only=True)
class ModelCapabilities:
    """What the model can do at runtime."""

    modalities: list[str] = field(default_factory=list)
    context_length: int | None = None
    supports_function_calling: bool = False
    supports_streaming: bool = False
    languages: list[str] = field(default_factory=list)
    benchmark_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ModelCapabilities:
        valid = {"modalities", "context_length", "supports_function_calling",
                 "supports_streaming", "languages", "benchmark_scores"}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass(kw_only=True)
class ToolRef:
    """Reference to an external tool / function the agent can call."""

    name: str
    version: str | None = None
    description: str | None = None
    source_url: str | None = None
    hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ToolRef:
        valid = {"name", "version", "description", "source_url", "hash"}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass(kw_only=True)
class AgentCapabilities:
    """What the agent supports at runtime."""

    max_iterations: int | None = None
    supports_streaming: bool = False
    supports_multi_turn: bool = True
    supports_tool_use: bool = False
    languages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AgentCapabilities:
        valid = {"max_iterations", "supports_streaming", "supports_multi_turn",
                 "supports_tool_use", "languages"}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass(kw_only=True)
class SystemPromptRecord:
    """Non-reversible audit record of the system prompt."""

    hash: str
    length_chars: int
    template_id: str | None = None
    redacted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SystemPromptRecord:
        valid = {"hash", "length_chars", "template_id", "redacted"}
        return cls(**{k: v for k, v in d.items() if k in valid})


# ──────────────────────────────────────────────────────────────────────────────
# BasePassport
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(kw_only=True)
class BasePassport:
    """
    Pure-Python base for ModelPassport and AgentPassport.

    All validation and ID-derivation logic lives here so it runs identically
    whether or not Pydantic is available.
    """

    # ── Required ──────────────────────────────────────────────────────────────
    name: str
    version: str
    creator: CreatorInfo | dict

    # ── Provenance ────────────────────────────────────────────────────────────
    artifact_hash: str | None = None
    parent_hash: str | None = None

    # ── Authorship & legal ────────────────────────────────────────────────────
    license: LicenseType | str = LicenseType.OTHER
    license_url: str | None = None

    # ── Identity (auto-computed) ──────────────────────────────────────────────
    id: str = field(default="")
    description: str | None = None

    # ── Registry metadata ─────────────────────────────────────────────────────
    status: PassportStatus | str = PassportStatus.DRAFT
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        # Coerce nested object
        if isinstance(self.creator, dict):
            self.creator = CreatorInfo.from_dict(self.creator)

        # Coerce enums from strings (enables from_dict round-trips)
        if isinstance(self.license, str):
            self.license = LicenseType(self.license)
        if isinstance(self.status, str):
            self.status = PassportStatus(self.status)

        # Validate hash format
        self.artifact_hash = _validate_hash(self.artifact_hash)
        self.parent_hash   = _validate_hash(self.parent_hash)

        # Validate version
        self.version = _validate_version(self.version)

        # Compute id if not already set
        if not self.id:
            self.id = _compute_id(
                passport_type=getattr(self, "passport_type", self.__class__.__name__),
                name=self.name,
                version=self.version,
                creator_name=self.creator.name,
                creator_org=self.creator.organization,
                artifact_hash=self.artifact_hash,
            )

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dict with all enum values serialised as strings."""
        raw = dataclasses.asdict(self)
        # Round-trip through json to normalise enums → values, datetimes → strings
        return json.loads(json.dumps(raw, default=_to_json_safe))

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> BasePassport:
        """Reconstruct from a dict.  If 'id' is absent it is re-derived."""
        d = dict(d)
        d.pop("passport_type", None)      # frozen field, set by subclass
        if isinstance(d.get("creator"), dict):
            d["creator"] = CreatorInfo.from_dict(d["creator"])
        return cls(**d)

    def short_id(self, length: int = 12) -> str:
        return self.id[:length]

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name={self.name!r} version={self.version!r} "
            f"id={self.short_id()}...>"
        )


# ──────────────────────────────────────────────────────────────────────────────
# ModelPassport
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(kw_only=True)
class ModelPassport(BasePassport):
    """Full identity and provenance document for an AI model."""

    passport_type: str = field(default="model", init=False)

    # ── Required ──────────────────────────────────────────────────────────────
    task_type: TaskType | str
    architecture: Architecture | str

    # ── External ID ───────────────────────────────────────────────────────────
    model_id: str | None = None

    # ── Artifact detail ───────────────────────────────────────────────────────
    artifact_files: list[str] = field(default_factory=list)
    quantization: str | None = None

    # ── Lineage ───────────────────────────────────────────────────────────────
    base_model_name: str | None = None
    fine_tuning_method: str | None = None

    # ── Training ──────────────────────────────────────────────────────────────
    training_data: list[TrainingDataRef | dict] = field(default_factory=list)
    parameter_count: int | None = None

    # ── Capabilities ──────────────────────────────────────────────────────────
    capabilities: ModelCapabilities | dict = field(default_factory=ModelCapabilities)
    usage_restrictions: list[str] = field(default_factory=list)

    # ── Links ─────────────────────────────────────────────────────────────────
    hub_url: str | None = None
    paper_url: str | None = None

    def __post_init__(self) -> None:
        # Coerce model-specific enums
        if isinstance(self.task_type, str):
            self.task_type = TaskType(self.task_type)
        if isinstance(self.architecture, str):
            self.architecture = Architecture(self.architecture)

        # Coerce nested objects
        if isinstance(self.capabilities, dict):
            self.capabilities = ModelCapabilities.from_dict(self.capabilities)
        self.training_data = [
            TrainingDataRef.from_dict(t) if isinstance(t, dict) else t
            for t in self.training_data
        ]

        # Delegate to base (hash validation, version validation, id derivation)
        super().__post_init__()

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        # Ensure enum values are strings (super() handles the json round-trip
        # but nested dataclasses like capabilities come through asdict already)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ModelPassport:
        d = dict(d)
        d.pop("passport_type", None)
        if isinstance(d.get("creator"), dict):
            d["creator"] = CreatorInfo.from_dict(d["creator"])
        if isinstance(d.get("capabilities"), dict):
            d["capabilities"] = ModelCapabilities.from_dict(d["capabilities"])
        if "training_data" in d:
            d["training_data"] = [
                TrainingDataRef.from_dict(t) if isinstance(t, dict) else t
                for t in d["training_data"]
            ]
        return cls(**d)


# ──────────────────────────────────────────────────────────────────────────────
# AgentPassport
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(kw_only=True)
class AgentPassport(BasePassport):
    """Full identity and provenance document for an AI agent."""

    passport_type: str = field(default="agent", init=False)

    # ── Required ──────────────────────────────────────────────────────────────
    model_id: str
    task_type: AgentTaskType | str
    architecture: AgentArchitecture | str

    # ── Model binding ─────────────────────────────────────────────────────────
    model_version: str | None = None

    # ── Identity / role ───────────────────────────────────────────────────────
    role: AgentRole | str = AgentRole.ASSISTANT
    capabilities: AgentCapabilities | dict = field(default_factory=AgentCapabilities)

    # ── Configuration fingerprints ────────────────────────────────────────────
    system_prompt: SystemPromptRecord | dict | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None

    # ── Tools and memory ──────────────────────────────────────────────────────
    tools: list[ToolRef | dict] = field(default_factory=list)
    memory_type: MemoryType | str = MemoryType.NONE
    memory_config: dict[str, Any] = field(default_factory=dict)

    # ── Fork lineage ──────────────────────────────────────────────────────────
    parent_agent_name: str | None = None
    fork_reason: str | None = None

    # ── Deployment ────────────────────────────────────────────────────────────
    deployment_env: str | None = None
    endpoint_hash: str | None = None

    def __post_init__(self) -> None:
        # Coerce agent-specific enums
        if isinstance(self.task_type, str):
            self.task_type = AgentTaskType(self.task_type)
        if isinstance(self.architecture, str):
            self.architecture = AgentArchitecture(self.architecture)
        if isinstance(self.role, str):
            self.role = AgentRole(self.role)
        if isinstance(self.memory_type, str):
            self.memory_type = MemoryType(self.memory_type)

        # Coerce nested objects
        if isinstance(self.capabilities, dict):
            self.capabilities = AgentCapabilities.from_dict(self.capabilities)
        if isinstance(self.system_prompt, dict):
            self.system_prompt = SystemPromptRecord.from_dict(self.system_prompt)
        self.tools = [
            ToolRef.from_dict(t) if isinstance(t, dict) else t
            for t in self.tools
        ]

        # Delegate to base
        super().__post_init__()

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AgentPassport:
        d = dict(d)
        d.pop("passport_type", None)
        if isinstance(d.get("creator"), dict):
            d["creator"] = CreatorInfo.from_dict(d["creator"])
        if isinstance(d.get("capabilities"), dict):
            d["capabilities"] = AgentCapabilities.from_dict(d["capabilities"])
        if isinstance(d.get("system_prompt"), dict):
            d["system_prompt"] = SystemPromptRecord.from_dict(d["system_prompt"])
        if "tools" in d:
            d["tools"] = [
                ToolRef.from_dict(t) if isinstance(t, dict) else t
                for t in d["tools"]
            ]
        return cls(**d)
