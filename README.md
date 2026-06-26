# KRITIS Alarm & Dependency Lab

A PostgreSQL-backed research prototype for filtering industrial alarm messages,
modelling critical-infrastructure dependencies, and supporting crisis-readiness analysis.
Built on the Tennessee Eastman Process (TEP) benchmark dataset.

---

## Table of Contents

1. [What This Project Does](#what-this-project-does)
2. [Requirements](#requirements)
3. [Step 1 — Clone the Repository](#step-1--clone-the-repository)
4. [Step 2 — Set Up PostgreSQL](#step-2--set-up-postgresql)
5. [Step 3 — Create a Python Virtual Environment](#step-3--create-a-python-virtual-environment)
6. [Step 4 — Install Dependencies](#step-4--install-dependencies)
7. [Step 5 — Configure Environment Variables](#step-5--configure-environment-variables)
8. [Step 6 — Initialise the Database](#step-6--initialise-the-database)
9. [Step 7 — Ingest TEP Sensor Data](#step-7--ingest-tep-sensor-data)
10. [Step 8 — Run the Web Application](#step-8--run-the-web-application)
11. [Using the Interactive Dashboard](#using-the-interactive-dashboard)
12. [Project Structure](#project-structure)
13. [Important Note on the Data](#important-note-on-the-data)

---

## What This Project Does

The lab ingests real **Tennessee Eastman Process** sensor data, detects threshold
breaches (alarms), clusters them into incidents, and presents everything through an
interactive web dashboard. Key features:

- 🚨 **Alarm Generation** — compare faulty sensor readings against fault-free baselines
- 🔥 **Incident Grouping** — cluster nearby alarms into manageable incidents
- 📋 **Readiness Assessment** — auto-score infrastructure preparedness
- 🕸 **Dependency Graph** — visualise component relationships
- ⚙️ **Simulation** — run cascading failure simulations
- 📊 **Live Dashboard** — click-driven pipeline with animated statistics and charts

---

## Application Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KRITIS ALARM & DEPENDENCY LAB                        │
│                          Full Execution Flow                                │
└─────────────────────────────────────────────────────────────────────────────┘

 ╔══════════════════════╗
 ║   RAW DATA (files)   ║
 ║  ──────────────────  ║
 ║  TEP_FaultFree_      ║
 ║  Training.RData      ║   500 simulation runs × 52 sensor variables
 ║                      ║   (normal baseline — no faults)
 ║  TEP_Faulty_         ║
 ║  Training.RData      ║   200 sampled faulty runs × 52 sensor variables
 ╚══════════╦═══════════╝   (21 fault types injected)
            │
            ▼
 ┌──────────────────────┐
 │  scripts/            │   PYTHONPATH=. python scripts/init_db.py
 │  init_db.py          │   → Creates all PostgreSQL tables
 │  seed_kritis_config  │   → Seeds: components, dependencies,
 │  .py                 │     readiness questions, BCM profiles
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │  scripts/            │   PYTHONPATH=. python scripts/preprocess_tep.py
 │  preprocess_tep.py   │
 │                      │   Reads .RData → pandas DataFrame
 │  [DEMO MODE]         │   Faulty files capped at 10 runs (memory safe)
 │  max 10 runs,        │   Samples every 10th row (÷10 row count)
 │  sample rate 1/10    │   Derives thresholds from fault-free baseline
 └──────────┬───────────┘
            │  Bulk INSERT into PostgreSQL
            ▼
 ┌──────────────────────────────────────────────────────────────────────────┐
 │                        PostgreSQL: kritis_alarm_lab                      │
 │  ┌────────────────┐  ┌──────────────────┐  ┌───────────────────────┐   │
 │  │  tep_runs      │  │ sensor_variables  │  │  variable_statistics  │   │
 │  │  (700 rows)    │  │  (52 variables)   │  │  (52 thresholds)      │   │
 │  └────────┬───────┘  └──────────────────┘  └───────────────────────┘   │
 │           │                                                              │
 │           │  sensor_observations (13,520,000 rows)                       │
 │           └──────────────────────────────────────────────────────────┐  │
 │                                                                       │  │
 │  ┌─────────────────────────────────────────────────────────────────┐ │  │
 │  │                    scripts/generate_alarms.py                   │◄┘  │
 │  │  For each faulty observation:                                   │    │
 │  │    if value > threshold → INSERT alarm_events (severity=critical)│   │
 │  │    if value > 0.5×threshold → INSERT alarm_events (warning)     │   │
 │  └──────────────────────────┬──────────────────────────────────────┘   │
 │                             │  alarm_events (~255,000 rows)             │
 │  ┌──────────────────────────▼──────────────────────────────────────┐   │
 │  │                    scripts/filter_alarms.py                     │   │
 │  │  Marks duplicate alarms (same variable, consecutive time steps) │   │
 │  └──────────────────────────┬──────────────────────────────────────┘   │
 │                             │                                           │
 │  ┌──────────────────────────▼──────────────────────────────────────┐   │
 │  │                    scripts/group_incidents.py                   │   │
 │  │  Clusters alarms in same component within a time window         │   │
 │  │  → incidents table (~64,000 incidents)                          │   │
 │  └──────────────────────────┬──────────────────────────────────────┘   │
 │                             │                                           │
 │  ┌──────────────────────────▼──────────────────────────────────────┐   │
 │  │              infrastructure_components, dependencies,           │   │
 │  │              readiness_questions, simulation_runs               │   │
 │  └─────────────────────────────────────────────────────────────────┘   │
 └──────────────────────────────────────────────────────────────────────────┘
            │
            ▼  PYTHONPATH=. python app.py
 ╔══════════════════════════════════════════════════════════════════════════╗
 ║                     FLASK WEB APPLICATION  :5000                        ║
 ║                                                                          ║
 ║   Browser Request                                                        ║
 ║        │                                                                 ║
 ║        ▼                                                                 ║
 ║   app/routes/pages.py ──────────────────────────────────────────────    ║
 ║   (renders Jinja2 templates)                                             ║
 ║        │                                                                 ║
 ║        ├── GET  /              → index.html  (Dashboard)                 ║
 ║        ├── GET  /alarms        → alarms.html (Filter + Chart + Table)    ║
 ║        ├── GET  /incidents     → incidents.html                          ║
 ║        ├── GET  /dependencies  → dependencies.html (Cytoscape graph)     ║
 ║        ├── GET  /simulation    → simulation.html                         ║
 ║        ├── GET  /readiness     → readiness.html (Assessment form)        ║
 ║        └── GET  /bpmn          → bpmn.html (Process diagram)             ║
 ║                                                                          ║
 ║   app/routes/api.py ─────────────────────────────────────────────────   ║
 ║   (JSON endpoints called by dashboard JS buttons)                        ║
 ║        │                                                                 ║
 ║        ├── GET  /api/pipeline/status          → live counts (all stages) ║
 ║        ├── GET  /api/pipeline/load-data       → stage-by-stage DB counts ║
 ║        ├── POST /api/pipeline/generate-alarms → runs alarm_generator.py  ║
 ║        ├── POST /api/pipeline/group-incidents → runs incident_grouper.py  ║
 ║        ├── POST /api/pipeline/run-readiness   → runs readiness_score.py  ║
 ║        ├── GET  /api/alarms?role=&severity=   → filtered alarm records   ║
 ║        ├── GET  /api/incidents                → incident records          ║
 ║        └── GET  /api/dependency-graph         → nodes + edges JSON        ║
 ║                                                                          ║
 ║   app/static/js/dashboard.js                                             ║
 ║   (drives the interactive pipeline panel)                                ║
 ║        │                                                                 ║
 ║        ├── Step 1: fetch /api/pipeline/load-data  → animated progress bar║
 ║        ├── Step 2: POST generate-alarms → counter animates, chart draws  ║
 ║        ├── Step 3: POST group-incidents → counter animates, chart draws   ║
 ║        └── Step 4: POST run-readiness  → gauge fills with colour         ║
 ╚══════════════════════════════════════════════════════════════════════════╝

 ┌──────────────────────────────────────────────────────────────────────────┐
 │                    SERVICES (app/services/)                              │
 │                                                                          │
 │  alarm_generator.py   Query observations → compare → INSERT alarms       │
 │  incident_grouper.py  Query alarms → time-window clustering → incidents  │
 │  readiness_score.py   Q&A answers → weighted scoring → assessment row    │
 │  dependency_analyzer  Walk dependency graph → cascade impact score       │
 └──────────────────────────────────────────────────────────────────────────┘
```

---

## Requirements

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11 or 3.12 | Runtime |
| PostgreSQL | 14+ | Database |
| pip | any | Python packages |
| git | any | Clone the repo |

> **No internet connection needed at runtime** — all JS assets are bundled locally.

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/tsyncIO/critical-infrastructure.git
cd critical-infrastructure
```

---

## Step 2 — Set Up PostgreSQL

You need a running PostgreSQL server with a database called `kritis_alarm_lab`.

### On Ubuntu / Debian:

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start the service
sudo systemctl start postgresql
sudo systemctl enable postgresql   # start automatically on boot

# Create the database
sudo -u postgres psql -c "CREATE DATABASE kritis_alarm_lab;"
```

> **What this does:** Creates an empty database that Flask will populate with tables
> automatically in Step 6.

The default credentials used in this project are:
- **User:** `postgres`
- **Password:** `postgres`
- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `kritis_alarm_lab`

If your PostgreSQL has a different password, you will update it in Step 5.

---

## Step 3 — Create a Python Virtual Environment

A virtual environment keeps the project's Python packages isolated from your system.

```bash
python3 -m venv .venv
```

Now **activate** the virtual environment:

```bash
# On Linux / macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

> **How to tell it worked:** Your terminal prompt will start with `(.venv)`.
> You must activate the venv every time you open a new terminal.

---

## Step 4 — Install Dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

> **What this installs:** Flask, SQLAlchemy, pandas, pyreadr (for `.RData` files),
> NumPy, and all other required packages. This takes 1–3 minutes.

---

## Step 5 — Configure Environment Variables

Copy the example config file and edit it if needed:

```bash
cp .env.example .env
```

Open `.env` and check the values:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/kritis_alarm_lab
FLASK_ENV=development
SECRET_KEY=change-me
FLASK_APP=app:create_app
```

> **Only change** `DATABASE_URL` if your PostgreSQL password or port is different.
> Leave everything else as-is for a local development setup.

---

## Step 6 — Initialise the Database

This creates all database tables and seeds the KRITIS configuration data.

```bash
# Create all database tables
PYTHONPATH=. python scripts/init_db.py

# Seed infrastructure components, questions, and dependency config
PYTHONPATH=. python scripts/seed_kritis_config.py
```

> **What to expect:**
> - `init_db.py` prints something like `"Database tables created successfully."`
> - `seed_kritis_config.py` prints the number of components and questions inserted.
> - If you see `"Table already exists"` — that is fine, it is idempotent.

---

## Step 7 — Ingest TEP Sensor Data

This is the main data pipeline. Run these scripts **in order**.

### 7a — Preprocess and ingest the RData files

```bash
PYTHONPATH=. python scripts/preprocess_tep.py
```

> **What to expect:** This takes 20–60 seconds.
> ```
> >> Processing TEP_FaultFree_Training.RData  (role=fault_free_training)
>    500 runs already ingested — will skip them.
>    File done in 3.0s total.
>
> >> Processing TEP_Faulty_Training.RData  (role=faulty_training)
>    [DEMO] Massive file detected — capping at 10 runs, sampling every 10th time-step.
>    Bulk-inserting 520,000 observations … done in 5.5s
>    File done in 20.4s total.
>
> >> Deriving thresholds from fault_free_training …
>    Thresholds derived for 52 variables.
>
> TEP ingestion complete.
> ```
> The `[DEMO]` cap keeps memory usage safe. The full file has 5M rows; we use 10 runs.

### 7b — Generate alarms from faulty data

```bash
PYTHONPATH=. python scripts/generate_alarms.py
```

> **What to expect:** Compares each faulty sensor reading against the fault-free
> threshold. Prints the number of alarm events inserted (expect ~85 000 – 255 000).

### 7c — Filter duplicate alarms (optional but recommended)

```bash
PYTHONPATH=. python scripts/filter_alarms.py
```

### 7d — Group alarms into incidents

```bash
PYTHONPATH=. python scripts/group_incidents.py
```

> **What to expect:** Clusters nearby alarms into incidents. Prints total incidents
> created (expect ~20 000 – 64 000).

### 7e — Run a sample simulation (optional)

```bash
PYTHONPATH=. python scripts/run_sample_simulation.py
```

---

## Step 8 — Run the Web Application

```bash
PYTHONPATH=. python app.py
```

> **What to expect:**
> ```
>  * Serving Flask app 'app'
>  * Debug mode: on
>  * Running on http://0.0.0.0:5000
> ```

Open your browser at **`http://localhost:5000`** (or replace `localhost` with your
server's IP address if running remotely).

> **To stop the server:** Press `Ctrl+C` in the terminal.

---

## Using the Interactive Dashboard

The dashboard has a **4-step pipeline**. Click each button in order:

| Step | Button | What Happens |
|---|---|---|
| 1 | 📦 **Load Data** | Progress bar fills showing files → runs → variables → observations |
| 2 | 🚨 **Generate Alarms** | Runs alarm detection; stat cards animate to new counts |
| 3 | 🔥 **Group Incidents** | Clusters alarms; pie chart draws |
| 4 | 📋 **Run Assessment** | Scores readiness; gauge fills with colour |

### Navigation

| Page | URL | Description |
|---|---|---|
| Dashboard | `/` | Interactive pipeline control panel |
| Alarms | `/alarms` | Filter and visualise alarm events |
| Incidents | `/incidents` | View grouped incident records |
| Dependencies | `/dependencies` | Infrastructure component graph |
| Simulation | `/simulation` | Run cascading failure scenarios |
| Readiness | `/readiness` | Full readiness assessment form |
| BPMN | `/bpmn` | Crisis response process diagram |

---

## Project Structure

```
critical-infrastructure/
├── app/
│   ├── models.py              # SQLAlchemy database models
│   ├── extensions.py          # Flask extensions (db, migrate)
│   ├── __init__.py            # App factory
│   ├── routes/
│   │   ├── api.py             # JSON API endpoints + pipeline actions
│   │   └── pages.py           # Page routes (Dashboard, Alarms, etc.)
│   ├── services/
│   │   ├── alarm_generator.py # Threshold-breach detection
│   │   ├── incident_grouper.py# Temporal alarm clustering
│   │   └── readiness_score.py # Readiness scoring engine
│   ├── templates/             # Jinja2 HTML templates
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── dashboard.js   # Pipeline button logic + animated counters
│           └── plotly.min.js  # Plotly charting (bundled locally)
├── scripts/
│   ├── init_db.py             # Create database tables
│   ├── seed_kritis_config.py  # Seed infrastructure config
│   ├── preprocess_tep.py      # Ingest TEP RData files → PostgreSQL
│   ├── generate_alarms.py     # Generate alarm events
│   ├── filter_alarms.py       # Mark duplicate alarms
│   ├── group_incidents.py     # Cluster alarms into incidents
│   └── run_sample_simulation.py
├── Data/
│   ├── TEP_FaultFree_Training.RData   # Normal baseline sensor data
│   └── TEP_Faulty_Training.RData      # Faulty sensor data (21 fault types)
├── config/                    # Flask configuration classes
├── app.py                     # Application entry point
├── requirements.txt
└── .env.example
```

---

## Important Note on the Data

The **Tennessee Eastman Process** dataset is a real, open industrial benchmark used
worldwide for process monitoring and fault detection research.

However:
- The **infrastructure dependency model** (port operations, cooling systems, etc.) is synthetic.
- The **BCM profiles** and **BPMN crisis-response process** are example research configurations.
- This project shows *how the method works*, not real maritime infrastructure data.

---

## Quick Reference — All Commands

```bash
# 1. Clone
git clone https://github.com/tsyncIO/critical-infrastructure.git
cd critical-infrastructure

# 2. PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE kritis_alarm_lab;"

# 3. Virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install packages
pip install -r requirements.txt

# 5. Configure
cp .env.example .env   # edit if needed

# 6. Database setup
PYTHONPATH=. python scripts/init_db.py
PYTHONPATH=. python scripts/seed_kritis_config.py

# 7. Data pipeline
PYTHONPATH=. python scripts/preprocess_tep.py
PYTHONPATH=. python scripts/generate_alarms.py
PYTHONPATH=. python scripts/filter_alarms.py
PYTHONPATH=. python scripts/group_incidents.py

# 8. Run the app
PYTHONPATH=. python app.py
# → Open http://localhost:5000
```
