"""test_thresholds.py – Tests for threshold derivation from fault-free training data."""
import pandas as pd
import numpy as np
import pytest
from app.services.threshold_builder import derive_thresholds


def _make_df(values: list, col: str = 'xmeas_1') -> pd.DataFrame:
    return pd.DataFrame({col: values})


def test_thresholds_derived_from_numeric_columns():
    """derive_thresholds must process xmeas_/xmv_ numeric columns."""
    n = 1000
    df = pd.DataFrame({
        'xmeas_1': np.random.normal(50, 5, n),
        'xmv_1': np.random.normal(20, 2, n),
        'unrelated': np.random.normal(0, 1, n),
    })
    result = derive_thresholds(df)
    assert 'xmeas_1' in result['variable_name'].values
    assert 'xmv_1' in result['variable_name'].values
    assert 'unrelated' not in result['variable_name'].values


def test_warning_thresholds_less_strict_than_critical():
    """warning_low ≥ critical_low and warning_high ≤ critical_high."""
    df = pd.DataFrame({'xmeas_1': np.random.normal(100, 10, 2000)})
    result = derive_thresholds(df)
    row = result[result['variable_name'] == 'xmeas_1'].iloc[0]
    assert row['warning_low'] >= row['critical_low'], (
        f"warning_low ({row['warning_low']:.4f}) must be >= critical_low ({row['critical_low']:.4f})"
    )
    assert row['warning_high'] <= row['critical_high'], (
        f"warning_high ({row['warning_high']:.4f}) must be <= critical_high ({row['critical_high']:.4f})"
    )


def test_constant_variable_fallback():
    """A constant variable must not produce NaN thresholds."""
    df = pd.DataFrame({'xmeas_1': [5.0] * 100})
    result = derive_thresholds(df)
    assert len(result) == 1
    row = result.iloc[0]
    for col in ['warning_low', 'warning_high', 'critical_low', 'critical_high']:
        assert not pd.isna(row[col]), f'{col} must not be NaN for a constant variable'


def test_thresholds_quantile_rule():
    """With sufficient spread, warning thresholds use q005/q995."""
    rng = np.random.default_rng(42)
    data = rng.normal(0, 1, 5000)
    df = pd.DataFrame({'xmeas_1': data})
    result = derive_thresholds(df)
    row = result.iloc[0]
    s = pd.Series(data)
    assert abs(row['warning_low'] - s.quantile(0.005)) < 0.1
    assert abs(row['warning_high'] - s.quantile(0.995)) < 0.1
