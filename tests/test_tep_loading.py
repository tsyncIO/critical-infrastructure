"""test_tep_loading.py – Tests for RData loading and role derivation."""
import os
import pytest
from pathlib import Path


def test_load_rdata_returns_frames():
    """load_rdata_file must return at least one DataFrame-like object."""
    from app.services.tep_loader import load_rdata_file
    data_dir = Path(__file__).resolve().parent.parent / 'Data'
    # Use the smallest file if Data/ exists; otherwise skip.
    candidates = list(data_dir.glob('TEP_FaultFree_Training.RData'))
    if not candidates:
        pytest.skip('TEP RData files not present; skipping integration test.')
    frames = load_rdata_file(str(candidates[0]))
    assert len(frames) >= 1
    for name, df in frames.items():
        assert hasattr(df, 'columns'), f'Object {name!r} must have columns'
        assert len(df.columns) > 0


def test_derive_dataset_role():
    """Dataset role must be correctly derived from file name."""
    from app.services.tep_loader import derive_dataset_role
    assert derive_dataset_role('TEP_FaultFree_Training.RData') == 'fault_free_training'
    assert derive_dataset_role('TEP_FaultFree_Testing.RData') == 'fault_free_testing'
    assert derive_dataset_role('TEP_Faulty_Training.RData') == 'faulty_training'
    assert derive_dataset_role('TEP_Faulty_Testing.RData') == 'faulty_testing'
    assert derive_dataset_role('unknown_file.RData') == 'unknown'
