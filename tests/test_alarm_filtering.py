"""test_alarm_filtering.py – Tests for duplicate alarm marking logic."""
import pytest
from app.models import (
    RawDatasetFile, TepRun, SensorVariable, VariableStatistic, AlarmEvent
)
from app.services.alarm_filter import mark_duplicate_alarms


def _make_alarm(db, run_id, variable_id, time_step, alarm_type='warning_high_alarm', severity='warning'):
    a = AlarmEvent(
        run_id=run_id,
        time_step=time_step,
        variable_id=variable_id,
        component_key='industrial_process',
        alarm_type=alarm_type,
        severity=severity,
        message=f'test alarm at t={time_step}',
    )
    db.session.add(a)
    return a


def test_duplicate_alarms_within_window_are_marked(app, db):
    """Alarms on the same variable within the duplicate window must be marked duplicate."""
    with app.app_context():
        file = RawDatasetFile(file_name='dup_test.RData', file_path='Data/dup_test.RData', dataset_role='faulty_testing')
        db.session.add(file)
        db.session.flush()
        run = TepRun(dataset_file_id=file.id, run_id='dup-0-1', dataset_role='faulty_testing',
                     fault_id=1, fault_label='fault_1', is_faulty=True)
        db.session.add(run)
        db.session.flush()
        var = SensorVariable(variable_name='xmeas_dup', component_key='industrial_process')
        db.session.add(var)
        db.session.flush()

        # First alarm at t=10, second at t=12 (within window=3)
        a1 = _make_alarm(db, run.id, var.id, time_step=10)
        a2 = _make_alarm(db, run.id, var.id, time_step=12)  # within window
        db.session.commit()

        mark_duplicate_alarms(window=3)

        db.session.refresh(a1)
        db.session.refresh(a2)
        assert a1.is_duplicate is False, "First alarm must not be duplicate"
        assert a2.is_duplicate is True, "Second alarm within window must be duplicate"


def test_alarms_outside_window_are_not_duplicates(app, db):
    """Alarms separated by more than the window must both be unique."""
    with app.app_context():
        file = RawDatasetFile(file_name='nodup_test.RData', file_path='Data/nodup_test.RData', dataset_role='faulty_testing')
        db.session.add(file)
        db.session.flush()
        run = TepRun(dataset_file_id=file.id, run_id='nodup-0-1', dataset_role='faulty_testing',
                     fault_id=1, fault_label='fault_1', is_faulty=True)
        db.session.add(run)
        db.session.flush()
        var = SensorVariable(variable_name='xmeas_nodup', component_key='industrial_process')
        db.session.add(var)
        db.session.flush()

        a1 = _make_alarm(db, run.id, var.id, time_step=10)
        a2 = _make_alarm(db, run.id, var.id, time_step=20)  # 10 steps apart > window=3
        db.session.commit()

        mark_duplicate_alarms(window=3)

        db.session.refresh(a1)
        db.session.refresh(a2)
        assert a1.is_duplicate is False
        assert a2.is_duplicate is False


def test_different_variables_not_marked_duplicate(app, db):
    """Alarms on different variables at same time must not be marked duplicate."""
    with app.app_context():
        file = RawDatasetFile(file_name='diffvar_test.RData', file_path='Data/diffvar_test.RData', dataset_role='faulty_testing')
        db.session.add(file)
        db.session.flush()
        run = TepRun(dataset_file_id=file.id, run_id='diffvar-0-1', dataset_role='faulty_testing',
                     fault_id=1, fault_label='fault_1', is_faulty=True)
        db.session.add(run)
        db.session.flush()
        var1 = SensorVariable(variable_name='xmeas_dv1', component_key='industrial_process')
        var2 = SensorVariable(variable_name='xmeas_dv2', component_key='cooling_system')
        db.session.add_all([var1, var2])
        db.session.flush()

        a1 = _make_alarm(db, run.id, var1.id, time_step=5)
        a2 = _make_alarm(db, run.id, var2.id, time_step=5)
        db.session.commit()

        mark_duplicate_alarms(window=3)

        db.session.refresh(a1)
        db.session.refresh(a2)
        assert a1.is_duplicate is False
        assert a2.is_duplicate is False
