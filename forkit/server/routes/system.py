"""System/bootstrap routes for the local forkit service."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ... import __version__
from ...registry.local import LocalRegistry
from ..config import ServerSettings
from ..deps import get_registry, get_settings

router = APIRouter(tags=["system"])
_SETTINGS_DEP = Depends(get_settings)
_REGISTRY_DEP = Depends(get_registry)


@router.get("/")
def service_info(
    settings: ServerSettings = _SETTINGS_DEP,
    registry: LocalRegistry = _REGISTRY_DEP,
) -> dict[str, object]:
    """Basic service metadata without exposing local filesystem paths."""
    return {
        "service": "forkit-local-service",
        "version": __version__,
        "status": "ok",
        "registry": {
            "initialized": registry.models_dir.exists() and registry.agents_dir.exists(),
            "storage_backend": "local-filesystem",
        },
        "docs": {
            "openapi": settings.openapi_url,
            "swagger": settings.docs_url,
            "redoc": settings.redoc_url,
        },
        "sync": {
            "backend": settings.sync_backend,
            "auth_enabled": settings.sync_bearer_token is not None,
            "postgres_schema": settings.sync_postgres_schema if settings.sync_backend == "postgres" else None,
        },
    }


@router.get("/healthz")
def health(
    settings: ServerSettings = _SETTINGS_DEP,
    registry: LocalRegistry = _REGISTRY_DEP,
) -> dict[str, object]:
    """Liveness check for the local service process."""
    return {
        "status": "ok",
        "initialized": registry.models_dir.exists() and registry.agents_dir.exists(),
    }


@router.get("/readyz")
def ready(
    settings: ServerSettings = _SETTINGS_DEP,
    registry: LocalRegistry = _REGISTRY_DEP,
) -> dict[str, object]:
    """Readiness check for the local registry bootstrap."""
    return {
        "status": "ready",
        "index_db_exists": registry.db_path.exists(),
        "models_dir_exists": registry.models_dir.exists(),
        "agents_dir_exists": registry.agents_dir.exists(),
        "outbox_exists": registry.outbox_path.exists(),
        "sync_state_exists": registry.sync_state_path.exists(),
        "sync_batches_exists": registry.sync_batches_path.exists(),
        "sync_inbox_exists": registry.sync_inbox_dir.exists(),
    }
