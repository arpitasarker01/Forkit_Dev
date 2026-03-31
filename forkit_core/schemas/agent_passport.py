"""
Agent Passport — identity and provenance document for an AI agent.

An agent is a deployed entity that wraps a model with instructions, tools,
memory, and runtime configuration.

Key fields
──────────
model_id        Forkit passport ID of the underlying ModelPassport.
version         Semver of this agent passport record.
task_type       Primary task this agent is designed to perform.
architecture    Agent reasoning / execution pattern (ReAct, CoT, RAG, etc.).
artifact_hash   SHA-256 of the agent's serialised config bundle (system prompt
                hash + tool manifest + runtime params).  Drives passport ID.
parent_hash     SHA-256 of the parent agent's config bundle this was forked from.
creator         Author / owning entity (inherited from BasePassport).
license         Distribution or usage license (inherited from BasePassport).
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .base import BasePassport  # re-exported

# ──────────────────────────────────────────────────────────────────────────────
# Enumerations
# ──────────────────────────────────────────────────────────────────────────────

class AgentTaskType(str, Enum):
    """Primary task this agent is designed to perform."""

    # Conversation
    CUSTOMER_SUPPORT   = "customer-support"
    PERSONAL_ASSISTANT = "personal-assistant"
    SALES_ASSISTANT    = "sales-assistant"

    # Development
    CODE_ASSISTANT     = "code-assistant"
    CODE_REVIEW        = "code-review"
    DEVOPS_AUTOMATION  = "devops-automation"

    # Data & research
    DATA_ANALYST       = "data-analyst"
    RESEARCH_ASSISTANT = "research-assistant"
    DOCUMENT_QA        = "document-qa"

    # Orchestration
    ORCHESTRATOR       = "orchestrator"
    PLANNER            = "planner"
    EVALUATOR          = "evaluator"

    # Domain-specific
    LEGAL_ASSISTANT    = "legal-assistant"
    MEDICAL_ASSISTANT  = "medical-assistant"
    FINANCE_ASSISTANT  = "finance-assistant"

    OTHER              = "other"


class AgentArchitecture(str, Enum):
    """
    Reasoning / execution pattern the agent implements.

    These map to well-known agentic patterns in the literature.
    """

    REACT              = "ReAct"           # Reason + Act (Yao et al. 2022)
    COT                = "CoT"             # Chain-of-Thought
    PLAN_EXECUTE       = "Plan-Execute"    # explicit plan step then execution
    RAG                = "RAG"             # Retrieval-Augmented Generation
    TOOL_USE           = "Tool-Use"        # direct tool dispatch, no explicit planning
    MULTI_AGENT        = "Multi-Agent"     # orchestrates sub-agents
    REFLEXION          = "Reflexion"       # self-reflection loop
    SELF_ASK           = "Self-Ask"        # decompose + ask sub-questions
    CODE_ACT           = "CodeAct"         # generates + executes code
    CUSTOM             = "Custom"


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
# Supporting models
# ──────────────────────────────────────────────────────────────────────────────

class ToolRef(BaseModel):
    """Reference to an external tool / function the agent can call."""

    name: str
    version: str | None = None
    description: str | None = None
    source_url: str | None = None
    hash: str | None = Field(
        None,
        description="SHA-256 of the tool implementation (function code or schema)",
    )


class AgentCapabilities(BaseModel):
    """What the agent supports at runtime."""

    max_iterations: int | None = Field(
        None,
        description="Hard cap on agent loops / steps per invocation",
    )
    supports_streaming: bool = False
    supports_multi_turn: bool = True
    supports_tool_use: bool = False
    languages: list[str] = Field(
        default_factory=list,
        description="ISO-639-1 codes for supported input languages",
    )


class SystemPromptRecord(BaseModel):
    """
    Non-reversible audit record of the system prompt.

    The raw prompt text is never stored in the passport.
    Only its SHA-256 hash and metadata are recorded.
    """

    hash: str = Field(..., description="SHA-256 of the raw system prompt text")
    length_chars: int = Field(..., description="Character length of the raw prompt")
    template_id: str | None = Field(
        None,
        description="Versioned template ID if the prompt was sourced from a template store",
    )
    redacted: bool = Field(
        default=False,
        description="True when the hash was computed but the source text is not retained",
    )


# ──────────────────────────────────────────────────────────────────────────────
# AgentPassport
# ──────────────────────────────────────────────────────────────────────────────

class AgentPassport(BasePassport):
    """
    Full identity and provenance document for an AI agent.

    Inherits from BasePassport:
        id, name, version, description, artifact_hash, parent_hash,
        creator, license, license_url, status, tags, metadata,
        created_at, updated_at

    Adds:
        model_id        Passport ID of the underlying model.
        task_type       Primary task this agent performs.
        architecture    Reasoning / execution pattern.
        … and runtime configuration fields below.
    """

    passport_type: str = Field(default="agent", frozen=True)

    # ── Core required fields ──────────────────────────────────────────────────

    model_id: str = Field(
        ...,
        description=(
            "Forkit passport ID (`id` field) of the ModelPassport this agent is built on. "
            "Provides a hard cryptographic link to the underlying model."
        ),
    )
    task_type: AgentTaskType = Field(
        ...,
        description="Primary task this agent is designed to perform",
    )
    architecture: AgentArchitecture = Field(
        ...,
        description="Reasoning / execution pattern the agent implements",
    )

    # ── Model binding ─────────────────────────────────────────────────────────
    model_version: str | None = Field(
        None,
        description="Expected model semver — used for integrity checking at deploy time",
    )

    # ── Artifact details ──────────────────────────────────────────────────────
    # artifact_hash (from BasePassport) = SHA-256 of the serialised agent config bundle.
    # parent_hash   (from BasePassport) = SHA-256 of the parent agent's config bundle.
    #
    # Recommended content of agent config bundle (for reproducible artifact_hash):
    #   system_prompt_hash + sorted(tool names + versions) + runtime params JSON

    # ── Identity / role ───────────────────────────────────────────────────────
    role: AgentRole = Field(
        AgentRole.ASSISTANT,
        description="Agent's primary role in a multi-agent system",
    )
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)

    # ── Configuration fingerprints ────────────────────────────────────────────
    system_prompt: SystemPromptRecord | None = Field(
        None,
        description="Non-reversible audit record of the system prompt",
    )
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    top_p: float | None = Field(None, ge=0.0, le=1.0)
    max_tokens: int | None = Field(None, gt=0)

    # ── Tools and memory ──────────────────────────────────────────────────────
    tools: list[ToolRef] = Field(default_factory=list)
    memory_type: MemoryType = MemoryType.NONE
    memory_config: dict[str, Any] = Field(
        default_factory=dict,
        description="Memory backend config, e.g. {'provider': 'qdrant', 'collection': 'v2'}",
    )

    # ── Fork lineage ──────────────────────────────────────────────────────────
    # parent_hash (BasePassport) = SHA-256 of parent agent's config bundle.
    # Complement with human-readable context:

    parent_agent_name: str | None = Field(
        None,
        description="Display name of the agent this was forked from. "
                    "Informational — parent_hash is the verifiable link.",
    )
    fork_reason: str | None = Field(
        None,
        description="Why this agent was forked, e.g. 'specialized for Arabic support'",
    )

    # ── Deployment ────────────────────────────────────────────────────────────
    deployment_env: str | None = Field(
        None,
        description="Target environment, e.g. 'production', 'staging', 'local'",
    )
    endpoint_hash: str | None = Field(
        None,
        description="SHA-256 of the serving endpoint URL — not the URL itself",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name":          "support-agent-ar-en",
                "version":       "2.0.0",
                "model_id":      "a" * 64,
                "task_type":     "customer-support",
                "architecture":  "ReAct",
                "artifact_hash": "c" * 64,
                "license":       "Apache-2.0",
                "creator": {
                    "name":         "Hamza",
                    "organization": "ForkIt",
                },
                "tools": [
                    {"name": "knowledge_base_search", "version": "1.2.0"},
                    {"name": "ticket_creator",        "version": "1.0.0"},
                ],
                "capabilities": {
                    "supports_tool_use":   True,
                    "supports_multi_turn": True,
                    "languages":           ["en", "ar"],
                },
            }
        }
    }
