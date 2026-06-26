# KRITIS Alarm & Dependency Lab

A PostgreSQL-backed research prototype for filtering industrial alarm messages, modelling critical-infrastructure dependencies, and supporting crisis-readiness analysis.

## Project Purpose

This repository extends the existing OpenBMC validation lab into a critical-infrastructure alarm and dependency research prototype. It uses real Tennessee Eastman Process (TEP) `.RData` files for alarm generation, and a synthetic KRITIS dependency model for crisis-impact simulation.

## What is synthetic

- TEP data is a real industrial benchmark for process monitoring and fault detection.
- The infrastructure dependency model, BCM profiles, and BPMN crisis-response process are synthetic research configurations.
- This project demonstrates how alarm preprocessing, incident grouping, and continuity scoring can be layered on benchmark process data.

## Stack

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- PostgreSQL
- pandas, NumPy, pyreadr
- Plotly.js, Cytoscape.js, bpmn-js
- pytest

## Repository Layout

- `app/` — KRITIS Flask application, models, routes, services, templates, and static assets
- `config/` — application configuration modules
- `scripts/` — CLI scripts for inspection, database setup, ingestion, and simulation
- `Data/` — Tennessee Eastman Process `.RData` benchmark files
- `docs/` — architecture, data pipeline, demo script, and assumptions
- `reports/` — generated inspection reports and output
- `controller/` — preserved existing OpenBMC validation controller and simulator logic
- `windows_side/` — preserved existing PowerShell client scripts

## PostgreSQL Setup

1. Install PostgreSQL locally.
2. Create the database `kritis_alarm_lab`.
3. Copy `.env.example` to `.env` and update credentials if needed.

Example `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/kritis_alarm_lab
FLASK_ENV=development
SECRET_KEY=change-me
FLASK_APP=app:create_app
```

## Installation

```bash
python -m pip install -r requirements.txt
```

## TEP Inspection and Ingestion

1. Inspect raw TEP files:
   ```bash
   python scripts/inspect_tep_rdata.py
   ```
2. Initialize the database and migration environment:
   ```bash
   python scripts/init_db.py
   ```
3. Seed synthetic KRITIS configuration:
   ```bash
   python scripts/seed_kritis_config.py
   ```
4. Preprocess and ingest TEP data:
   ```bash
   python scripts/preprocess_tep.py
   ```
5. Generate alarms from faulty testing runs:
   ```bash
   python scripts/generate_alarms.py
   ```
6. Filter duplicate alarms:
   ```bash
   python scripts/filter_alarms.py
   ```
7. Group incidents:
   ```bash
   python scripts/group_incidents.py
   ```
8. Run a sample cascading simulation:
   ```bash
   python scripts/run_sample_simulation.py
   ```

## Running the Web App

```bash
flask run
```

Open `http://localhost:5000`.

## Testing

```bash
pytest
```

## Interview Demo Flow

1. Start PostgreSQL.
2. Run database migrations.
3. Inspect TEP data with `scripts/inspect_tep_rdata.py`.
4. Preprocess TEP data with `scripts/preprocess_tep.py`.
5. Generate alarms with `scripts/generate_alarms.py`.
6. Filter alarms with `scripts/filter_alarms.py`.
7. Group incidents with `scripts/group_incidents.py`.
8. Open the dashboard at `http://localhost:5000`.
9. Select a fault scenario and show raw alarms.
10. Show grouped incident details.
11. Show the dependency graph.
12. Run cascading simulation.
13. Show BCM recommendation.
14. Show readiness assessment.
15. Show the BPMN crisis-response process.

## Important Limitation

The Tennessee Eastman Process dataset is used as an open industrial benchmark for process-monitoring and fault scenarios. It is not real maritime critical-infrastructure data. The infrastructure dependency model, BCM profiles, and BPMN process are synthetic research configurations used to demonstrate how the method can be adapted to crisis-management contexts.

This script calls:

- `http://localhost:5000/health`
- `http://localhost:5000/metrics`
- `http://localhost:5001/redfish/v1/` (if BMC simulator running)

## Verification & Quick Checks

- Verify Python syntax for controller modules:

```bash
python -m py_compile controller/config.py controller/logger.py controller/main.py controller/server/bmc_server.py controller/tests/test_bmc.py
```

- Tail logs while running tests:

```bash
tail -f controller/logs/run.log
```

## Notes and Next Steps

- The `bmc_server.py` is a minimal Redfish-style simulator intended for early-stage validation; extend endpoints as needed.
- To add firmware-level behavior, boot the OpenBMC QEMU image in `openbmc_vm/` and point `OPENBMC_HOST` in `controller/config.py` to its listening address.
- Consider adding a disk usage test or longer-running load simulation if you want stress testing.

If you want, I can also add a disk test and a Redfish "system health" endpoint simulation next.
