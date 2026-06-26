import pyreadr
import pandas as pd
from pathlib import Path

DATA_ROLE_MAP = {
    'TEP_FaultFree_Training.RData': 'fault_free_training',
    'TEP_FaultFree_Testing.RData': 'fault_free_testing',
    'TEP_Faulty_Training.RData': 'faulty_training',
    'TEP_Faulty_Testing.RData': 'faulty_testing',
}


def load_rdata_file(path: str) -> dict[str, pd.DataFrame]:
    data = pyreadr.read_r(path)
    frames = {}
    for name, obj in data.items():
        if hasattr(obj, 'columns'):
            frames[name] = obj
    if not frames:
        raise ValueError(f'No tabular objects found in {path}')
    return frames


def derive_dataset_role(file_name: str) -> str:
    return DATA_ROLE_MAP.get(Path(file_name).name, 'unknown')
