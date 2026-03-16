"""
forkit.schemas.enums
────────────────────
All enumerations shared by ModelPassport and AgentPassport.

Kept in a single file so:
  - the dataclass backend, the Pydantic backend, and any CLI/serialisation
    code all import from one canonical location.
  - adding a new enum value is a one-line change with no risk of drift
    between backends.
"""

from __future__ import annotations

from enum import Enum


# ── Shared ────────────────────────────────────────────────────────────────────

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


# ── Model ─────────────────────────────────────────────────────────────────────

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


# ── Agent ─────────────────────────────────────────────────────────────────────

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
