"""Configuration for the local forkit service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ServerSettings:
    """Runtime settings for the local FastAPI service."""

    registry_root: Path = Path("~/.forkit/registry").expanduser().resolve()
    host: str = "127.0.0.1"
    port: int = 8000
    title: str = "forkit local service"
    description: str = "Local HTTP service for the forkit passport registry."
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    @classmethod
    def from_env(cls) -> "ServerSettings":
        """Build settings from environment variables when present."""
        registry_root = Path(
            os.getenv("FORKIT_REGISTRY_ROOT", "~/.forkit/registry")
        ).expanduser().resolve()
        host = os.getenv("FORKIT_SERVER_HOST", "127.0.0.1")
        port = int(os.getenv("FORKIT_SERVER_PORT", "8000"))
        return cls(
            registry_root=registry_root,
            host=host,
            port=port,
        )
