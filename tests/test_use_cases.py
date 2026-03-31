"""
tests/test_use_cases.py
───────────────────────
Pytest test suite covering all 10 validated passport use cases.

These tests encode the exact behavioural invariants confirmed by the original
demo script (scripts/demo_passports.py) and must stay green across both the
dataclass backend and the optional Pydantic v2 backend.

Use-case index
──────────────
 1. Register a base model passport — basic field assignment and ID derivation
 2. Fine-tuned model with artifact_hash and parent_hash provenance
 3. Agent passport linked to a model by model_id
 4. artifact_hash drives the passport ID (same metadata, different hash → different ID)
 5. Hash a real artifact file/directory → attach to passport → tamper detection
 6. Fork an agent using parent_hash
 7. Lineage graph — ancestors and descendants
 8. Passport integrity verification — re-derive ID from content
 9. Serialise → dict → deserialise roundtrip (ModelPassport and AgentPassport)
10. Field validation — reject invalid hash values
"""

from __future__ import annotations

import json

import pytest

from forkit.domain import (
    EdgeType,
    HashEngine,
    LineageEdge,
    LineageGraph,
    LineageNode,
    NodeType,
    verify_passport_id,
)
from forkit.domain.identity import validate_hash
from forkit.schemas import (
    AgentArchitecture,
    AgentPassport,
    AgentTaskType,
    Architecture,
    LicenseType,
    ModelPassport,
    PassportStatus,
    TaskType,
)

CREATOR = {"name": "Hamza", "organization": "ForkIt"}
H = HashEngine()


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 1 — Register a base model passport
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase1_BaseModelPassport:
    """Basic field assignment and deterministic ID derivation."""

    def test_required_fields_accepted(self):
        m = ModelPassport(
            name         = "llama-3-8b-base",
            version      = "1.0.0",
            task_type    = TaskType.TEXT_GENERATION,
            architecture = Architecture.DECODER_ONLY,
            creator      = CREATOR,
            license      = LicenseType.LLAMA_3,
            model_id     = "meta-llama/Meta-Llama-3-8B",
            parameter_count = 8_000_000_000,
            status       = PassportStatus.ACTIVE,
            tags         = ["llm", "base"],
        )
        assert m.name    == "llama-3-8b-base"
        assert m.version == "1.0.0"
        assert len(m.id) == 64, "Passport ID must be a 64-char SHA-256 hex string"

    def test_id_is_64_char_hex(self, base_model):
        assert len(base_model.id) == 64
        assert all(c in "0123456789abcdef" for c in base_model.id)

    def test_short_id_is_prefix(self, base_model):
        assert base_model.short_id(12) == base_model.id[:12]

    def test_passport_type_is_model(self):
        m = ModelPassport(
            name="m", version="1.0", task_type=TaskType.EMBEDDING,
            architecture=Architecture.ENCODER_ONLY, creator=CREATOR,
        )
        assert m.passport_type == "model"

    def test_id_is_deterministic(self):
        """Same inputs must always produce the same ID."""
        kwargs = dict(
            name="det-model", version="1.0.0",
            task_type=TaskType.TEXT_GENERATION,
            architecture=Architecture.DECODER_ONLY,
            creator=CREATOR,
        )
        assert ModelPassport(**kwargs).id == ModelPassport(**kwargs).id

    def test_no_artifact_hash_by_default(self, base_model):
        assert base_model.artifact_hash is None
        assert base_model.parent_hash   is None


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 2 — Fine-tuned model with artifact_hash and parent_hash
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase2_FineTunedModel:
    """artifact_hash and parent_hash are stored correctly and validated."""

    def test_artifact_hash_stored(self):
        ah = "a" * 64
        m  = ModelPassport(
            name="ft-model", version="1.0.0",
            task_type=TaskType.INSTRUCTION_FOLLOWING,
            architecture=Architecture.DECODER_ONLY,
            creator=CREATOR, artifact_hash=ah,
        )
        assert m.artifact_hash == ah

    def test_parent_hash_stored(self):
        ah = "a" * 64
        ph = "b" * 64
        m  = ModelPassport(
            name="ft-model", version="1.0.0",
            task_type=TaskType.INSTRUCTION_FOLLOWING,
            architecture=Architecture.DECODER_ONLY,
            creator=CREATOR, artifact_hash=ah, parent_hash=ph,
        )
        assert m.parent_hash == ph

    def test_artifact_hash_uppercased_is_normalised(self):
        """Uppercase hex should be normalised to lowercase."""
        m = ModelPassport(
            name="m", version="1.0", task_type=TaskType.TEXT_GENERATION,
            architecture=Architecture.DECODER_ONLY, creator=CREATOR,
            artifact_hash="A" * 64,
        )
        assert m.artifact_hash == "a" * 64

    def test_lineage_fields_stored(self):
        m = ModelPassport(
            name="ft", version="1.0.0",
            task_type=TaskType.INSTRUCTION_FOLLOWING,
            architecture=Architecture.DECODER_ONLY,
            creator=CREATOR, artifact_hash="c" * 64,
            base_model_name="meta-llama/Meta-Llama-3-8B",
            fine_tuning_method="LoRA",
        )
        assert m.base_model_name    == "meta-llama/Meta-Llama-3-8B"
        assert m.fine_tuning_method == "LoRA"

    def test_file_hash_roundtrip(self, weights_file):
        ah = H.hash_file(weights_file)
        m  = ModelPassport(
            name="ft", version="1.0.0",
            task_type=TaskType.INSTRUCTION_FOLLOWING,
            architecture=Architecture.DECODER_ONLY,
            creator=CREATOR, artifact_hash=ah,
        )
        assert m.artifact_hash == ah
        assert H.verify_file(weights_file, m.artifact_hash)


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 3 — Agent passport linked to a model
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase3_AgentPassport:
    """Agent passport construction with model_id link."""

    @pytest.fixture()
    def model_id(self, base_model) -> str:
        return base_model.id

    def test_agent_registered_with_model_id(self, model_id):
        agent = AgentPassport(
            name         = "support-agent",
            version      = "1.0.0",
            model_id     = model_id,
            task_type    = AgentTaskType.CUSTOMER_SUPPORT,
            architecture = AgentArchitecture.REACT,
            creator      = CREATOR,
        )
        assert agent.model_id == model_id
        assert len(agent.id)  == 64

    def test_agent_passport_type(self, model_id):
        a = AgentPassport(
            name="a", version="1.0", model_id=model_id,
            task_type=AgentTaskType.CODE_ASSISTANT,
            architecture=AgentArchitecture.COT,
            creator=CREATOR,
        )
        assert a.passport_type == "agent"

    def test_tools_coerced_from_dicts(self, model_id):
        agent = AgentPassport(
            name="a", version="1.0", model_id=model_id,
            task_type=AgentTaskType.CUSTOMER_SUPPORT,
            architecture=AgentArchitecture.REACT,
            creator=CREATOR,
            tools=[
                {"name": "kb_search",     "version": "1.2.0"},
                {"name": "ticket_create", "version": "1.0.0"},
            ],
        )
        assert len(agent.tools) == 2
        assert agent.tools[0].name == "kb_search"

    def test_agent_id_differs_from_model_id(self, base_model, model_id):
        agent = AgentPassport(
            name="a", version="1.0", model_id=model_id,
            task_type=AgentTaskType.CUSTOMER_SUPPORT,
            architecture=AgentArchitecture.REACT,
            creator=CREATOR,
        )
        assert agent.id != base_model.id


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 4 — artifact_hash drives the passport ID
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase4_ArtifactHashDrivesId:
    """Two passports with the same metadata but different artifact_hash must differ."""

    BASE = dict(
        name="same-model", version="1.0.0",
        task_type=TaskType.TEXT_GENERATION,
        architecture=Architecture.DECODER_ONLY,
        creator=CREATOR,
    )

    def test_no_hash_vs_hash_differ(self):
        m_no  = ModelPassport(**self.BASE)
        m_has = ModelPassport(**self.BASE, artifact_hash="a" * 64)
        assert m_no.id != m_has.id

    def test_different_hashes_differ(self):
        ma = ModelPassport(**self.BASE, artifact_hash="a" * 64)
        mb = ModelPassport(**self.BASE, artifact_hash="b" * 64)
        assert ma.id != mb.id

    def test_same_hash_is_deterministic(self):
        ma1 = ModelPassport(**self.BASE, artifact_hash="a" * 64)
        ma2 = ModelPassport(**self.BASE, artifact_hash="a" * 64)
        assert ma1.id == ma2.id

    def test_version_change_changes_id(self):
        m1 = ModelPassport(**{**self.BASE, "version": "1.0.0"})
        m2 = ModelPassport(**{**self.BASE, "version": "2.0.0"})
        assert m1.id != m2.id


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 5 — Hash a real artifact → attach to passport → tamper detection
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase5_ArtifactHashing:
    """hash_artifact and verify_artifact work on files and directories."""

    def test_hash_file_and_verify(self, weights_file):
        ah = H.hash_artifact(weights_file)
        assert len(ah) == 64
        assert H.verify_artifact(weights_file, ah)

    def test_hash_directory_and_verify(self, model_dir):
        ah = H.hash_artifact(model_dir)
        assert H.verify_artifact(model_dir, ah)

    def test_tamper_detected(self, model_dir):
        ah = H.hash_artifact(model_dir)
        (model_dir / "model.safetensors").write_bytes(b"[TAMPERED]" * 5000)
        assert not H.verify_artifact(model_dir, ah)

    def test_hash_attached_to_passport(self, model_dir):
        ah = H.hash_artifact(model_dir)
        m  = ModelPassport(
            name="m", version="1.0", task_type=TaskType.TEXT_GENERATION,
            architecture=Architecture.DECODER_ONLY,
            creator=CREATOR, artifact_hash=ah,
        )
        assert m.artifact_hash == ah
        assert H.verify_artifact(model_dir, m.artifact_hash)

    def test_weights_only_vs_all_files_differ(self, model_dir):
        all_h     = H.hash_artifact(model_dir)
        weights_h = H.hash_model_artifact(model_dir, include_config=False)
        # All files includes README.md; weights-only does not — so they differ
        assert all_h != weights_h


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 6 — Fork an agent (parent_hash chain)
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase6_AgentFork:
    """parent_hash on a forked agent equals the parent agent's artifact_hash."""

    @pytest.fixture()
    def parent_agent(self, base_model):
        config_hash = H.hash_config({
            "system_prompt_hash": H.hash_system_prompt("You are a support agent."),
            "tools":  ["kb_search", "ticket_create"],
            "temperature": 0.3,
        })
        return AgentPassport(
            name="parent-agent", version="1.0.0",
            model_id=base_model.id,
            task_type=AgentTaskType.CUSTOMER_SUPPORT,
            architecture=AgentArchitecture.REACT,
            creator=CREATOR,
            artifact_hash=config_hash,
        )

    @pytest.fixture()
    def forked_agent(self, base_model, parent_agent):
        forked_config_hash = H.hash_config({
            "system_prompt_hash": H.hash_system_prompt(
                "You are a bilingual support agent."
            ),
            "tools":  ["kb_search", "ticket_create", "translation"],
            "temperature": 0.3,
        })
        return AgentPassport(
            name="forked-agent", version="2.0.0",
            model_id=base_model.id,
            task_type=AgentTaskType.CUSTOMER_SUPPORT,
            architecture=AgentArchitecture.REACT,
            creator=CREATOR,
            artifact_hash=forked_config_hash,
            parent_hash=parent_agent.artifact_hash,
            parent_agent_name=parent_agent.name,
            fork_reason="Added Arabic + translation tool",
        )

    def test_parent_hash_equals_parent_artifact_hash(self, parent_agent, forked_agent):
        assert forked_agent.parent_hash == parent_agent.artifact_hash

    def test_forked_agent_has_different_id(self, parent_agent, forked_agent):
        assert parent_agent.id != forked_agent.id

    def test_fork_reason_stored(self, forked_agent):
        assert forked_agent.fork_reason == "Added Arabic + translation tool"

    def test_parent_agent_name_stored(self, parent_agent, forked_agent):
        assert forked_agent.parent_agent_name == parent_agent.name


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 7 — Lineage graph: ancestors and descendants
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase7_LineageGraph:
    """LineageGraph correctly tracks ancestry and descendants."""

    @pytest.fixture()
    def graph_and_passports(self, base_creator):
        base = ModelPassport(
            name="base", version="1.0", task_type=TaskType.TEXT_GENERATION,
            architecture=Architecture.DECODER_ONLY, creator=base_creator,
        )
        ft = ModelPassport(
            name="finetuned", version="1.0", task_type=TaskType.INSTRUCTION_FOLLOWING,
            architecture=Architecture.DECODER_ONLY, creator=base_creator,
            artifact_hash="a" * 64,
        )
        agent = AgentPassport(
            name="agent", version="1.0", model_id=ft.id,
            task_type=AgentTaskType.CUSTOMER_SUPPORT,
            architecture=AgentArchitecture.REACT, creator=base_creator,
        )

        g = LineageGraph()
        g.add_node(LineageNode(base.id, NodeType.MODEL, base.name, base.version))
        g.add_node(LineageNode(ft.id,   NodeType.MODEL, ft.name,   ft.version))
        g.add_node(LineageNode(agent.id, NodeType.AGENT, agent.name, agent.version))

        g.add_edge(LineageEdge(ft.id,    base.id, EdgeType.DERIVED_FROM, "LoRA"))
        g.add_edge(LineageEdge(agent.id, ft.id,   EdgeType.BUILT_ON))

        return g, base, ft, agent

    def test_ancestors_of_agent(self, graph_and_passports):
        g, base, ft, agent = graph_and_passports
        anc_ids = {n.id for n in g.ancestors(agent.id)}
        assert ft.id   in anc_ids
        assert base.id in anc_ids
        assert agent.id not in anc_ids  # self excluded

    def test_descendants_of_base(self, graph_and_passports):
        g, base, ft, agent = graph_and_passports
        desc_ids = {n.id for n in g.descendants(base.id)}
        assert ft.id    in desc_ids
        assert agent.id in desc_ids
        assert base.id  not in desc_ids  # self excluded

    def test_cycle_rejected(self, graph_and_passports):
        g, base, ft, agent = graph_and_passports
        with pytest.raises(ValueError, match="cycle"):
            g.add_edge(LineageEdge(base.id, agent.id, EdgeType.BUILT_ON))

    def test_summary_counts(self, graph_and_passports):
        g, base, ft, agent = graph_and_passports
        summary = g.summary()
        assert "3 nodes" in summary
        assert "2 models" in summary
        assert "1 agents" in summary

    def test_serialise_roundtrip(self, graph_and_passports, tmp_path):
        g, base, ft, agent = graph_and_passports
        path = tmp_path / "lineage.json"
        g.save(path)
        g2 = LineageGraph.load(path)
        assert {n.id for n in g2.ancestors(agent.id)} == {n.id for n in g.ancestors(agent.id)}


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 8 — Passport integrity verification
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase8_IntegrityVerification:
    """Re-deriving a passport ID from its content must match the stored ID."""

    def test_verify_valid_passport(self, base_model):
        result = verify_passport_id(base_model.to_dict())
        assert result["valid"] is True
        assert result["reason"] == "ok"

    def test_stripped_id_rederived(self, base_model):
        d = {k: v for k, v in base_model.to_dict().items() if k != "id"}
        restored = ModelPassport.from_dict(d)
        assert restored.id == base_model.id

    def test_tampered_name_changes_id(self, base_model):
        d          = {k: v for k, v in base_model.to_dict().items() if k != "id"}
        d["name"]  = "TAMPERED"
        tampered   = ModelPassport.from_dict(d)
        assert tampered.id != base_model.id

    def test_tampered_artifact_hash_changes_id(self, base_model):
        d = base_model.to_dict()
        d.pop("id")
        d["artifact_hash"] = "f" * 64
        altered = ModelPassport.from_dict(d)
        assert altered.id != base_model.id

    def test_verify_id_mismatch_detected(self, base_model):
        d = base_model.to_dict()
        d["id"] = "deadbeef" + "0" * 56   # wrong ID
        result  = verify_passport_id(d)
        assert result["valid"]  is False
        assert result["reason"] == "id_mismatch"


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 9 — Serialise → dict → deserialise roundtrip
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase9_Roundtrip:
    """to_dict() / from_dict() / JSON serialisation must preserve all fields and ID."""

    def test_model_passport_roundtrip(self, base_model):
        restored = ModelPassport.from_dict(base_model.to_dict())
        assert restored.id      == base_model.id
        assert restored.name    == base_model.name
        assert restored.version == base_model.version

    def test_model_json_roundtrip(self, base_model):
        serialised = json.dumps(base_model.to_dict(), default=str)
        restored   = ModelPassport.from_dict(json.loads(serialised))
        assert restored.id           == base_model.id
        assert restored.artifact_hash == base_model.artifact_hash

    def test_agent_passport_roundtrip(self, base_model):
        agent = AgentPassport(
            name="ag", version="1.0", model_id=base_model.id,
            task_type=AgentTaskType.CUSTOMER_SUPPORT,
            architecture=AgentArchitecture.REACT,
            creator=CREATOR,
            tools=[{"name": "search", "version": "1.0"}],
        )
        restored = AgentPassport.from_dict(agent.to_dict())
        assert restored.id      == agent.id
        assert restored.model_id == agent.model_id
        assert len(restored.tools) == 1
        assert restored.tools[0].name == "search"

    def test_enum_values_serialised_as_strings(self, base_model):
        d = base_model.to_dict()
        assert isinstance(d["task_type"],    str)
        assert isinstance(d["architecture"], str)
        assert isinstance(d["license"],      str)
        assert isinstance(d["status"],       str)

    def test_model_with_artifact_hash_roundtrip(self):
        m = ModelPassport(
            name="m", version="1.0", task_type=TaskType.TEXT_GENERATION,
            architecture=Architecture.DECODER_ONLY, creator=CREATOR,
            artifact_hash="c" * 64, parent_hash="d" * 64,
        )
        r = ModelPassport.from_dict(m.to_dict())
        assert r.id            == m.id
        assert r.artifact_hash == m.artifact_hash
        assert r.parent_hash   == m.parent_hash


# ═══════════════════════════════════════════════════════════════════════════════
# Use case 10 — Field validation — reject invalid hash values
# ═══════════════════════════════════════════════════════════════════════════════

class TestUseCase10_FieldValidation:
    """Invalid hash strings must be rejected; valid ones accepted."""

    BASE = dict(
        name="m", version="1.0",
        task_type=TaskType.TEXT_GENERATION,
        architecture=Architecture.DECODER_ONLY,
        creator=CREATOR,
    )

    def test_valid_lowercase_hex_accepted(self):
        m = ModelPassport(**self.BASE, artifact_hash="a" * 64)
        assert m.artifact_hash == "a" * 64

    def test_uppercase_hex_normalised(self):
        """validate_hash normalises uppercase to lowercase."""
        result = validate_hash("A" * 64)
        assert result == "a" * 64

    def test_too_short_rejected(self):
        with pytest.raises((ValueError, Exception)):
            ModelPassport(**self.BASE, artifact_hash="abc123")

    def test_non_hex_rejected(self):
        with pytest.raises((ValueError, Exception)):
            ModelPassport(**self.BASE, artifact_hash="z" * 64)

    def test_non_hex_rejected_via_validate_hash(self):
        with pytest.raises(ValueError):
            validate_hash("z" * 64)

    def test_too_short_rejected_via_validate_hash(self):
        with pytest.raises(ValueError):
            validate_hash("abc")

    def test_is_valid_hash_strict(self):
        """is_valid_hash is a strict check — uppercase returns False."""
        assert HashEngine.is_valid_hash("a" * 64)   is True
        assert HashEngine.is_valid_hash("A" * 64)   is False   # strict — no normalisation
        assert HashEngine.is_valid_hash("abc")      is False
        assert HashEngine.is_valid_hash("z" * 64)   is False

    def test_invalid_version_rejected(self):
        with pytest.raises((ValueError, Exception)):
            ModelPassport(**{**self.BASE, "version": "1"})

    def test_valid_2part_version_accepted(self):
        m = ModelPassport(**{**self.BASE, "version": "1.0"})
        assert m.version == "1.0"

    def test_valid_3part_version_accepted(self):
        m = ModelPassport(**{**self.BASE, "version": "1.0.0"})
        assert m.version == "1.0.0"
