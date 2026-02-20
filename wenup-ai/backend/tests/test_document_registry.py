import pytest
from app.core.document_registry import DocumentRegistry


def test_loads_will_config():
    registry = DocumentRegistry()
    config = registry.get("will_england_wales")
    assert config.document_type_id == "will_england_wales"
    assert config.jurisdiction == "England and Wales"


def test_list_all_returns_at_least_one():
    registry = DocumentRegistry()
    all_types = registry.list_all()
    assert len(all_types) >= 1


def test_unknown_type_raises_key_error():
    registry = DocumentRegistry()
    with pytest.raises(KeyError):
        registry.get("nonexistent_type")


def test_will_config_has_required_fields():
    registry = DocumentRegistry()
    config = registry.get("will_england_wales")
    field_ids = [f.id for f in config.fields]
    assert "testator_full_name" in field_ids
    assert "residuary_beneficiaries" in field_ids
    assert "executor_primary_full_name" in field_ids
