# Data Dictionary – KRITIS Alarm & Dependency Lab

## PostgreSQL Tables

### `raw_dataset_files`
Tracks each `.RData` source file loaded into the system.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment |
| `file_name` | VARCHAR | File name (e.g., `TEP_Faulty_Testing.RData`) |
| `file_path` | TEXT | Relative path to the file |
| `file_size_bytes` | BIGINT | File size in bytes |
| `dataset_role` | VARCHAR | One of: `fault_free_training`, `fault_free_testing`, `faulty_training`, `faulty_testing` |
| `created_at` | TIMESTAMP | Ingest timestamp |

### `tep_runs`
One record per simulation run within a TEP dataset.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `dataset_file_id` | FK → `raw_dataset_files` | |
| `run_id` | VARCHAR | Derived key: `{role}-{fault_id}-{sim_run}` |
| `dataset_role` | VARCHAR | Same as parent file |
| `fault_id` | INTEGER | 0 = fault-free, 1–20 = fault type |
| `fault_label` | VARCHAR | `fault_free` or `fault_{n}` |
| `is_faulty` | BOOLEAN | True if fault_id != 0 |
| `row_count` | INTEGER | Number of time steps |
| `variable_count` | INTEGER | Number of sensor variables in this run |

### `sensor_variables`
Unique sensor variable definitions, shared across all runs.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `variable_name` | VARCHAR UNIQUE | e.g., `xmeas_1`, `xmv_9` |
| `display_name` | VARCHAR | Human-readable name |
| `component_key` | VARCHAR | Infrastructure component this variable maps to |
| `variable_group` | VARCHAR | `measurement` (xmeas_) or `manipulated` (xmv_) |

### `sensor_observations`
Long-format sensor values: one row per (run, time_step, variable).

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `run_id` | FK → `tep_runs` | |
| `time_step` | INTEGER | Simulation time index |
| `variable_id` | FK → `sensor_variables` | |
| `variable_value` | DOUBLE | Actual sensor reading |

### `variable_statistics`
Baseline statistics and alarm thresholds, derived from fault-free training data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `variable_id` | FK → `sensor_variables` | |
| `baseline_mean` | DOUBLE | Mean of fault-free training values |
| `baseline_std` | DOUBLE | Standard deviation |
| `q001`..`q999` | DOUBLE | Quantile values (0.1%, 0.5%, 2.5%, 50%, 97.5%, 99.5%, 99.9%) |
| `warning_low` | DOUBLE | q005 threshold (lower warning bound) |
| `warning_high` | DOUBLE | q995 threshold (upper warning bound) |
| `critical_low` | DOUBLE | q001 threshold (lower critical bound) |
| `critical_high` | DOUBLE | q999 threshold (upper critical bound) |
| `derived_from_role` | VARCHAR | Always `fault_free_training` |

### `alarm_events`
One record per alarm condition detected in sensor data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `run_id` | FK → `tep_runs` | |
| `observation_id` | FK → `sensor_observations` | Source observation (nullable) |
| `time_step` | INTEGER | When the alarm was triggered |
| `variable_id` | FK → `sensor_variables` | Which variable triggered |
| `component_key` | VARCHAR | Component associated with the variable |
| `alarm_type` | VARCHAR | `warning_high_alarm`, `warning_low_alarm`, `critical_high_alarm`, `critical_low_alarm` |
| `severity` | VARCHAR | `warning` or `critical` |
| `message` | TEXT | Human-readable alarm message |
| `deviation_value` | DOUBLE | How far the value exceeded the threshold |
| `threshold_value` | DOUBLE | Which threshold was crossed |
| `is_duplicate` | BOOLEAN | True if marked as duplicate by alarm filter |

### `incidents`
Grouped alarm clusters representing infrastructure events.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `run_id` | FK → `tep_runs` | |
| `title` | VARCHAR | Auto-generated human-readable title |
| `severity` | VARCHAR | `critical` or `warning` |
| `status` | VARCHAR | `open` or `closed` |
| `raw_alarm_count` | INTEGER | Total alarms in the group |
| `unique_alarm_count` | INTEGER | Non-duplicate alarms |
| `affected_component_count` | INTEGER | Distinct components |
| `first_time_step` | INTEGER | Start of alarm window |
| `last_time_step` | INTEGER | End of alarm window |
| `root_cause_candidate` | VARCHAR | Component with most alarms |
| `explanation` | TEXT | Auto-generated explanation |

### `infrastructure_components`
Synthetic KRITIS component definitions (research configuration).

| Column | Type | Description |
|--------|------|-------------|
| `component_key` | VARCHAR UNIQUE | System identifier |
| `display_name` | VARCHAR | Human-readable name |
| `sector` | VARCHAR | KRITIS sector |
| `responsible_org` | VARCHAR | Responsible organisation |
| `description` | TEXT | Component description |

### `infrastructure_dependencies`
Directed dependency edges between components (research configuration).

| Column | Type | Description |
|--------|------|-------------|
| `source_component_id` | FK → components | Upstream (depends on target) |
| `target_component_id` | FK → components | Downstream (affected if source fails) |
| `dependency_type` | VARCHAR | Type of dependency |
| `criticality` | VARCHAR | `high`, `medium`, `low` |
| `description` | TEXT | Dependency description |

### `bcm_profiles`
Business Continuity Management parameters per component.

| Column | Type | Description |
|--------|------|-------------|
| `component_id` | FK → components | |
| `maximum_tolerable_downtime_min` | INTEGER | MTD in minutes |
| `recovery_time_objective_min` | INTEGER | RTO in minutes |
| `backup_available` | BOOLEAN | Whether backup exists |
| `backup_duration_min` | INTEGER | Backup endurance |
| `recovery_action` | TEXT | Recommended recovery action |
| `emergency_contact_role` | VARCHAR | Who to contact |

### `simulation_runs`
Results of cascading impact simulations.

| Column | Type | Description |
|--------|------|-------------|
| `incident_id` | FK → incidents | |
| `scenario_name` | VARCHAR | e.g., `default`, `worst-case` |
| `estimated_interruption_min` | INTEGER | Modelled interruption duration |
| `continuity_risk` | VARCHAR | `high`, `medium`, `low` |
| `recommendation` | TEXT | BCM recovery recommendation |
| `started_at` | TIMESTAMP | |

### `readiness_questions`
Fixed question bank for readiness assessments.

| Column | Type | Description |
|--------|------|-------------|
| `question_key` | VARCHAR UNIQUE | Machine key |
| `question_text` | TEXT | Full question text |
| `category` | VARCHAR | Category (e.g., BCM, Communication) |
| `weight` | FLOAT | Importance weight for scoring |

### `readiness_assessments`
Scored readiness assessment sessions.

| Column | Type | Description |
|--------|------|-------------|
| `title` | VARCHAR | Assessment title |
| `total_score` | FLOAT | Weighted sum of scored answers |
| `max_score` | FLOAT | Maximum possible weighted score |
| `percentage_score` | FLOAT | `total_score / max_score × 100` |
| `created_at` | TIMESTAMP | |

## TEP Variable Descriptions

| Variable | Description | Component |
|----------|-------------|-----------|
| xmeas_1–20 | Reactor, separator, stripper measurements | industrial_process |
| xmeas_21 | Reactor cooling water outlet temperature | cooling_system |
| xmeas_22 | Separator cooling water outlet temperature | cooling_system |
| xmeas_23–41 | Quality/composition analysers | port_operations |
| xmv_1–11 | Manipulated control variables (valve positions, flow rates) | process_control_system |
