"""
Model Passport — identity and provenance document for an AI model.

Key fields
──────────
model_id        External identifier (HuggingFace path, internal slug, etc.).
                Distinct from `id` which is the forkit-computed passport ID.
version         Semver of this passport record.
task_type       Primary task the model was trained / fine-tuned for.
architecture    Model architecture family (transformer, diffusion, mamba, …).
artifact_hash   SHA-256 of the model weights file or weights directory.
                Drives passport ID — swapping weights changes the passport ID.
parent_hash     SHA-256 of the base model weights this was fine-tuned from.
                Enables hash-chain lineage without a central parent registry.
creator         Author / owning entity (inherited from BasePassport).
license         Distribution license (inherited from BasePassport).
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from .base import BasePassport  # LicenseType re-exported for convenience

# ──────────────────────────────────────────────────────────────────────────────
# Enumerations
# ──────────────────────────────────────────────────────────────────────────────

class TaskType(str, Enum):
    """Primary task a model was trained or fine-tuned for."""

    # Language
    TEXT_GENERATION        = "text-generation"
    TEXT_CLASSIFICATION    = "text-classification"
    TEXT_SUMMARIZATION     = "text-summarization"
    QUESTION_ANSWERING     = "question-answering"
    TRANSLATION            = "translation"
    NAMED_ENTITY_RECOGNITION = "named-entity-recognition"
    SENTIMENT_ANALYSIS     = "sentiment-analysis"

    # Code
    CODE_GENERATION        = "code-generation"
    CODE_COMPLETION        = "code-completion"

    # Multimodal
    IMAGE_GENERATION       = "image-generation"
    IMAGE_CLASSIFICATION   = "image-classification"
    IMAGE_CAPTIONING       = "image-captioning"
    VISUAL_QA              = "visual-question-answering"
    SPEECH_TO_TEXT         = "speech-to-text"
    TEXT_TO_SPEECH         = "text-to-speech"

    # Embedding / retrieval
    EMBEDDING              = "embedding"
    RERANKING              = "reranking"

    # Reasoning / agents
    REASONING              = "reasoning"
    FUNCTION_CALLING       = "function-calling"
    INSTRUCTION_FOLLOWING  = "instruction-following"

    OTHER                  = "other"


class Architecture(str, Enum):
    """Model architecture family."""

    TRANSFORMER    = "transformer"
    ENCODER_ONLY   = "encoder-only"        # BERT-style
    DECODER_ONLY   = "decoder-only"        # GPT-style
    ENCODER_DECODER = "encoder-decoder"    # T5-style
    MAMBA          = "mamba"
    DIFFUSION      = "diffusion"
    CNN            = "cnn"
    RNN            = "rnn"
    HYBRID         = "hybrid"
    MIXTURE_OF_EXPERTS = "mixture-of-experts"
    OTHER          = "other"


class Modality(str, Enum):
    TEXT       = "text"
    IMAGE      = "image"
    AUDIO      = "audio"
    VIDEO      = "video"
    MULTIMODAL = "multimodal"
    CODE       = "code"
    EMBEDDING  = "embedding"


# ──────────────────────────────────────────────────────────────────────────────
# Supporting models
# ──────────────────────────────────────────────────────────────────────────────

class TrainingDataRef(BaseModel):
    """Lightweight reference to a training dataset."""

    name: str
    url: str | None = None
    hash: str | None = Field(
        None,
        description="SHA-256 of a canonical dataset snapshot (e.g. manifest file)",
    )
    size_tokens: int | None = None
    cutoff_date: str | None = Field(
        None,
        description="ISO-8601 date string: knowledge cutoff for this dataset slice",
    )


class ModelCapabilities(BaseModel):
    """What the model can do at runtime."""

    modalities: list[Modality] = Field(default_factory=list)
    context_length: int | None = Field(None, description="Maximum input context in tokens")
    supports_function_calling: bool = False
    supports_streaming: bool = False
    languages: list[str] = Field(
        default_factory=list,
        description="ISO-639-1 language codes, e.g. ['en', 'ar', 'fr']",
    )
    benchmark_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Benchmark name → score, e.g. {'MMLU': 0.72, 'HumanEval': 0.54}",
    )


# ──────────────────────────────────────────────────────────────────────────────
# ModelPassport
# ──────────────────────────────────────────────────────────────────────────────

class ModelPassport(BasePassport):
    """
    Full identity and provenance document for an AI model.

    Inherits from BasePassport:
        id, name, version, description, artifact_hash, parent_hash,
        creator, license, license_url, status, tags, metadata,
        created_at, updated_at

    Adds:
        model_id        External / human-readable identifier.
        task_type       Primary task this model addresses.
        architecture    Architecture family.
        … and rich metadata fields below.
    """

    passport_type: str = Field(default="model", frozen=True)

    # ── Core required fields ──────────────────────────────────────────────────

    model_id: str | None = Field(
        None,
        description=(
            "External identifier for this model, e.g. 'meta-llama/Llama-3-8B-Instruct' "
            "or an internal slug.  Distinct from the passport `id` which is "
            "forkit-computed from canonical fields + artifact_hash."
        ),
    )
    task_type: TaskType = Field(
        ...,
        description="Primary task this model was trained or fine-tuned for",
    )
    architecture: Architecture = Field(
        ...,
        description="Model architecture family",
    )

    # ── Artifact details ──────────────────────────────────────────────────────
    # artifact_hash and parent_hash are defined in BasePassport.
    # The fields below provide richer context for what those hashes cover.

    artifact_files: list[str] = Field(
        default_factory=list,
        description=(
            "Relative paths of files included in the artifact_hash computation, "
            "e.g. ['model.safetensors', 'config.json', 'tokenizer.json']. "
            "Allows exact reconstruction of what was hashed."
        ),
    )
    quantization: str | None = Field(
        None,
        description="Quantization format applied to weights, e.g. 'fp16', 'int8', 'gguf-q4_k_m'",
    )

    # ── Lineage / fine-tuning ─────────────────────────────────────────────────
    # parent_hash (from BasePassport) = SHA-256 of base model weights.
    # Complement it with human-readable context:

    base_model_name: str | None = Field(
        None,
        description="Display name of the base model, e.g. 'meta-llama/Llama-3-8B'. "
                    "Informational only — parent_hash is the verifiable link.",
    )
    fine_tuning_method: str | None = Field(
        None,
        description="How the model was adapted, e.g. 'LoRA', 'full', 'RLHF', 'DPO'",
    )

    # ── Training data ─────────────────────────────────────────────────────────
    training_data: list[TrainingDataRef] = Field(default_factory=list)
    parameter_count: int | None = Field(
        None,
        description="Total parameter count",
        examples=[7_000_000_000, 70_000_000_000],
    )

    # ── Capabilities ─────────────────────────────────────────────────────────
    capabilities: ModelCapabilities = Field(default_factory=ModelCapabilities)
    usage_restrictions: list[str] = Field(
        default_factory=list,
        description="Usage restrictions from the license, e.g. ['no-commercial', 'no-military']",
    )

    # ── External links ────────────────────────────────────────────────────────
    hub_url: str | None = Field(
        None,
        description="Model hub URL (HuggingFace, ModelScope, Ollama registry, etc.)",
    )
    paper_url: str | None = Field(None, description="arXiv or paper URL")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name":          "llama-3-8b-instruct-support-ft",
                "version":       "1.0.0",
                "model_id":      "forkit/llama-3-8b-instruct-support-ft",
                "task_type":     "text-generation",
                "architecture":  "decoder-only",
                "artifact_hash": "a" * 64,
                "parent_hash":   "b" * 64,
                "license":       "llama3",
                "creator": {
                    "name":         "Hamza",
                    "organization": "ForkIt",
                },
                "capabilities": {
                    "modalities":                ["text"],
                    "context_length":            8192,
                    "supports_function_calling": True,
                },
            }
        }
    }
