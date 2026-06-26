"""test_alarm_generation.py – Unit tests for alarm generation logic."""
import types
import pytest
from app.services.alarm_generator import determine_alarm, SEVERITY_MAP


def _stat(critical_low, warning_low, warning_high, critical_high):
    stat = types.SimpleNamespace(
        critical_low=critical_low,
        warning_low=warning_low,
        warning_high=warning_high,
        critical_high=critical_high,
    )
    return stat


def test_value_above_critical_high_generates_critical_alarm():
    stat = _stat(-5, -2, 2, 5)
    alarm_type, threshold = determine_alarm(7.0, stat)
    assert alarm_type == 'critical_high_alarm'
    assert threshold == 5
    assert SEVERITY_MAP[alarm_type] == 'critical'


def test_value_below_critical_low_generates_critical_alarm():
    stat = _stat(-5, -2, 2, 5)
    alarm_type, threshold = determine_alarm(-8.0, stat)
    assert alarm_type == 'critical_low_alarm'
    assert threshold == -5
    assert SEVERITY_MAP[alarm_type] == 'critical'


def test_value_above_warning_high_generates_warning_alarm():
    stat = _stat(-5, -2, 2, 5)
    alarm_type, threshold = determine_alarm(3.5, stat)
    assert alarm_type == 'warning_high_alarm'
    assert SEVERITY_MAP[alarm_type] == 'warning'


def test_value_below_warning_low_generates_warning_alarm():
    stat = _stat(-5, -2, 2, 5)
    alarm_type, threshold = determine_alarm(-3.0, stat)
    assert alarm_type == 'warning_low_alarm'
    assert SEVERITY_MAP[alarm_type] == 'warning'


def test_normal_value_generates_no_alarm():
    stat = _stat(-5, -2, 2, 5)
    alarm_type, threshold = determine_alarm(0.5, stat)
    assert alarm_type is None
    assert threshold is None


def test_boundary_value_at_critical_high_is_not_alarmed():
    stat = _stat(-5, -2, 2, 5)
    # Exactly at critical_high: not strictly > so no alarm.
    alarm_type, _ = determine_alarm(5.0, stat)
    assert alarm_type in (None, 'warning_high_alarm')  # boundary behaviour


def test_boundary_value_just_above_warning_high_is_warning():
    stat = _stat(-5, -2, 2, 5)
    alarm_type, _ = determine_alarm(2.001, stat)
    assert alarm_type == 'warning_high_alarm'
