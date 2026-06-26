# Limitations

## 1. Dataset Limitations

### 1.1 Tennessee Eastman Process is Not Maritime Data

The Tennessee Eastman Process (TEP) dataset is an open industrial benchmark for chemical process monitoring and fault detection. It is **not** real maritime critical-infrastructure operational data.

The dataset represents a simulated chemical plant with 41 measured variables (xmeas_1 to xmeas_41) and 11 manipulated variables (xmv_1 to xmv_11). It does not contain ship systems, port management data, or real maritime sensor streams.

### 1.2 Synthetic Infrastructure Model

The infrastructure dependency model (components, dependency edges), BCM profiles, and readiness questions are **synthetic research configurations** created to demonstrate how the methodology can be adapted. They are not based on real operational surveys, expert interviews, or validated dependency data.

### 1.3 No Real-Time Data

The system processes static pre-loaded `.RData` files. It does not connect to live industrial systems, SCADA systems, or real sensor feeds.

## 2. Alarm Pipeline Limitations

### 2.1 Rule-Based Thresholds

Alarm thresholds are derived statistically from the fault-free training data (quantile-based). They do not incorporate domain knowledge, sensor calibration information, or process-specific safe operating limits.

### 2.2 No Root-Cause Identification

The system identifies dominant affected components based on which component has the most alarms. It does not perform actual root-cause analysis. The `root_cause_candidate` field is a heuristic approximation.

### 2.3 Simplified Duplicate Filtering

Duplicate filtering uses a sliding time window of 3 steps applied to the same variable and alarm type. More sophisticated methods (e.g., nuisance alarm analysis, Petri-net-based alarm rationalisation) are not implemented.

## 3. Simulation Limitations

### 3.1 Linear Interruption Estimation

The estimated interruption time is calculated as a simple linear formula (base + 15 minutes per downstream component). It does not model component recovery curves, partial degradation, or redundancy.

### 3.2 No Stochastic Uncertainty

All simulation results are deterministic. Real cascading failure models would incorporate probabilistic failure rates, Monte Carlo simulation, or Bayesian uncertainty quantification.

## 4. Web Application Limitations

### 4.1 No Authentication

The web application has no authentication or access control. It is intended for local research use only.

### 4.2 Pagination Limitations

Some API endpoints are limited to 200 or 500 records. For large datasets, pagination or further filtering is required.

## 5. Research Scope Disclaimer

This prototype demonstrates how the complete chain from industrial alarm data to crisis-management tooling can be modelled in software. The results are illustrative only and are not suitable for operational decision-making in real critical-infrastructure scenarios.

In a real research project, all components — dependency model, alarm rules, BCM profiles, BPMN process — would be validated through:

- Literature review of KRITIS and BCM standards (ISO 22301, BSI-Kritisverordnung)
- Expert interviews with infrastructure operators
- Structured workshops with civil protection authorities
- Iterative validation of the alarm processing pipeline against labelled real data
