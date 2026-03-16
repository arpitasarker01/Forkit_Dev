"""
Shared fixtures for forkit test suite.

All tests import from forkit (the new package).
The forkit_core package is kept intact for reference but is not tested here.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repo root is on sys.path so `import forkit` works from any cwd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import tempfile

from forkit.schemas import (
    AgentPassport,
    AgentArchitecture,
    AgentTaskType,
    Architecture,
    CreatorInfo,
    LicenseType,
    ModelPassport,
    PassportStatus,
    TaskType,
)
from forkit.domain import HashEngine


CREATOR_DICT = {"name": "Hamza", "organization": "ForkIt"}
CREATOR      = CreatorInfo(name="Hamza", organization="ForkIt")


@pytest.fixture()
def base_creator() -> dict:
    return CREATOR_DICT


@pytest.fixture()
def minimal_model_kwargs(base_creator) -> dict:
    """Minimal valid kwargs to construct a ModelPassport."""
    return dict(
        name         = "test-model",
        version      = "1.0.0",
        task_type    = TaskType.TEXT_GENERATION,
        architecture = Architecture.DECODER_ONLY,
        creator      = base_creator,
    )


@pytest.fixture()
def base_model(minimal_model_kwargs) -> ModelPassport:
    return ModelPassport(**minimal_model_kwargs)


@pytest.fixture()
def weights_file(tmp_path) -> Path:
    """A temporary .safetensors file with deterministic content."""
    p = tmp_path / "model.safetensors"
    p.write_bytes(b"[simulated weights]" * 1000)
    return p


@pytest.fixture()
def model_dir(tmp_path) -> Path:
    """A temporary model directory with weights + config files."""
    (tmp_path / "model.safetensors").write_bytes(b"[weights]" * 5000)
    (tmp_path / "config.json").write_text('{"hidden_size": 4096}')
    (tmp_path / "tokenizer.json").write_text('{"version": "1.0"}')
    (tmp_path / "README.md").write_text("# Model card")
    return tmp_path
