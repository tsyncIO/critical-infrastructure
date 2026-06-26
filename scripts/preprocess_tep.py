"""
scripts/preprocess_tep.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Preprocess all TEP .RData files and ingest them into PostgreSQL.

Performance optimizations applied
----------------------------------
1. Pre-load all existing TepRun.run_id values per file in one query
   → eliminates N per-run SELECT round-trips.
2. Pre-load and cache all SensorVariable records into a dict once
   → eliminates up to 52 per-variable SELECT round-trips per run.
3. Batch-flush new SensorVariable inserts in one flush, not one per variable.
4. Accumulate ALL observations for a file into a single DataFrame, then
   insert them in one go using psycopg2 execute_values (COPY-speed).
5. Commit once per file instead of once per run.

Usage:
    python scripts/preprocess_tep.py
"""
from __future__ import annotations

import gc
import json
import time
from pathlib import Path

import pandas as pd
from psycopg2.extras import execute_values
from sqlalchemy import text

from app import create_app
from app.extensions import db
from app.models import (
    RawDatasetFile,
    TepRun,
    SensorVariable,
    VariableStatistic,
)
from app.services.tep_loader import load_rdata_file, derive_dataset_role
from app.services.tep_preprocessor import normalize_tep_dataframe, select_variable_columns
from app.services.threshold_builder import derive_thresholds

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "Data"
MAPPING_FILE = ROOT / "kritis" / "configs" / "component_variable_mapping.json"

# ---------------------------------------------------------------------------
# Demo-mode limits — keep ingestion fast for a successful demonstration.
#   DEMO_MAX_RUNS   : max (run_id, fault_id) groups to ingest per massive file.
#   DEMO_SAMPLE_RATE: keep only 1-in-N time-step rows for massive files.
#                     Set to 1 to keep every row.
# ---------------------------------------------------------------------------
DEMO_MAX_RUNS: int = 10    # 10 fault-run groups ≈ a few thousand rows
DEMO_SAMPLE_RATE: int = 10  # keep every 10th timestep → ~90 % row reduction

# ---------------------------------------------------------------------------
# Load variable → component mapping once at module level.
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Observation bulk-insert via psycopg2 execute_values (fastest for Postgres)
# ---------------------------------------------------------------------------

def _bulk_insert_observations(conn_raw, rows: list[tuple]) -> None:
    """
    Insert observation rows using psycopg2 execute_values.
    Rows: (run_id, time_step, variable_id, variable_value)
    The 'created_at' column has a server-side default (NOW()) so we omit it.
    """
    if not rows:
        return
    cursor = conn_raw.cursor()
    execute_values(
        cursor,
        """
        INSERT INTO sensor_observations (run_id, time_step, variable_id, variable_value)
        VALUES %s
        """,
        rows,
        page_size=50_000,  # send 50k rows per round-trip
    )
    cursor.close()


# ---------------------------------------------------------------------------
# Main ingestion
# ---------------------------------------------------------------------------

def _ensure_sensor_variables(variable_names: list[str]) -> dict[str, int]:
    """
    Load all SensorVariable records from DB into a dict {name: id}.
    Insert any missing variables in a single batch flush.
    Returns the complete name→id mapping.
    """
    # Fetch everything currently in DB
    existing: dict[str, int] = {
        row.variable_name: row.id
        for row in SensorVariable.query.all()
    }

    new_vars = [n for n in variable_names if n not in existing]
    if new_vars:
        new_recs = [
            SensorVariable(
                variable_name=n,
                display_name=n.replace("_", " ").title(),
                component_key=_get_component_key(n),
                variable_group=(
                    "measurement" if n.startswith("xmeas_") else "manipulated"
                ),
            )
            for n in new_vars
        ]
        db.session.add_all(new_recs)
        db.session.flush()  # ONE flush for all new variables
        for rec in new_recs:
            existing[rec.variable_name] = rec.id

    return existing


def ingest():
    app = create_app()
    with app.app_context():
        # ------------------------------------------------------------------
        # Step 1: Iterate over .RData files
        # ------------------------------------------------------------------
        for rdata_path in sorted(DATA_DIR.glob("*.RData")):
            role = derive_dataset_role(rdata_path.name)
            t_file_start = time.perf_counter()
            print(f"\n>> Processing {rdata_path.name}  (role={role})")

            # Upsert the RawDatasetFile record
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
                db.session.flush()

            # ------------------------------------------------------------------
            # Optimisation 1: bulk pre-load all already-ingested run IDs for
            # this file → no per-run SELECT inside the loop.
            # ------------------------------------------------------------------
            already_ingested: set[str] = {
                row.run_id
                for row in TepRun.query.filter_by(
                    dataset_file_id=dataset_file.id
                ).with_entities(TepRun.run_id).all()
            }
            print(f"   {len(already_ingested)} runs already ingested — will skip them.")

            frames = load_rdata_file(str(rdata_path))

            for obj_name, frame_df in frames.items():
                print(f"   object '{obj_name}': {frame_df.shape}")
                
                # Any file containing "Faulty" (Training or Testing) is treated
                # as massive and subject to demo-mode limits.
                is_massive_file = "Faulty" in rdata_path.name
                if is_massive_file:
                    print(f"   [DEMO] Massive file detected — capping at "
                          f"{DEMO_MAX_RUNS} runs, sampling every "
                          f"{DEMO_SAMPLE_RATE}th time-step.")
                    
                    # ---------------------------------------------------------
                    # PRE-FILTER THE DATAFRAME BEFORE MELTING TO AVOID OOM
                    # ---------------------------------------------------------
                    # 1. Filter to max runs per fault
                    if "faultNumber" in frame_df.columns and "simulationRun" in frame_df.columns:
                        kept_runs = []
                        for fault_id, fault_group in frame_df.groupby("faultNumber"):
                            runs_for_fault = fault_group["simulationRun"].unique()[:DEMO_MAX_RUNS]
                            kept_runs.append(fault_group[fault_group["simulationRun"].isin(runs_for_fault)])
                        frame_df = pd.concat(kept_runs, ignore_index=True)
                    
                    # 2. Sample time-steps
                    if "sample" in frame_df.columns and DEMO_SAMPLE_RATE > 1:
                        unique_steps = sorted(frame_df["sample"].unique())
                        sampled_steps = set(unique_steps[::DEMO_SAMPLE_RATE])
                        frame_df = frame_df[frame_df["sample"].isin(sampled_steps)]
                    
                    print(f"   [DEMO] Reduced object size to: {frame_df.shape}")

                selected = select_variable_columns(frame_df)
                long_df = normalize_tep_dataframe(selected, role)

                # ------------------------------------------------------------------
                # Optimisation 2: load / create ALL SensorVariables upfront once.
                # ------------------------------------------------------------------
                all_var_names = long_df["variable_name"].unique().tolist()
                variable_ids: dict[str, int] = _ensure_sensor_variables(all_var_names)

                # Pre-map variable_id column (vectorised, not a Python loop)
                long_df["variable_id"] = long_df["variable_name"].map(variable_ids)

                limit_counter = 0

                # ------------------------------------------------------------------
                # Accumulate all new observation rows for this file object.
                # We'll do ONE bulk insert at the end.
                # ------------------------------------------------------------------
                all_obs_rows: list[tuple] = []

                for (run_id_val, fault_id_val), group in long_df.groupby(
                    ["run_id", "fault_id"]
                ):
                    fault_id_int = int(fault_id_val) if fault_id_val is not None else 0
                    run_name = f"{role}-{fault_id_int}-{run_id_val}"

                    # ------------------------------------------------------------------
                    # Optimisation 1 (cont.): use the pre-loaded set, not a DB query.
                    # ------------------------------------------------------------------
                    if run_name in already_ingested:
                        continue  # idempotent skip

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
                        row_count=int(group["time_step"].nunique()),
                        variable_count=int(group["variable_name"].nunique()),
                    )
                    db.session.add(tep_run)
                    db.session.flush()  # get tep_run.id

                    # ------------------------------------------------------------------
                    # Optimisation 3: accumulate rows as plain tuples (no DataFrame
                    # copy, no to_sql overhead).
                    # ------------------------------------------------------------------
                    run_db_id = tep_run.id
                    obs_group = group[["time_step", "variable_id", "variable_value"]]
                    for row in obs_group.itertuples(index=False):
                        all_obs_rows.append((
                            run_db_id,
                            int(row.time_step),
                            int(row.variable_id),
                            float(row.variable_value),
                        ))

                # ------------------------------------------------------------------
                # Optimisation 4: single bulk insert for ALL accumulated rows.
                # Use the raw psycopg2 connection for execute_values (COPY speed).
                # ------------------------------------------------------------------
                if all_obs_rows:
                    print(f"   Bulk-inserting {len(all_obs_rows):,} observations …", end=" ", flush=True)
                    t0 = time.perf_counter()
                    raw_conn = db.session.connection().connection
                    _bulk_insert_observations(raw_conn, all_obs_rows)
                    print(f"done in {time.perf_counter() - t0:.1f}s")

                # ------------------------------------------------------------------
                # Optimisation 5: commit ONCE per file object, not per run.
                # ------------------------------------------------------------------
                db.session.commit()

            # Explicit GC to free large RData frames from RAM
            del frames, long_df
            gc.collect()

            elapsed = time.perf_counter() - t_file_start
            print(f"   File done in {elapsed:.1f}s total.")

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
