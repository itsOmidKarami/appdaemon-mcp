"""Unit tests for Pydantic models."""

from appdaemon_mcp.models import AppConfig, AppEntity, AppInfo, LogEntry


def test_app_info_parsing():
    data = {"version": "4.4.2", "timezone": "UTC"}
    info = AppInfo(**data)
    assert info.version == "4.4.2"
    assert info.timezone == "UTC"


def test_app_entity_parsing():
    data = {
        "entity_id": "light.kitchen",
        "state": "on",
        "attributes": {"brightness": 255},
        "last_changed": "2024-03-08T12:00:00Z",
    }
    entity = AppEntity(**data)
    assert entity.entity_id == "light.kitchen"
    assert entity.state == "on"
    assert entity.attributes["brightness"] == 255


def test_log_entry_parsing():
    data = {"ts": 1709900000.0, "type": "INFO", "message": "App initialized"}
    entry = LogEntry(**data)
    assert entry.type == "INFO"
    assert entry.message == "App initialized"


def test_app_config_parsing():
    data = {
        "name": "my_app",
        "module": "my_module",
        "class": "MyClass",
        "args": {"param1": "value1"},
    }
    config = AppConfig(**data)
    assert config.name == "my_app"
    assert config.module == "my_module"
    assert config.class_name == "MyClass"
    assert config.args["param1"] == "value1"
