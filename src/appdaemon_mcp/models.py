"""Pydantic models for AppDaemon API."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AppInfo(BaseModel):
    """AppDaemon system overview information."""

    version: str
    timezone: str
    status: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None


class AppEntity(BaseModel):
    """Represents a single entity in AppDaemon's state."""

    model_config = ConfigDict(extra="ignore")

    entity_id: str | None = None
    state: Any
    attributes: dict[str, Any] = Field(default_factory=dict)
    last_changed: str | None = None
    last_updated: str | None = None
    namespace: str | None = None


class LogEntry(BaseModel):
    """A single log entry from AppDaemon."""

    ts: float | str
    type: str
    message: str
    name: str | None = None


class AppConfig(BaseModel):
    """Configuration for an AppDaemon app."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    name: str
    module: str
    class_name: str = Field(alias="class")
    dependencies: list[str] = Field(default_factory=list)
    disable: bool = False
    args: dict[str, Any] = Field(default_factory=dict)
