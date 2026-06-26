"""
scripts/preprocess_tep.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Preprocess all TEP .RData files and ingest them into PostgreSQL.

Usage:
    python scripts/preprocess_tep.py
"""
from __future__ import annotations

import gc
import json
from pathlib import Path

import pandas as pd

from app import create_app
from app.extensions import db
from app.models import (
    RawDatasetFile,
    TepRun,
    SensorVariable,
    SensorObservation,
    VariableStatistic,
)
from app.services.tep_loader import load_rdata_file, derive_dataset_role
from app.services.tep_preprocessor import normalize_tep_dataframe, select_variable_columns
from app.services.threshold_builder import derive_thresholds

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "Data"
MAPPING_FILE = ROOT / "kritis" / "configs" / "component_variable_mapping.json"

# Load variable → component mapping once.
_COMPONENT_MAP: dict[str, str] = {}
if MAPPING_FILE.exists():
    with MAPPING_FILE.open(encoding="utf-8") as _f:
        _data = json.load(_f)
        if isinstance(_data, list) and _data:
            _COMPONENT_MAP = _data[0]
        elif isinstance(_data, dict):
            _COMPONENT_MAP = _data


def _get_component_key(variable_name: str) -> str:
    return _COMPONENT_MAP.get(variable_name, "industrial_process")


def ingest():
    app = create_app()
    with app.app_context():
        # ------------------------------------------------------------------
        # Step 1: Iterate over .RData files
        # ------------------------------------------------------------------
        for rdata_path in sorted(DATA_DIR.glob("*.RData")):
            role = derive_dataset_role(rdata_path.name)
            print(f"\n>> Processing {rdata_path.name}  (role={role})")

            dataset_file = RawDatasetFile.query.filter_by(
                file_name=rdata_path.name
            ).first()
            if not dataset_file:
                dataset_file = RawDatasetFile(
                    file_name=rdata_path.name,
                    file_path=str(rdata_path),
                    file_size_bytes=rdata_path.stat().st_size,
                    dataset_role=role,
                )
                db.session.add(dataset_file)
                db.session.commit()

            frames = load_rdata_file(str(rdata_path))
            for obj_name, frame_df in frames.items():
                print(f"   object '{obj_name}': {frame_df.shape}")
                selected = select_variable_columns(frame_df)
                long_df = normalize_tep_dataframe(selected, role)

                limit_counter = 0
                is_massive_file = "TEP_Faulty_Testing" in rdata_path.name
                for (run_id_val, fault_id_val), group in long_df.groupby(
                    ["run_id", "fault_id"]
                ):
                    if is_massive_file and limit_counter >= 50:
                        break
                    limit_counter += 1
                    run_name = f"{role}-{fault_id_val}-{run_id_val}"
                    tep_run = TepRun.query.filter_by(
                        dataset_file_id=dataset_file.id, run_id=run_name
                    ).first()
                    if tep_run:
                        continue  # already ingested — skip (idempotent)

                    fault_id_int = int(fault_id_val) if fault_id_val is not None else 0
                    tep_run = TepRun(
                        dataset_file_id=dataset_file.id,
                        run_id=run_name,
                        dataset_role=role,
                        fault_id=fault_id_int,
                        fault_label=(
                            "fault_free"
                            if fault_id_int == 0
                            else f"fault_{fault_id_int}"
                        ),
                        is_faulty=fault_id_int != 0,
                        row_count=len(group["time_step"].unique()),
                        variable_count=len(group["variable_name"].unique()),
                    )
                    db.session.add(tep_run)
                    db.session.flush()

                    # Create or look up SensorVariable records.
                    variable_ids: dict[str, int] = {}
                    for var_name in group["variable_name"].unique():
                        var_rec = SensorVariable.query.filter_by(
                            variable_name=var_name
                        ).first()
                        if not var_rec:
                            var_rec = SensorVariable(
                                variable_name=var_name,
                                display_name=var_name.replace("_", " ").title(),
                                component_key=_get_component_key(var_name),
                                variable_group=(
                                    "measurement"
                                    if var_name.startswith("xmeas_")
                                    else "manipulated"
                                ),
                            )
                            db.session.add(var_rec)
                            db.session.flush()
                        variable_ids[var_name] = var_rec.id

                    # Bulk insert observations using pandas to_sql for speed.
                    obs_df = group[
                        ["time_step", "variable_name", "variable_value"]
                    ].copy()
                    obs_df["run_id"] = tep_run.id
                    obs_df["variable_id"] = obs_df["variable_name"].map(variable_ids)
                    obs_df = obs_df.drop(columns=["variable_name"])
                    obs_df = obs_df.rename(
                        columns={"variable_value": "variable_value"}
                    )
                    obs_df["time_step"] = obs_df["time_step"].astype(int)
                    obs_df["variable_value"] = obs_df["variable_value"].astype(float)

                    obs_df.to_sql(
                        "sensor_observations",
                        db.session.connection(),
                        if_exists="append",
                        index=False,
                        method="multi",
                        chunksize=10000,
                    )
                    db.session.commit()
                    print(
                        f"   Ingested run '{run_name}': "
                        f"{len(obs_df)} observations."
                    )

        
            # Explicit garbage collection to free RAM immediately
            if 'frames' in locals():
                del frames
            if 'long_df' in locals():
                del long_df
            gc.collect()

        # ------------------------------------------------------------------
        # Step 2: Derive thresholds from fault_free_training
        # ------------------------------------------------------------------
        print("\n>> Deriving thresholds from fault_free_training …")
        training_file = RawDatasetFile.query.filter_by(
            dataset_role="fault_free_training"
        ).first()
        if not training_file:
            print("   No fault_free_training file found. Skipping thresholds.")
        else:
            file_frames = load_rdata_file(str(training_file.file_path))
            raw_df = next(iter(file_frames.values()))
            selected_df = select_variable_columns(raw_df)
            thresholds = derive_thresholds(selected_df)

            for _, row in thresholds.iterrows():
                var_rec = SensorVariable.query.filter_by(
                    variable_name=row["variable_name"]
                ).first()
                if not var_rec:
                    continue
                exists = VariableStatistic.query.filter_by(
                    variable_id=var_rec.id, derived_from_role="fault_free_training"
                ).first()
                if exists:
                    continue
                stat = VariableStatistic(
                    variable_id=var_rec.id,
                    baseline_mean=row["baseline_mean"],
                    baseline_std=row["baseline_std"],
                    q001=row["q001"],
                    q005=row["q005"],
                    q025=row["q025"],
                    q500=row["q500"],
                    q975=row["q975"],
                    q995=row["q995"],
                    q999=row["q999"],
                    warning_low=row["warning_low"],
                    warning_high=row["warning_high"],
                    critical_low=row["critical_low"],
                    critical_high=row["critical_high"],
                    derived_from_role="fault_free_training",
                )
                db.session.add(stat)
            db.session.commit()
            print(f"   Thresholds derived for {len(thresholds)} variables.")

    print("\nTEP ingestion complete.")


if __name__ == "__main__":
    ingest()
