import pandas as pd
from typing import Tuple

TEP_ID_COLUMNS = ['faultNumber', 'simulationRun', 'sample']


def normalize_tep_dataframe(df: pd.DataFrame, dataset_role: str) -> pd.DataFrame:
    df = df.copy()
    for col in ['faultNumber', 'simulationRun']:
        if col in df.columns:
            df[col] = df[col].astype('Int64')
    df = df.rename(columns={'faultNumber': 'fault_id', 'simulationRun': 'run_id', 'sample': 'time_step'})

    if 'run_id' not in df.columns:
        df['run_id'] = 0
    if 'fault_id' not in df.columns:
        df['fault_id'] = 0
    if 'time_step' not in df.columns:
        df['time_step'] = range(1, len(df) + 1)

    id_columns = ['run_id', 'fault_id', 'time_step']
    measurement_columns = [col for col in df.columns if col not in id_columns]
    long = df.melt(id_vars=id_columns, value_vars=measurement_columns, var_name='variable_name', value_name='variable_value')
    long['dataset_role'] = dataset_role
    long['fault_label'] = long['fault_id'].apply(lambda x: 'fault_free' if x == 0 else f'fault_{x}')
    long['is_faulty'] = long['fault_id'] != 0
    return long


def select_variable_columns(df: pd.DataFrame) -> pd.DataFrame:
    vars = [c for c in df.columns if c.startswith('xmeas_') or c.startswith('xmv_')]
    id_cols = [c for c in ['faultNumber', 'simulationRun', 'sample', 'fault_id', 'run_id', 'time_step'] if c in df.columns]
    return df[id_cols + vars]
