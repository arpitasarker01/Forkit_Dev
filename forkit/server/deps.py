"""Shared dependencies for HTTP handlers."""

from __future__ import annotations

from fastapi import Request

from ..registry.local import LocalRegistry
from .config import ServerSettings


def get_registry(request: Request) -> LocalRegistry:
    return request.app.state.registry


def get_settings(request: Request) -> ServerSettings:
    return request.app.state.settings
