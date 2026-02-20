from app.core.document_registry import DocumentRegistry
from app.core.state_machine import FieldStateMachine
from app.models.session import StateMachineState


def _make_machine():
    registry = DocumentRegistry()
    config = registry.get("will_england_wales")
    state = StateMachineState()
    return FieldStateMachine(config, state), config


def test_starts_at_first_field():
    machine, config = _make_machine()
    first = machine.current_field()
    assert first is not None
    assert first.id == "testator_full_name"


def test_advance_moves_to_next_field():
    machine, config = _make_machine()
    machine.advance()
    field = machine.current_field()
    assert field is not None
    assert field.id == "testator_dob"


def test_progress_starts_at_zero():
    machine, _ = _make_machine()
    assert machine.progress_percentage() == 0


def test_progress_increases_on_advance():
    machine, _ = _make_machine()
    machine.advance()
    assert machine.progress_percentage() > 0


def test_record_value_stores_in_collected_data():
    machine, _ = _make_machine()
    machine.record_value("testator_full_name", "Jane Smith")
    assert machine.state.collected_data["testator_full_name"] == "Jane Smith"


def test_skip_optional_field_marks_as_skipped():
    machine, _ = _make_machine()
    # Fields 0-6 are the 7 required fields before the optional substitute executor (index 7).
    # Advance 7 times: 0→1→2→3→4→5→6→7
    for _ in range(7):
        machine.advance()
    field = machine.current_field()
    assert field is not None
    assert field.id == "executor_substitute_full_name"
    machine.skip_current_field()
    assert "executor_substitute_full_name" in machine.state.skipped_fields


def test_dependent_field_skipped_when_dependency_skipped():
    machine, _ = _make_machine()
    # Advance to executor_substitute_full_name and skip it
    for _ in range(7):
        machine.advance()
    machine.skip_current_field()
    # executor_substitute_address depends on executor_substitute_full_name (not_skipped)
    # It should be auto-skipped
    field = machine.current_field()
    assert field is not None
    assert field.id != "executor_substitute_address"


def test_increment_clarification_returns_true_at_limit():
    machine, _ = _make_machine()
    machine.increment_clarification()
    machine.increment_clarification()
    give_up = machine.increment_clarification()
    assert give_up is True
