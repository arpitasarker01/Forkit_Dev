# OSS Architecture

This repository is the open-source, local-first core of Forkit.

Its job is to make model and agent passports easy to create, inspect, verify,
store, and move between systems without requiring any hosted service.

## In Scope

These capabilities belong in OSS:

- passport schemas and deterministic `passport_id` derivation
- artifact hashing, integrity verification, and lineage
- local JSON + SQLite registry
- local HTTP service for registration, lookup, verification, lineage, and export
- generic sync contract built on `GET /export`, `POST /sync/passports`, `sync push`, and `sync pull`
- LangGraph and LangChain adapters
- self-host and local development examples
- compatibility shims needed during public API migration

## Out of Scope

These capabilities do not belong in this repository:

- tenant or workspace controls
- organization, seat, or account management
- RBAC, approvals, policy enforcement, or hosted governance workflows
- billing, plans, entitlements, or usage metering
- hosted dashboards, admin consoles, or managed multi-tenant operations
- product-specific business logic that only exists in a separate service

If a feature only makes sense when there is a centralized hosted control plane,
it should stay out of OSS.

## Boundary Rules

Contributors should follow these rules:

- Keep `passport_id` deterministic and local. Do not add hosted-only inputs to identity material.
- Keep the sync boundary protocol-based. Systems should connect through documents and HTTP contracts, not shared databases.
- Keep OSS local-first. A developer should be able to use the repo offline and still get value.
- Keep new features generic. If the behavior is only useful for one hosted deployment, it does not belong here.
- Keep remote metadata separate from passport identity. Extra labels, sync status, or deployment annotations must not rewrite the passport.

## Stable Contract

The long-term contract that should remain stable across systems is:

- passport JSON document shape
- deterministic ID rules
- lineage semantics
- generic export/import envelope shape

Storage engines can differ. Deployment models can differ. The contract should not.

## Contribution Checklist

Before merging a feature, check:

1. Does it work locally without a hosted dependency?
2. Does it preserve deterministic passport identity?
3. Does it avoid tenant, billing, or policy logic?
4. Does it connect through the existing sync contract instead of direct DB coupling?
5. Will it still make sense for a contributor running only this repository?

If the answer to any of these is no, the feature should stay outside this repo.
