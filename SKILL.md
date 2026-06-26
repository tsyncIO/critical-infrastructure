# skill.md

# KRITIS Alarm & Dependency Lab
## Specification-Driven Development Plan for a Complete PostgreSQL-Backed Web App

**Project base:** Existing `openbmc-validator` repository  
**Target app:** `KRITIS Alarm & Dependency Lab`  
**Primary goal:** Adapt the existing OpenBMC validation project into a research-grade web application for critical-infrastructure alarm preprocessing, alarm filtering, dependency modelling, process simulation, Business Continuity Management, readiness assessment, and BPMN-based crisis-response visualization.

---

## 0. Non-Negotiable Implementation Rules for the Coding Agent

Before writing or modifying any application code, the coding agent must inspect the real local project.

The currently known project root from `project_layout.txt` is:

```powershell
C:\Users\User\Desktop\RobiulGermany\project-26\openbmc-validator
```

The known current top-level layout is:

```text
openbmc-validator/
├── .venv/
├── controller/
├── Data/
├── logs/
├── openbmc_vm/
├── reports/
├── windows_side/
├── .gitignore
├── project_layout.txt
├── README.md
└── requirements.txt
```

The known `Data/` folder contains these TEP dataset files:

```text
Data/TEP_FaultFree_Testing.RData
Data/TEP_FaultFree_Training.RData
Data/TEP_Faulty_Testing.RData
Data/TEP_Faulty_Training.RData
```

The agent must perform repository discovery first:

```bash
pwd
find . -maxdepth 4 -type f | sort
find . -maxdepth 3 -type d | sort
```

Then inspect all existing source files before implementation:

```bash
cat README.md
cat requirements.txt
find controller -type f -maxdepth 5 -print
find openbmc_vm -type f -maxdepth 5 -print
find windows_side -type f -maxdepth 5 -print
```

For each discovered Python, PowerShell, config, JSON, markdown, shell, or HTML file, read it before modifying the project.

Do not delete the existing OpenBMC validation functionality. Extend the project by adding a new web app layer and TEP/KRITIS processing modules.

Do not hard-code fake sensor values. All sensor values used in the web app must come from the real TEP `.RData` files after preprocessing.

Do not invent unknown TEP column names without inspection. First inspect the `.RData` object names, dimensions, column names, labels, and metadata.

Do not create meaningless placeholder demo data. Static configuration is allowed only for domain modelling that does not exist in TEP, such as critical-infrastructure dependency definitions, BCM profiles, and readiness questions. These must be explicit, documented, and labelled as a synthetic research layer.

---

## 1. Background and Interview Alignment

The target job involves support for:

- web application development,
- Python-based software development,
- automated and semi-automated data analysis,
- process simulation,
- preprocessing and filtering automatically generated alarm messages,
- crisis-management process modelling,
- BPMN 2.0 model reading, creation, and modification,
- research support in civil protection and critical infrastructure.

This project must therefore not look like a generic monitoring dashboard. It must demonstrate the complete chain:

```text
industrial fault data
    ↓
alarm generation
    ↓
alarm filtering and grouping
    ↓
incident interpretation
    ↓
critical-infrastructure dependency impact
    ↓
cascading failure simulation
    ↓
Business Continuity recommendation
    ↓
BPMN crisis-response process
    ↓
web-based research dashboard
```

The existing OpenBMC project should be used as the credibility bridge:

```text
Existing OpenBMC Validation Lab
    └── Python validation framework
    └── Flask-style / REST-style interfaces
    └── Redfish-like BMC simulation
    └── JSON reports
    └── CPU / memory / network / thermal / BMC checks

New KRITIS extension
    └── TEP industrial process data adapter
    └── alarm preprocessing and filtering
    └── PostgreSQL-backed incident storage
    └── dependency and cascading-impact model
    └── BCM and readiness dashboard
    └── BPMN process viewer
```

---

## 2. Final Application Name

Use this project name consistently:

```text
KRITIS Alarm & Dependency Lab
```

Subtitle:

```text
A PostgreSQL-backed research prototype for filtering industrial alarm messages, modelling critical-infrastructure dependencies, and supporting crisis-readiness analysis.
```

---

## 3. Technology Stack

### 3.1 Backend

Use:

```text
Python 3.11+
Flask
Flask-SQLAlchemy
SQLAlchemy
Alembic / Flask-Migrate
psycopg2-binary or psycopg
pandas
NumPy
pyreadr
scikit-learn optional only after baseline rules work
pytest
python-dotenv
```

### 3.2 Database

Use PostgreSQL.

Required local database name:

```text
kritis_alarm_lab
```

Recommended local credentials must be read from `.env`, not hard-coded:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/kritis_alarm_lab
FLASK_ENV=development
FLASK_APP=app.py
```

### 3.3 Frontend

Use:

```text
HTML
CSS
Bootstrap 5
JavaScript
Plotly.js
Cytoscape.js
bpmn-js
```

React is not required for the first complete version. If React exists already in the repository, do not remove it, but the app must remain runnable through Flask templates.

### 3.4 Data Processing

Use:

```text
pyreadr for .RData loading
pandas for tabular transformation
NumPy for numerical rules
PostgreSQL COPY / bulk insert for efficient loading
Parquet cache optional for preprocessed outputs
```

### 3.5 Testing

Use:

```text
pytest
pytest-flask optional
```

---

## 4. Target Architecture

```text
+--------------------------------------------------------------------------------+
|                         KRITIS Alarm & Dependency Lab                           |
|              PostgreSQL-backed web app extending OpenBMC validator              |
+--------------------------------------------------------------------------------+

         +-------------------------------------------------------------+
         | Existing openbmc-validator repository                       |
         | controller/ openbmc_vm/ windows_side/ logs/ reports/        |
         +-----------------------------+-------------------------------+
                                       |
                                       v
         +-------------------------------------------------------------+
         | Repository Discovery Layer                                  |
         | - inspect existing scripts                                  |
         | - preserve existing OpenBMC functionality                    |
         | - add KRITIS extension without destructive edits             |
         +-----------------------------+-------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                                  DATA LAYER                                    |
+--------------------------------------------------------------------------------+

         +-----------------------------+          +------------------------------+
         | TEP .RData files            |          | Synthetic research configs   |
         | Data/*.RData                |          | dependencies, BCM, BPMN      |
         +--------------+--------------+          +---------------+--------------+
                        |                                         |
                        v                                         v
         +-----------------------------+          +------------------------------+
         | TEP Inspection              |          | Config Loader                |
         | - object keys               |          | - dependencies.json          |
         | - dimensions                |          | - bcm_profiles.json          |
         | - columns                   |          | - readiness_questions.json   |
         | - labels/fault metadata     |          | - bpmn/crisis_response.bpmn  |
         +--------------+--------------+          +---------------+--------------+
                        |                                         |
                        v                                         v
         +-------------------------------------------------------------+
         | TEP Preprocessing Pipeline                                  |
         | - normalize variable names                                  |
         | - convert wide to long format                               |
         | - attach dataset split and fault metadata                    |
         | - derive baseline thresholds from fault-free training data    |
         | - create sensor observations                                |
         +-----------------------------+-------------------------------+
                                       |
                                       v
         +-------------------------------------------------------------+
         | PostgreSQL                                                   |
         | - raw_dataset_files                                          |
         | - tep_runs                                                   |
         | - sensor_observations                                        |
         | - variable_statistics                                        |
         | - alarm_events                                               |
         | - incidents                                                  |
         | - infrastructure_components                                  |
         | - infrastructure_dependencies                                |
         | - bcm_profiles                                               |
         | - simulation_runs                                             |
         | - readiness_assessments                                      |
         +-----------------------------+-------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                               APPLICATION LAYER                                |
+--------------------------------------------------------------------------------+

         +-----------------------------+
         | Alarm Generator             |
         | - threshold alarms          |
         | - deviation severity        |
         | - component mapping         |
         +--------------+--------------+
                        |
                        v
         +-----------------------------+
         | Alarm Filter & Grouper      |
         | - duplicate filtering       |
         | - time-window grouping      |
         | - correlation grouping      |
         | - incident creation         |
         +--------------+--------------+
                        |
                        v
         +-----------------------------+
         | Dependency Analyzer         |
         | - direct impacts            |
         | - downstream impacts        |
         | - criticality propagation   |
         +--------------+--------------+
                        |
                        v
         +-----------------------------+
         | Cascading Simulator         |
         | - timeline events           |
         | - risk scoring              |
         | - downtime estimation       |
         +--------------+--------------+
                        |
                        v
         +-----------------------------+
         | BCM / Readiness Engine      |
         | - MTD / RTO checks          |
         | - backup duration checks    |
         | - readiness scoring         |
         +--------------+--------------+
                        |
                        v
+--------------------------------------------------------------------------------+
|                                  WEB LAYER                                     |
+--------------------------------------------------------------------------------+

         +-------------------------------------------------------------+
         | Flask Routes + REST API                                      |
         | /                                                           |
         | /alarms                                                     |
         | /incidents                                                  |
         | /dependencies                                               |
         | /simulation                                                 |
         | /readiness                                                  |
         | /bpmn                                                       |
         | /api/*                                                      |
         +-----------------------------+-------------------------------+
                                       |
                                       v
         +-------------------------------------------------------------+
         | Browser UI                                                   |
         | Bootstrap cards and tables                                   |
         | Plotly time-series charts                                    |
         | Cytoscape dependency graph                                   |
         | bpmn-js crisis process viewer                                |
         +-------------------------------------------------------------+
```

---

## 5. Required Final Repository Layout

The coding agent should evolve the current project into this layout while preserving existing folders.

```text
openbmc-validator/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── skill.md
│
├── controller/                         # preserve existing OpenBMC code
├── openbmc_vm/                         # preserve existing OpenBMC simulator code
├── windows_side/                       # preserve existing Windows/PowerShell code
├── logs/
├── reports/
│
├── Data/
│   ├── TEP_FaultFree_Testing.RData
│   ├── TEP_FaultFree_Training.RData
│   ├── TEP_Faulty_Testing.RData
│   └── TEP_Faulty_Training.RData
│
├── kritis/
│   ├── __init__.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── seed_static_configs.py
│   │   └── migrations/                # generated by Flask-Migrate/Alembic
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── inspect_tep.py
│   │   ├── load_rdata.py
│   │   ├── preprocess_tep.py
│   │   ├── derive_thresholds.py
│   │   ├── ingest_to_postgres.py
│   │   └── validate_dataset.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── alarm_generator.py
│   │   ├── alarm_filter.py
│   │   ├── incident_grouper.py
│   │   ├── dependency_analyzer.py
│   │   ├── simulator.py
│   │   ├── bcm.py
│   │   ├── readiness_score.py
│   │   └── report_exporter.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── pages.py
│   │   └── api.py
│   │
│   ├── configs/
│   │   ├── infrastructure_components.json
│   │   ├── infrastructure_dependencies.json
│   │   ├── component_variable_mapping.json
│   │   ├── bcm_profiles.json
│   │   └── readiness_questions.json
│   │
│   └── bpmn/
│       └── crisis_response.bpmn
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── alarms.html
│   ├── incidents.html
│   ├── dependencies.html
│   ├── simulation.html
│   ├── readiness.html
│   └── bpmn.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── alarms.js
│   │   ├── incidents.js
│   │   ├── dependencies.js
│   │   ├── simulation.js
│   │   ├── readiness.js
│   │   └── bpmn_viewer.js
│   └── vendor/                         # optional local JS assets if not using CDN
│
├── tests/
│   ├── test_tep_loading.py
│   ├── test_thresholds.py
│   ├── test_alarm_generation.py
│   ├── test_alarm_filtering.py
│   ├── test_incident_grouping.py
│   ├── test_dependency_analysis.py
│   ├── test_bcm.py
│   └── test_readiness.py
│
└── docs/
    ├── architecture.md
    ├── data_dictionary.md
    ├── preprocessing_report.md
    ├── demo_script.md
    └── limitations.md
```

---

## 6. Requirements File

Update `requirements.txt` after inspecting the existing file. Include at minimum:

```txt
Flask
Flask-SQLAlchemy
Flask-Migrate
SQLAlchemy
psycopg2-binary
python-dotenv
pandas
numpy
pyreadr
scikit-learn
pytest
pytest-flask
```

Add only libraries actually used in implementation.

---

## 7. PostgreSQL Database Design

### 7.1 Database Name

```text
kritis_alarm_lab
```

### 7.2 Tables

Implement tables through SQLAlchemy models and migrations.

#### raw_dataset_files

Tracks source `.RData` files.

```sql
CREATE TABLE raw_dataset_files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    dataset_role VARCHAR(50) NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Allowed `dataset_role` values:

```text
fault_free_training
fault_free_testing
faulty_training
faulty_testing
```

#### tep_runs

Stores run-level metadata derived from the TEP objects.

```sql
CREATE TABLE tep_runs (
    id SERIAL PRIMARY KEY,
    dataset_file_id INTEGER REFERENCES raw_dataset_files(id) ON DELETE CASCADE,
    run_id VARCHAR(100) NOT NULL,
    dataset_role VARCHAR(50) NOT NULL,
    fault_id INTEGER,
    fault_label VARCHAR(150),
    is_faulty BOOLEAN NOT NULL,
    row_count INTEGER,
    variable_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dataset_file_id, run_id)
);
```

#### sensor_variables

Stores variable metadata.

```sql
CREATE TABLE sensor_variables (
    id SERIAL PRIMARY KEY,
    variable_name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(150),
    variable_group VARCHAR(100),
    component_key VARCHAR(100),
    unit VARCHAR(50),
    description TEXT
);
```

#### sensor_observations

Stores normalized long-format observations from the TEP dataset.

```sql
CREATE TABLE sensor_observations (
    id BIGSERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES tep_runs(id) ON DELETE CASCADE,
    time_step INTEGER NOT NULL,
    variable_id INTEGER REFERENCES sensor_variables(id) ON DELETE CASCADE,
    variable_value DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Add index:

```sql
CREATE INDEX idx_sensor_obs_run_time ON sensor_observations(run_id, time_step);
CREATE INDEX idx_sensor_obs_variable ON sensor_observations(variable_id);
```

#### variable_statistics

Stores thresholds derived from fault-free training data.

```sql
CREATE TABLE variable_statistics (
    id SERIAL PRIMARY KEY,
    variable_id INTEGER REFERENCES sensor_variables(id) ON DELETE CASCADE,
    baseline_mean DOUBLE PRECISION,
    baseline_std DOUBLE PRECISION,
    q001 DOUBLE PRECISION,
    q005 DOUBLE PRECISION,
    q025 DOUBLE PRECISION,
    q500 DOUBLE PRECISION,
    q975 DOUBLE PRECISION,
    q995 DOUBLE PRECISION,
    q999 DOUBLE PRECISION,
    warning_low DOUBLE PRECISION,
    warning_high DOUBLE PRECISION,
    critical_low DOUBLE PRECISION,
    critical_high DOUBLE PRECISION,
    derived_from_role VARCHAR(50) DEFAULT 'fault_free_training',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(variable_id, derived_from_role)
);
```

Threshold rule:

```text
warning_low  = q005
warning_high = q995
critical_low = q001
critical_high = q999
```

If quantiles are unreliable for a variable because of missing or constant values, use:

```text
warning_low  = mean - 3 * std
warning_high = mean + 3 * std
critical_low = mean - 4 * std
critical_high = mean + 4 * std
```

Document every fallback in `docs/preprocessing_report.md`.

#### alarm_events

Stores generated alarm messages.

```sql
CREATE TABLE alarm_events (
    id BIGSERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES tep_runs(id) ON DELETE CASCADE,
    observation_id BIGINT REFERENCES sensor_observations(id) ON DELETE SET NULL,
    time_step INTEGER NOT NULL,
    variable_id INTEGER REFERENCES sensor_variables(id) ON DELETE SET NULL,
    component_key VARCHAR(100),
    alarm_type VARCHAR(100) NOT NULL,
    severity VARCHAR(30) NOT NULL,
    message TEXT NOT NULL,
    deviation_value DOUBLE PRECISION,
    threshold_value DOUBLE PRECISION,
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_group_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Allowed severity values:

```text
normal
warning
critical
```

#### incidents

Stores grouped incidents.

```sql
CREATE TABLE incidents (
    id BIGSERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES tep_runs(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    root_cause_candidate VARCHAR(150),
    severity VARCHAR(30) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    first_time_step INTEGER,
    last_time_step INTEGER,
    raw_alarm_count INTEGER DEFAULT 0,
    unique_alarm_count INTEGER DEFAULT 0,
    affected_component_count INTEGER DEFAULT 0,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### incident_alarm_events

```sql
CREATE TABLE incident_alarm_events (
    incident_id BIGINT REFERENCES incidents(id) ON DELETE CASCADE,
    alarm_event_id BIGINT REFERENCES alarm_events(id) ON DELETE CASCADE,
    PRIMARY KEY (incident_id, alarm_event_id)
);
```

#### infrastructure_components

Synthetic critical-infrastructure layer.

```sql
CREATE TABLE infrastructure_components (
    id SERIAL PRIMARY KEY,
    component_key VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(150) NOT NULL,
    sector VARCHAR(100),
    responsible_org VARCHAR(150),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Required components:

```text
process_control_system
cooling_system
industrial_process
communication_system
port_operations
municipal_crisis_coordination
emergency_power
water_supply
```

#### infrastructure_dependencies

```sql
CREATE TABLE infrastructure_dependencies (
    id SERIAL PRIMARY KEY,
    source_component_id INTEGER REFERENCES infrastructure_components(id) ON DELETE CASCADE,
    target_component_id INTEGER REFERENCES infrastructure_components(id) ON DELETE CASCADE,
    dependency_type VARCHAR(100),
    criticality VARCHAR(30),
    description TEXT,
    UNIQUE(source_component_id, target_component_id)
);
```

Interpretation:

```text
source_component_id → target_component_id
```

Meaning:

```text
target depends on source
```

Required dependency chain:

```text
emergency_power → process_control_system
process_control_system → cooling_system
cooling_system → industrial_process
industrial_process → port_operations
communication_system → municipal_crisis_coordination
port_operations → municipal_crisis_coordination
water_supply → municipal_crisis_coordination
```

#### bcm_profiles

```sql
CREATE TABLE bcm_profiles (
    id SERIAL PRIMARY KEY,
    component_id INTEGER REFERENCES infrastructure_components(id) ON DELETE CASCADE,
    maximum_tolerable_downtime_min INTEGER NOT NULL,
    recovery_time_objective_min INTEGER NOT NULL,
    backup_available BOOLEAN DEFAULT FALSE,
    backup_duration_min INTEGER,
    recovery_action TEXT,
    emergency_contact_role VARCHAR(150),
    last_exercise_date DATE,
    UNIQUE(component_id)
);
```

Use specific, coherent BCM profiles. Do not use empty placeholder text.

#### simulation_runs

```sql
CREATE TABLE simulation_runs (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT REFERENCES incidents(id) ON DELETE CASCADE,
    scenario_name VARCHAR(150),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_interruption_min INTEGER,
    continuity_risk VARCHAR(30),
    recommendation TEXT
);
```

#### simulation_impact_events

```sql
CREATE TABLE simulation_impact_events (
    id BIGSERIAL PRIMARY KEY,
    simulation_run_id BIGINT REFERENCES simulation_runs(id) ON DELETE CASCADE,
    minute_offset INTEGER NOT NULL,
    component_key VARCHAR(100) NOT NULL,
    impact_level VARCHAR(30) NOT NULL,
    message TEXT NOT NULL
);
```

#### readiness_questions

```sql
CREATE TABLE readiness_questions (
    id SERIAL PRIMARY KEY,
    question_key VARCHAR(100) UNIQUE NOT NULL,
    question_text TEXT NOT NULL,
    category VARCHAR(100),
    weight DOUBLE PRECISION DEFAULT 1.0
);
```

#### readiness_assessments

```sql
CREATE TABLE readiness_assessments (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(150),
    total_score DOUBLE PRECISION,
    max_score DOUBLE PRECISION,
    percentage_score DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### readiness_answers

```sql
CREATE TABLE readiness_answers (
    id BIGSERIAL PRIMARY KEY,
    assessment_id BIGINT REFERENCES readiness_assessments(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES readiness_questions(id) ON DELETE CASCADE,
    answer_value VARCHAR(30) NOT NULL,
    numeric_score DOUBLE PRECISION NOT NULL,
    comment TEXT
);
```

Allowed answer values:

```text
yes
partial
no
unknown
```

Scoring:

```text
yes     = 1.0
partial = 0.5
no      = 0.0
unknown = 0.0
```

---

## 8. TEP Dataset Preprocessing Plan

### 8.1 Inspect `.RData` Files

Implement:

```text
kritis/data/inspect_tep.py
```

Required behavior:

1. Open each `.RData` file with `pyreadr.read_r()`.
2. Print object keys.
3. For each object:
   - type,
   - shape,
   - column names,
   - first 5 rows,
   - null count,
   - numeric column count,
   - non-numeric column count.
4. Write inspection output to:

```text
docs/preprocessing_report.md
```

5. Do not assume object names. Discover them.

Example command:

```bash
python -m kritis.data.inspect_tep
```

### 8.2 Load `.RData`

Implement:

```text
kritis/data/load_rdata.py
```

Required function:

```python
def load_rdata_file(path: str) -> dict[str, pandas.DataFrame]:
    """Load one RData file and return all DataFrame-like objects."""
```

Rules:

- Keep all object names.
- Convert R column names to lowercase snake_case.
- Preserve original column names in logs/report.
- Raise a clear error if no tabular object is found.

### 8.3 Identify Dataset Role

The file role must be derived from the file name:

```text
TEP_FaultFree_Training.RData → fault_free_training
TEP_FaultFree_Testing.RData  → fault_free_testing
TEP_Faulty_Training.RData    → faulty_training
TEP_Faulty_Testing.RData     → faulty_testing
```

### 8.4 Normalize TEP Structure

Because `.RData` object structure may vary, implement a robust normalizer.

Required normalized run-level output:

```text
run_id
dataset_role
fault_id
fault_label
is_faulty
time_step
variable_name
variable_value
```

The agent must inspect actual columns before deciding how to extract `fault_id`, `run_id`, and `time_step`.

If the dataset is in wide format:

```text
sample/run/time rows × sensor columns
```

convert to long format:

```text
run_id | time_step | variable_name | variable_value
```

If the dataset already contains `faultNumber`, `simulationRun`, `sample`, or similar columns, preserve them and map them to normalized names.

If no run identifier exists, create deterministic run IDs based on dataset role, object name, fault id, and row grouping discovered from the data. This is not fake demo data; it is deterministic metadata derived from the dataset structure. Document the rule in `docs/preprocessing_report.md`.

### 8.5 Fault Metadata

For fault-free files:

```text
fault_id = 0
fault_label = fault_free
is_faulty = false
```

For faulty files:

- Extract fault ID from actual dataset metadata if present.
- If the file contains multiple fault scenarios, preserve all of them.
- If no explicit fault label exists, use `fault_<id>`.

### 8.6 Variable Mapping

Create:

```text
kritis/configs/component_variable_mapping.json
```

This file must map actual discovered TEP variables to infrastructure components.

Required logic:

1. Inspect actual variable names.
2. If variables match typical TEP names such as `xmeas_1`, `xmeas_2`, `xmv_1`, map them by category.
3. If names differ, create mapping using discovered variable names and document the mapping.

Minimum categories:

```text
process_control_system
cooling_system
industrial_process
communication_system
port_operations
```

Mapping must not assign every variable randomly. It must use consistent rules:

- temperature/cooling-related variables → `cooling_system`,
- pressure/reactor/process variables → `industrial_process`,
- manipulated/control variables → `process_control_system`,
- quality/output/service stability proxy variables → `port_operations`,
- if unknown → `industrial_process` with explanation.

### 8.7 Threshold Derivation

Implement:

```text
kritis/data/derive_thresholds.py
```

Use only `fault_free_training` data for baseline thresholds.

For each numeric variable:

```text
mean
std
q001
q005
q025
q500
q975
q995
q999
warning_low
warning_high
critical_low
critical_high
```

Threshold priority:

```text
warning_low  = q005
warning_high = q995
critical_low = q001
critical_high = q999
```

Fallback when quantiles are not useful:

```text
warning_low  = mean - 3 * std
warning_high = mean + 3 * std
critical_low = mean - 4 * std
critical_high = mean + 4 * std
```

If a variable is constant in fault-free training:

```text
warning_low  = constant_value
warning_high = constant_value
critical_low = constant_value
critical_high = constant_value
```

Then alarm generation should flag any deviation from the constant value.

### 8.8 PostgreSQL Ingestion

Implement:

```text
kritis/data/ingest_to_postgres.py
```

Pipeline:

```text
RData files
    ↓
inspect
    ↓
normalize
    ↓
create / update raw_dataset_files
    ↓
create tep_runs
    ↓
create sensor_variables
    ↓
bulk insert sensor_observations
    ↓
derive variable_statistics
```

Command:

```bash
python -m kritis.data.ingest_to_postgres
```

The ingestion must be idempotent:

- running it twice must not duplicate files, runs, variables, or observations,
- either use delete-and-reload per dataset file or stable unique constraints.

For large data, avoid row-by-row ORM insert. Use one of:

```text
pandas.to_sql(method='multi')
SQLAlchemy bulk_save_objects
PostgreSQL COPY through psycopg
```

---

## 9. Alarm Generation Design

Implement:

```text
kritis/services/alarm_generator.py
```

### 9.1 Input

Sensor observations from PostgreSQL joined with:

- sensor variable metadata,
- variable statistics,
- run metadata.

### 9.2 Output

Rows in `alarm_events`.

### 9.3 Rules

For each observation:

```text
value < critical_low  → critical_low_alarm
value > critical_high → critical_high_alarm
value < warning_low   → warning_low_alarm
value > warning_high  → warning_high_alarm
otherwise             → no alarm
```

Severity:

```text
critical_low_alarm / critical_high_alarm → critical
warning_low_alarm / warning_high_alarm   → warning
```

Alarm message format:

```text
<display_name> is below/above <severity> threshold at time step <time_step>. Value=<value>, threshold=<threshold>.
```

Do not generate alarms for fault-free normal observations unless thresholds detect abnormality.

### 9.4 Command

```bash
python -m kritis.services.alarm_generator --role faulty_testing
```

Allow filtering by:

```text
--run-id
--fault-id
--limit-runs
```

---

## 10. Alarm Filtering Design

Implement:

```text
kritis/services/alarm_filter.py
```

### 10.1 Duplicate Filter

Mark duplicate alarms when all are true:

```text
same run_id
same variable_id
same alarm_type
same severity
within duplicate window of 3 time steps
```

Keep the first alarm as unique. Mark later alarms as duplicate.

### 10.2 Time-Window Filter

Group alarms into windows:

```text
window_size = 10 time steps
```

For each run and component, collect alarms per time window.

### 10.3 Correlation Filter

Alarms are correlated if:

```text
same run_id
same or dependent component
same 10-step window
```

Use infrastructure dependency graph to detect related components.

---

## 11. Incident Grouping Design

Implement:

```text
kritis/services/incident_grouper.py
```

### 11.1 Incident Creation Rule

Create one incident per:

```text
run_id + time window + dominant affected component / dependency chain
```

### 11.2 Incident Title Logic

Use root-cause candidate from dominant component:

```text
cooling_system             → Cooling-system degradation
process_control_system     → Process-control anomaly
industrial_process         → Industrial-process instability
port_operations            → Port-service availability risk
communication_system       → Communication-system degradation
```

### 11.3 Severity Rule

```text
critical if at least one critical unique alarm exists
warning if only warning alarms exist
normal is not used for incidents
```

### 11.4 Explanation

Incident explanation must be generated from real alarm counts:

```text
This incident groups <raw_alarm_count> raw alarms into <unique_alarm_count> unique alarm types between time steps <first_time_step> and <last_time_step>. The dominant affected component is <component>. Severity is <severity> because <reason>.
```

---

## 12. Infrastructure Dependency Model

Implement static seed files:

```text
kritis/configs/infrastructure_components.json
kritis/configs/infrastructure_dependencies.json
```

This layer is synthetic because TEP does not contain municipal/maritime dependency data. It must be labelled as synthetic research configuration in README and UI.

### 12.1 Components

Use these components:

```json
[
  {
    "component_key": "emergency_power",
    "display_name": "Emergency Power",
    "sector": "Energy",
    "responsible_org": "Infrastructure operator",
    "description": "Backup power capability used to maintain control and monitoring functions during disruption."
  },
  {
    "component_key": "process_control_system",
    "display_name": "Process Control System",
    "sector": "Industrial control",
    "responsible_org": "Industrial operator",
    "description": "Control and monitoring layer for industrial process variables and manipulated variables."
  },
  {
    "component_key": "cooling_system",
    "display_name": "Cooling System",
    "sector": "Technical infrastructure",
    "responsible_org": "Industrial operator",
    "description": "Cooling-related technical subsystem whose degradation can affect process stability."
  },
  {
    "component_key": "industrial_process",
    "display_name": "Industrial Process",
    "sector": "Production / service process",
    "responsible_org": "Industrial operator",
    "description": "Core process represented by the Tennessee Eastman benchmark variables."
  },
  {
    "component_key": "port_operations",
    "display_name": "Port Operations",
    "sector": "Maritime critical infrastructure",
    "responsible_org": "Port operator",
    "description": "Synthetic service layer representing operational availability of maritime infrastructure."
  },
  {
    "component_key": "communication_system",
    "display_name": "Communication System",
    "sector": "Information and communication",
    "responsible_org": "IT / communications provider",
    "description": "Communication layer needed for coordination between operators and authorities."
  },
  {
    "component_key": "water_supply",
    "display_name": "Water Supply",
    "sector": "Municipal infrastructure",
    "responsible_org": "Municipal utility",
    "description": "Synthetic municipal dependency used for crisis-readiness demonstration."
  },
  {
    "component_key": "municipal_crisis_coordination",
    "display_name": "Municipal Crisis Coordination",
    "sector": "Civil protection",
    "responsible_org": "Municipal crisis team",
    "description": "Coordination function for crisis response and continuity decisions."
  }
]
```

### 12.2 Dependencies

```json
[
  {
    "source": "emergency_power",
    "target": "process_control_system",
    "dependency_type": "power_dependency",
    "criticality": "high",
    "description": "The process control system requires power or backup power to remain available."
  },
  {
    "source": "process_control_system",
    "target": "cooling_system",
    "dependency_type": "control_dependency",
    "criticality": "high",
    "description": "Cooling-system control depends on the availability of the process control layer."
  },
  {
    "source": "cooling_system",
    "target": "industrial_process",
    "dependency_type": "technical_dependency",
    "criticality": "high",
    "description": "Cooling degradation can destabilize industrial process operation."
  },
  {
    "source": "industrial_process",
    "target": "port_operations",
    "dependency_type": "service_dependency",
    "criticality": "medium",
    "description": "Industrial process instability can reduce operational service availability."
  },
  {
    "source": "port_operations",
    "target": "municipal_crisis_coordination",
    "dependency_type": "coordination_dependency",
    "criticality": "medium",
    "description": "Severe disruption in port operations requires crisis coordination."
  },
  {
    "source": "communication_system",
    "target": "municipal_crisis_coordination",
    "dependency_type": "communication_dependency",
    "criticality": "high",
    "description": "Crisis coordination requires functioning communication channels."
  },
  {
    "source": "water_supply",
    "target": "municipal_crisis_coordination",
    "dependency_type": "municipal_dependency",
    "criticality": "medium",
    "description": "Water-supply disruption can become a municipal crisis-management concern."
  }
]
```

---

## 13. Dependency Analyzer Design

Implement:

```text
kritis/services/dependency_analyzer.py
```

Required functions:

```python
def get_direct_impacts(component_key: str) -> list[str]
def get_downstream_impacts(component_key: str) -> list[str]
def get_impact_path(component_key: str) -> list[dict]
def calculate_dependency_risk(component_key: str, incident_severity: str) -> dict
```

Use breadth-first traversal over `infrastructure_dependencies`.

Risk rule:

```text
critical incident + high criticality dependency path     → high risk
critical incident + medium criticality dependency path   → medium risk
warning incident + high criticality dependency path      → medium risk
warning incident + medium/low dependency path            → low risk
```

---

## 14. Cascading Simulation Design

Implement:

```text
kritis/services/simulator.py
```

### 14.1 Input

```text
incident_id
```

### 14.2 Output

Rows in:

```text
simulation_runs
simulation_impact_events
```

### 14.3 Simulation Rule

For each affected component and downstream dependency:

```text
minute_offset = graph_depth * 10
```

Impact level:

```text
root component critical incident → severe
root component warning incident  → moderate
one-hop downstream               → reduced / at_risk
two-hop downstream               → at_risk
three-hop downstream             → monitoring_required
```

Estimated interruption:

```text
base = 30 minutes for warning incident
base = 90 minutes for critical incident
+ 15 minutes for each downstream component
```

Continuity risk:

Compare estimated interruption with BCM maximum tolerable downtime.

```text
estimated_interruption > MTD       → high
estimated_interruption > RTO       → medium
otherwise                          → low
```

Recommendation:

Use BCM recovery action of the most critical affected component.

---

## 15. BCM Design

Implement:

```text
kritis/services/bcm.py
```

Seed `kritis/configs/bcm_profiles.json` with meaningful profiles:

```json
[
  {
    "component_key": "cooling_system",
    "maximum_tolerable_downtime_min": 60,
    "recovery_time_objective_min": 30,
    "backup_available": true,
    "backup_duration_min": 45,
    "recovery_action": "Activate backup cooling procedure and dispatch technical maintenance team.",
    "emergency_contact_role": "Technical operations lead"
  },
  {
    "component_key": "industrial_process",
    "maximum_tolerable_downtime_min": 90,
    "recovery_time_objective_min": 45,
    "backup_available": false,
    "backup_duration_min": 0,
    "recovery_action": "Reduce process load and prepare controlled shutdown if instability persists.",
    "emergency_contact_role": "Process operations lead"
  },
  {
    "component_key": "port_operations",
    "maximum_tolerable_downtime_min": 120,
    "recovery_time_objective_min": 60,
    "backup_available": true,
    "backup_duration_min": 90,
    "recovery_action": "Switch to manual coordination and prioritize critical port services.",
    "emergency_contact_role": "Port operations coordinator"
  },
  {
    "component_key": "municipal_crisis_coordination",
    "maximum_tolerable_downtime_min": 30,
    "recovery_time_objective_min": 15,
    "backup_available": true,
    "backup_duration_min": 180,
    "recovery_action": "Activate crisis staff communication protocol and establish situation report workflow.",
    "emergency_contact_role": "Municipal crisis staff lead"
  },
  {
    "component_key": "process_control_system",
    "maximum_tolerable_downtime_min": 45,
    "recovery_time_objective_min": 20,
    "backup_available": true,
    "backup_duration_min": 60,
    "recovery_action": "Switch control monitoring to backup workstation and verify controller communication.",
    "emergency_contact_role": "Control system engineer"
  },
  {
    "component_key": "communication_system",
    "maximum_tolerable_downtime_min": 30,
    "recovery_time_objective_min": 15,
    "backup_available": true,
    "backup_duration_min": 120,
    "recovery_action": "Use alternate communication channel and notify coordination partners.",
    "emergency_contact_role": "IT and communication lead"
  },
  {
    "component_key": "emergency_power",
    "maximum_tolerable_downtime_min": 15,
    "recovery_time_objective_min": 5,
    "backup_available": true,
    "backup_duration_min": 240,
    "recovery_action": "Start emergency generator and verify fuel/runtime status.",
    "emergency_contact_role": "Facility security lead"
  },
  {
    "component_key": "water_supply",
    "maximum_tolerable_downtime_min": 180,
    "recovery_time_objective_min": 90,
    "backup_available": true,
    "backup_duration_min": 120,
    "recovery_action": "Coordinate with municipal water utility and check emergency supply capacity.",
    "emergency_contact_role": "Municipal utility coordinator"
  }
]
```

---

## 16. Readiness Assessment Design

Implement:

```text
kritis/services/readiness_score.py
```

Seed questions:

```json
[
  {
    "question_key": "dependencies_documented",
    "question_text": "Are critical dependencies between infrastructure components documented?",
    "category": "Dependency management",
    "weight": 1.5
  },
  {
    "question_key": "responsibilities_assigned",
    "question_text": "Are responsible organisations or roles assigned for each critical component?",
    "category": "Organisation",
    "weight": 1.0
  },
  {
    "question_key": "backup_power_available",
    "question_text": "Is backup power available for critical monitoring and control functions?",
    "category": "Technical continuity",
    "weight": 1.5
  },
  {
    "question_key": "backup_duration_known",
    "question_text": "Is the expected backup operating duration known and documented?",
    "category": "Technical continuity",
    "weight": 1.0
  },
  {
    "question_key": "alternative_communication_available",
    "question_text": "Is an alternative communication channel available for crisis coordination?",
    "category": "Communication",
    "weight": 1.5
  },
  {
    "question_key": "recovery_times_defined",
    "question_text": "Are maximum tolerable downtime and recovery-time objectives defined?",
    "category": "Business Continuity Management",
    "weight": 1.5
  },
  {
    "question_key": "exercise_performed",
    "question_text": "Has the recovery or crisis-response process been exercised or tested?",
    "category": "Training and exercises",
    "weight": 1.0
  },
  {
    "question_key": "alarm_filtering_defined",
    "question_text": "Is there a defined procedure for filtering and validating automated alarms?",
    "category": "Alarm management",
    "weight": 1.0
  }
]
```

Score:

```text
weighted_score = sum(answer_numeric_score * question_weight)
max_score = sum(question_weight)
percentage_score = weighted_score / max_score * 100
```

---

## 17. BPMN Process Design

Create:

```text
kritis/bpmn/crisis_response.bpmn
```

The BPMN process must include lanes:

```text
Monitoring System
Infrastructure Operator
Municipal Crisis Team
External Support / Authority
```

Process flow:

```text
Alarm received
    ↓
Automated validation
    ↓
Duplicate alarm?
    ├── yes → Group with existing incident
    └── no  → Create new incident
                ↓
Identify affected infrastructure
                ↓
Assess dependency impact
                ↓
Critical continuity risk?
    ├── yes → Notify municipal crisis team
    │           ↓
    │       Activate continuity measure
    │           ↓
    │       Request external support if required
    └── no  → Monitor and document
                ↓
Update situation report
                ↓
Close incident after recovery
```

Use `bpmn-js` to render this file in `/bpmn`.

---

## 18. Flask Application Design

### 18.1 app.py

`app.py` must create the Flask app and register blueprints.

Required pattern:

```python
from kritis import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

### 18.2 kritis/__init__.py

Factory pattern:

```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
```

---

## 19. Web Pages

### 19.1 `/` Overview Dashboard

Show:

```text
Total TEP runs loaded
Total sensor observations
Total generated alarms
Critical alarms
Open incidents
Affected components
Latest simulation risk
Readiness score
```

Charts:

```text
Alarm count by severity
Incident count by component
Latest selected run sensor timeline
```

### 19.2 `/alarms`

Show:

- filter by dataset role,
- filter by fault id,
- filter by run id,
- alarm table,
- duplicate status,
- severity badge,
- linked incident ID.

### 19.3 `/incidents`

Show:

- incident cards,
- raw alarm count,
- unique alarm count,
- affected components,
- explanation,
- button to run simulation.

### 19.4 `/dependencies`

Use Cytoscape.js.

Show:

```text
emergency_power → process_control_system → cooling_system → industrial_process → port_operations → municipal_crisis_coordination
communication_system → municipal_crisis_coordination
water_supply → municipal_crisis_coordination
```

Highlight affected components for selected incident.

### 19.5 `/simulation`

Show:

- select incident,
- run simulation,
- timeline table,
- continuity risk,
- BCM recommendation.

### 19.6 `/readiness`

Show:

- readiness questionnaire,
- yes / partial / no / unknown options,
- score result,
- strengths,
- weaknesses.

### 19.7 `/bpmn`

Show BPMN viewer rendering `crisis_response.bpmn`.

---

## 20. REST API Design

Implement:

```text
GET  /api/health
GET  /api/dataset/summary
GET  /api/runs
GET  /api/variables
GET  /api/alarms
GET  /api/incidents
GET  /api/incidents/<id>
POST /api/incidents/<id>/simulate
GET  /api/dependencies
GET  /api/dependencies/impact/<component_key>
GET  /api/simulations/<id>
GET  /api/readiness/questions
POST /api/readiness/assess
GET  /api/bpmn/crisis-response
```

### 20.1 `/api/dataset/summary`

Return:

```json
{
  "files_loaded": 4,
  "runs": 0,
  "sensor_observations": 0,
  "variables": 0,
  "alarms": 0,
  "incidents": 0
}
```

The actual values must come from PostgreSQL.

### 20.2 `/api/alarms`

Query parameters:

```text
role
fault_id
run_id
severity
component_key
limit
offset
```

### 20.3 `/api/incidents/<id>/simulate`

Creates a simulation run from the selected incident and returns simulation ID and impact events.

---

## 21. CLI Commands

Provide runnable commands.

```bash
python -m kritis.data.inspect_tep
python -m kritis.data.ingest_to_postgres
python -m kritis.services.alarm_generator --role faulty_testing
python -m kritis.services.alarm_filter
python -m kritis.services.incident_grouper
python -m kritis.db.seed_static_configs
flask db init
flask db migrate -m "initial kritis schema"
flask db upgrade
flask run
pytest
```

Also add Flask CLI commands if possible:

```bash
flask kritis inspect-tep
flask kritis ingest-tep
flask kritis generate-alarms
flask kritis group-incidents
flask kritis seed-configs
```

---

## 22. End-to-End Build Order

The coding agent must implement in this order.

### Phase 1: Repository Understanding

1. Read all existing files.
2. Summarize existing OpenBMC architecture in `docs/architecture.md`.
3. Identify reusable functions.
4. Do not change existing behaviour yet.

### Phase 2: Project Scaffolding

1. Add `kritis/` package.
2. Add Flask app factory.
3. Add config handling.
4. Add PostgreSQL connection.
5. Add SQLAlchemy models.
6. Add migrations.

### Phase 3: TEP Inspection and Preprocessing

1. Load `.RData` files.
2. Inspect object structure.
3. Create preprocessing report.
4. Normalize data into run/observation format.
5. Derive thresholds from fault-free training data.
6. Ingest into PostgreSQL.

### Phase 4: Static Research Configs

1. Seed infrastructure components.
2. Seed infrastructure dependencies.
3. Seed BCM profiles.
4. Seed readiness questions.
5. Create BPMN file.

### Phase 5: Alarm Pipeline

1. Generate alarms from TEP observations.
2. Mark duplicates.
3. Group alarms into incidents.
4. Persist incidents.

### Phase 6: Dependency and Simulation

1. Implement graph traversal.
2. Implement cascading simulation.
3. Implement BCM recommendation.
4. Persist simulation runs.

### Phase 7: Web UI

1. Build base template.
2. Build overview dashboard.
3. Build alarm dashboard.
4. Build incident page.
5. Build dependency graph.
6. Build simulation page.
7. Build readiness page.
8. Build BPMN page.

### Phase 8: Tests and Documentation

1. Add pytest tests.
2. Update README.
3. Add screenshots if available.
4. Add `docs/demo_script.md`.
5. Add `docs/limitations.md`.

---

## 23. Tests

Minimum tests:

### test_tep_loading.py

- `.RData` loader returns at least one DataFrame-like object.
- Dataset role is correctly derived from file name.

### test_thresholds.py

- Thresholds are derived only from fault-free training data.
- Warning thresholds are less strict than critical thresholds.

### test_alarm_generation.py

- Values beyond critical threshold generate critical alarm.
- Values beyond warning threshold generate warning alarm.
- Normal values generate no alarm.

### test_alarm_filtering.py

- Duplicate alarms within the same time window are marked duplicate.
- Different variables are not incorrectly marked duplicate.

### test_incident_grouping.py

- Related alarms create one incident.
- Incident severity becomes critical if any unique alarm is critical.

### test_dependency_analysis.py

- Downstream impact from `cooling_system` includes `industrial_process`, `port_operations`, and `municipal_crisis_coordination`.

### test_bcm.py

- Interruption above MTD returns high continuity risk.

### test_readiness.py

- yes / partial / no scores produce correct weighted percentage.

---

## 24. README Requirements

Update README with:

```text
1. Project motivation
2. Interview relevance
3. Stack
4. Architecture diagram
5. Dataset explanation
6. Important limitation: TEP is not maritime data
7. PostgreSQL setup
8. How to inspect TEP
9. How to ingest TEP
10. How to run alarm generation
11. How to run the web app
12. How to run tests
13. Demo script
```

README limitation section must include:

```text
The Tennessee Eastman Process dataset is used as an open industrial benchmark for process-monitoring and fault scenarios. It is not real maritime critical-infrastructure data. The infrastructure dependency model, BCM profiles, and BPMN process are synthetic research configurations used to demonstrate how the method can be adapted to crisis-management contexts.
```

---

## 25. Interview Demo Script

Add:

```text
docs/demo_script.md
```

Demo flow:

```text
1. Open overview dashboard.
2. Explain that real TEP data has been ingested from .RData files.
3. Show dataset summary from PostgreSQL.
4. Open alarm dashboard.
5. Filter for faulty testing runs.
6. Show generated alarms from real sensor deviations.
7. Show duplicate filtering.
8. Open incidents.
9. Show grouped incident such as Cooling-system degradation or Process instability.
10. Open dependency graph.
11. Show downstream effects from technical component to port/crisis coordination layer.
12. Run cascading simulation.
13. Show BCM continuity risk and recommendation.
14. Open readiness assessment.
15. Show crisis-readiness scoring.
16. Open BPMN response process.
17. Close with limitations and next research steps.
```

Closing sentence:

```text
This prototype uses real open industrial process data for the alarm layer and a synthetic critical-infrastructure model for the crisis-management layer. In a real research project, the dependency model, alarm rules, and BPMN process would be validated through literature review, interviews, workshops, and expert feedback.
```

---

## 26. Acceptance Criteria

The project is complete when all of the following are true.

### Data

- All four `.RData` files are inspected.
- Inspection report exists.
- PostgreSQL contains source file records.
- PostgreSQL contains TEP run records.
- PostgreSQL contains sensor variables.
- PostgreSQL contains sensor observations from real TEP data.
- Variable statistics and thresholds are derived from fault-free training data.

### Alarm Pipeline

- Alarm events are generated from actual TEP observations.
- Duplicate alarms are marked.
- Incidents are created from grouped alarms.
- Incident explanations use real alarm counts and time steps.

### Critical Infrastructure Layer

- Infrastructure components are seeded.
- Dependencies are seeded.
- Dependency graph API works.
- Downstream impact analysis works.

### Simulation and BCM

- Incident simulation works.
- Simulation timeline is saved.
- BCM recommendation is generated.
- Continuity risk is calculated.

### Web UI

- Flask app starts successfully.
- Dashboard loads.
- Alarm page loads real alarms from PostgreSQL.
- Incident page loads grouped incidents.
- Dependency graph renders with Cytoscape.js.
- Simulation page runs and displays timeline.
- Readiness page calculates score.
- BPMN page renders process model.

### Quality

- Existing OpenBMC code remains intact.
- README is updated.
- Tests pass.
- No fake TEP sensor values are hard-coded.
- Synthetic domain assumptions are clearly labelled.

---

## 27. Final Git Commit Structure

Use clear commits:

```text
1. docs: document existing repository and KRITIS extension plan
2. setup: add Flask app factory and PostgreSQL configuration
3. db: add KRITIS SQLAlchemy models and migrations
4. data: add TEP inspection and preprocessing pipeline
5. data: ingest TEP observations and derive thresholds
6. configs: seed infrastructure, BCM, readiness and BPMN assets
7. alarms: implement alarm generation, filtering and incident grouping
8. simulation: implement dependency analysis, cascading simulation and BCM logic
9. ui: add dashboard, alarms, incidents, dependencies, simulation, readiness and BPMN pages
10. tests: add pipeline and service tests
11. docs: update README, demo script and limitations
```

---

## 28. Important Implementation Notes

1. The application must be explainable. Use rule-based alarm filtering first.
2. Do not add black-box AI unless the baseline pipeline is complete.
3. PostgreSQL must be the source of truth after ingestion.
4. Keep TEP preprocessing reproducible.
5. Keep synthetic crisis-management assumptions separate from real TEP data.
6. Every dashboard value must come from PostgreSQL or documented static config.
7. Every limitation must be documented honestly.
8. The app must run locally with `flask run`.
9. The coding agent must not overwrite existing project files blindly.
10. The project should look like a serious research prototype, not a toy dashboard.

---

## 29. Minimum Successful Interview Version

If time is limited, the coding agent must still complete this minimum vertical slice:

```text
RData inspection
    ↓
TEP ingestion into PostgreSQL
    ↓
threshold derivation from fault-free training
    ↓
alarm generation for faulty testing
    ↓
duplicate filtering
    ↓
incident grouping
    ↓
dependency graph impact
    ↓
simulation timeline
    ↓
Flask dashboard pages
    ↓
BPMN process viewer
```

This minimum version is enough to demonstrate all job-relevant capabilities:

```text
Python
PostgreSQL
Flask
web application development
automated data analysis
alarm filtering
process simulation
critical infrastructure dependency modelling
Business Continuity reasoning
BPMN process modelling
research-prototype thinking
```
