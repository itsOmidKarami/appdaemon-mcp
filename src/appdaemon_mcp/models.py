"""Pydantic models for AppDaemon API."""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class AppInfo(BaseModel):
    """AppDaemon system overview information."""

    version: str
    timezone: str
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[float] = None


class AppEntity(BaseModel):
    """Represents a single entity in AppDaemon's state."""

    model_config = ConfigDict(extra="ignore")

    entity_id: str
    state: Any
    attributes: dict[str, Any] = Field(default_factory=dict)
    last_changed: Optional[str] = None
    last_updated: Optional[str] = None
    namespace: Optional[str] = None


class LogEntry(BaseModel):
    """A single log entry from AppDaemon."""

    ts: float | str
    type: str
    message: str
    name: Optional[str] = None


class AppConfig(BaseModel):
    """Configuration for an AppDaemon app."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    name: str
    module: str
    class_name: str = Field(alias="class")
    dependencies: list[str] = Field(default_factory=list)
    disable: bool = False
    args: dict[str, Any] = Field(default_factory=dict)
