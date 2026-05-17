"""
Minimal deterministic identity demo for Hacker News readers.

Run:
  python examples/deterministic_identity_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forkit.domain import verify_passport_id
from forkit.schemas import Architecture, ModelPassport, TaskType

CREATOR = {"name": "Forkit Demo", "organization": "Forkit"}

BASE = dict(
    name="passport-demo-model",
    version="1.0.0",
    task_type=TaskType.TEXT_GENERATION,
    architecture=Architecture.DECODER_ONLY,
    creator=CREATOR,
)


def show(label: str, passport: ModelPassport) -> None:
    print(f"{label:<24} {passport.id}")


def main() -> None:
    first = ModelPassport(**BASE, artifact_hash="a" * 64)
    repeat = ModelPassport(**BASE, artifact_hash="a" * 64)
    changed_artifact = ModelPassport(**BASE, artifact_hash="b" * 64)
    changed_creator = ModelPassport(
        **{**BASE, "creator": {"name": "Forkit Demo", "organization": "Another Org"}},
        artifact_hash="a" * 64,
    )

    print("Forkit deterministic passport demo\n")
    show("same input", first)
    show("same input again", repeat)
    show("changed artifact", changed_artifact)
    show("changed creator", changed_creator)

    print("\nVerification:")
    print(verify_passport_id(first.to_dict()))

    print("\nExpectation:")
    print("- identical stable fields => identical passport_id")
    print("- changing artifact or creator => different passport_id")


if __name__ == "__main__":
    main()
