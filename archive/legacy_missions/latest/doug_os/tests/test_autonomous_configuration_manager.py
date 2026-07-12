import pytest
from discovery.autonomous_configuration_manager import AutonomousConfigurationManager, ConfigEntry


def test_set_and_get_config():
    mgr = AutonomousConfigurationManager()
    mgr.set_config("db_host", "localhost")
    val = mgr.get_config("db_host")
    assert val == "localhost"


def test_get_missing_key():
    mgr = AutonomousConfigurationManager()
    assert mgr.get_config("nonexistent") is None


def test_config_versioning():
    mgr = AutonomousConfigurationManager()
    mgr.set_config("key", "v1")
    mgr.set_config("key", "v2")
    assert mgr.get_config("key") == "v2"


def test_rollback_to_previous():
    mgr = AutonomousConfigurationManager()
    mgr.set_config("key", "original")
    mgr.set_config("key", "updated")
    config = mgr._configs["key"]
    versions = mgr._versions.get(config.id, [])
    # Should have one version (from first update); rollback to it
    assert len(versions) >= 1
    v_num = versions[0].version
    ok = mgr.rollback("key", v_num)
    assert ok is True


def test_rollback_unknown_version():
    mgr = AutonomousConfigurationManager()
    mgr.set_config("key", "val")
    assert mgr.rollback("key", 999) is False


def test_rollback_unknown_key():
    mgr = AutonomousConfigurationManager()
    assert mgr.rollback("nonexistent", 1) is False


def test_add_listener_fires_on_set():
    mgr = AutonomousConfigurationManager()
    changes = []
    mgr.add_listener(lambda k, v: changes.append((k, v)))
    mgr.set_config("key", "newval")
    assert len(changes) == 1
    assert changes[0] == ("key", "newval")


def test_checksum_stored():
    mgr = AutonomousConfigurationManager()
    mgr.set_config("secured", "secret")
    entry = mgr._configs.get("secured")
    assert entry is not None
    assert entry.checksum != ""


def test_sensitive_config_hidden():
    mgr = AutonomousConfigurationManager()
    mgr.set_config("api_key", "super_secret", sensitive=True)
    entry = mgr._configs.get("api_key")
    d = entry.to_dict()
    assert d["value"] == "***"


def test_multiple_keys():
    mgr = AutonomousConfigurationManager()
    mgr.set_config("a", 1)
    mgr.set_config("b", 2)
    assert mgr.get_config("a") == 1
    assert mgr.get_config("b") == 2
