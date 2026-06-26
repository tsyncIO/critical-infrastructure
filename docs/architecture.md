# KRITIS Alarm & Dependency Lab – Architecture

## System Overview

This project extends a pre-existing OpenBMC validation laboratory into a PostgreSQL-backed research prototype for critical-infrastructure alarm analysis and crisis management support.

## End-to-End Processing Chain

```
TEP .RData files (real industrial benchmark)
    │
    ▼
Inspection (kritis/data/inspect_tep.py)
    │
    ▼
Preprocessing & Normalisation (scripts/preprocess_tep.py)
    │ – wide-format → long-format (per run, per sensor, per time step)
    │ – snake_case column names
    │ – fault_id / run_id / time_step extraction
    │
    ▼
PostgreSQL (kritis_alarm_lab)
    │ – raw_dataset_files
    │ – tep_runs
    │ – sensor_variables  (component mapping from kritis/configs/)
    │ – sensor_observations
    │ – variable_statistics (thresholds from fault_free_training)
    │
    ▼
Alarm Generation (app/services/alarm_generator.py)
    │ – per-observation threshold comparison
    │ – critical/warning severity assignment
    │
    ▼
Alarm Filtering (app/services/alarm_filter.py)
    │ – duplicate marking (same variable, same type, within 3 time steps)
    │
    ▼
Incident Grouping (app/services/incident_grouper.py)
    │ – time-window grouping (10-step windows per run per component)
    │ – incident severity from alarm severity
    │
    ▼
Dependency Analysis (app/services/dependency_analyzer.py)
    │ – BFS over infrastructure_dependencies graph
    │ – direct and downstream impact calculation
    │ – risk scoring (critical × high criticality → high risk)
    │
    ▼
Cascading Simulation (app/services/simulator.py)
    │ – impact timeline with minute offsets
    │ – BCM continuity risk versus MTD/RTO
    │ – recovery recommendation from BcmProfile
    │
    ▼
Flask Web Application (app/)
    │ – REST API (app/routes/api.py)
    │ – Page routes (app/routes/pages.py)
    │ – Bootstrap 5 + Plotly + Cytoscape.js + bpmn-js UI
```

## Layer Descriptions

### Data Layer (PostgreSQL)

All persistent state is stored in PostgreSQL. The schema is defined via SQLAlchemy models in `app/models.py` and managed with Flask-Migrate / Alembic.

| Table | Purpose |
|-------|---------|
| `raw_dataset_files` | Source `.RData` file registry |
| `tep_runs` | Run-level TEP metadata (fault_id, role) |
| `sensor_variables` | Variable definitions with component mapping |
| `sensor_observations` | Long-format observations (run × timestep × variable) |
| `variable_statistics` | Baseline thresholds derived from fault-free training |
| `alarm_events` | Generated alarm records with severity and duplicate flag |
| `incidents` | Grouped alarm clusters |
| `incident_alarm_events` | Many-to-many link |
| `infrastructure_components` | Synthetic KRITIS components |
| `infrastructure_dependencies` | Dependency graph edges |
| `bcm_profiles` | BCM parameters per component |
| `simulation_runs` | Cascading impact simulation results |
| `simulation_impact_events` | Per-component timeline events |
| `readiness_questions` | Assessment question bank |
| `readiness_assessments` | Assessment results |
| `readiness_answers` | Per-question answers |

### Application Layer

- **`app/services/`** – business logic (alarm generation, filtering, dependency analysis, simulation, BCM, readiness scoring)
- **`app/routes/api.py`** – JSON REST API
- **`app/routes/pages.py`** – Jinja2 page routes
- **`app/cli.py`** – Flask CLI commands

### Frontend Layer

- Bootstrap 5 + custom dark-mode CSS (`app/static/css/style.css`)
- Plotly.js for time-series and bar charts
- Cytoscape.js for the infrastructure dependency graph
- bpmn-js for BPMN process rendering

### Preserved Legacy Layer

- `controller/` – OpenBMC Redfish validation controller
- `openbmc_vm/` – QEMU/OpenBMC simulator configurations
- `windows_side/` – PowerShell client scripts

## Configuration

All environment configuration is read from `.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/kritis_alarm_lab
FLASK_ENV=development
SECRET_KEY=change-me
FLASK_APP=app.py
```

## Synthetic vs Real Data

| Layer | Real/Synthetic |
|-------|----------------|
| Sensor observations | **Real** – Tennessee Eastman Process benchmark |
| Alarm thresholds | **Derived** – from real fault-free training statistics |
| Infrastructure components | **Synthetic** – research configuration |
| Dependency edges | **Synthetic** – research configuration |
| BCM profiles | **Synthetic** – research configuration |
| BPMN process | **Synthetic** – research illustration |
