# CIP Scheduling with CP-SAT

A small **Cleaning-in-Place (CIP) scheduling tool** for a manufacturing plant.

Given a fixed production plan, the scheduler decides **when each piece of equipment should be cleaned** and **which cleaning resource should perform the cleaning**, with the objective of minimizing equipment waiting time before cleaning.

Built with **Python, Pandas, and Google OR-Tools CP-SAT**.

All data is simulated.

---

## Contents

1. [The Problem](#1-the-problem)
2. [How It Works](#2-how-it-works)
3. [Key Ideas](#3-key-ideas)
4. [Run the Project](#4-run-the-project)
5. [Output](#5-output)
6. [Limitations](#6-limitations)
7. [Possible Next Steps](#7-possible-next-steps)
8. [Requirements](#8-requirements)
9. [License](#9-license)

---

## 1. The Problem

The project addresses the scheduling of **Cleaning-in-Place (CIP)** operations in a manufacturing environment.

The basic situation is:

* Production batches use equipment according to a fixed timetable.
* After each batch, the equipment must be cleaned.
* Cleaning must start after production ends.
* Cleaning must finish before the **Dirty Hold Time (DHT)** limit expires and before the equipment is used again.
* Only certain cleaning resources can access each piece of equipment.
* Each cleaning resource can handle only one cleaning operation at a time.
* A cleaning resource also requires a **setup/flush time** after each cleaning.

When several batches require the same cleaning resource at overlapping times, some cleaning operations may have to wait.

The scheduler finds a feasible assignment and timing that **minimizes total waiting time**.

---

## 2. How It Works

The project is organized into five steps.

### Step 1 — `01_create_data.py`

Builds the production plan and calculates the cleaning window for each batch:

* Earliest possible start
* Latest possible start
* Slack

The script stops if any cleaning window is impossible.

### Step 2 — `02_cleaning_tasks.py`

Generates all possible **(batch, cleaning resource)** combinations based on the equipment-resource compatibility table.

### Step 3 — `03_scheduler.py`

Builds and solves the **CP-SAT optimization model**.

The model determines:

* One cleaning start time for each batch
* One compatible cleaning resource for each batch
* No overlap between jobs assigned to the same resource
* Setup/flush time after each cleaning
* Minimum total waiting time

### Step 4 — `04_validator.py`

Independently checks the scheduler's solution using plain Pandas.

The validator checks:

* Every batch has exactly one cleaning
* The selected resource is compatible
* Cleaning starts within the allowed time window
* The DHT and next-use deadlines are respected
* Cleaning and setup do not overlap with another job on the same resource

### Step 5 — `05_report.py`

Generates an Excel report:

```text
cleaning_report.xlsx
```

with detailed scheduling and resource-utilization information.

---

## 3. Key Ideas

### Slack

**Slack** represents the size of a batch's allowed cleaning-start window.

A negative slack means that the production plan itself is infeasible.

In that case, no scheduler can produce a valid solution without changing the production plan or the cleaning constraints.

### Waiting

**Waiting** is the time between the equipment becoming ready for cleaning and the actual start of its cleaning operation.

Reducing this waiting time is the main optimization objective.

### Optional Intervals

Optional intervals allow the CP-SAT solver to choose between compatible cleaning resources.

A cleaning operation only occupies the resource to which it is assigned.

### Setup Time

Setup/flush time is included directly in the scheduling interval.

Therefore, if a cleaning takes 30 minutes and the required setup time is 15 minutes, the resource remains occupied for:

```text
30 + 15 = 45 minutes
```

This prevents another cleaning from starting before the required flush is complete.

### Independent Validation

The validator uses logic separate from the optimization model.

This provides an additional layer of verification and helps detect potential modeling or scheduling errors.

---

## 4. Run the Project

Install the required packages:

```bash
pip install -r requirements.txt
```

Then run the scripts in order:

```bash
python 01_create_data.py
python 02_cleaning_tasks.py
python 03_scheduler.py
python 04_validator.py
python 05_report.py
```

### Important: Setup Time

The scheduler, validator, and report all use the setup-time parameter:

```text
SETUP_MIN
```

Keep the same value everywhere it appears.

If different values are used, the validator and report may no longer match the generated schedule.

---

## 5. Output

The `cleaning_report.xlsx` workbook contains several sheets.

| Sheet                 | Description                                                               |
| --------------------- | ------------------------------------------------------------------------- |
| **Summary**           | Total waiting, waiting batches, busiest resource, and tightest batch      |
| **Waiting batches**   | Waiting batches, blocking cleaning, and reason for waiting                |
| **Resource workload** | Cleaning, setup, busy, and idle minutes per resource, including job order |
| **Resource timeline** | Cleaning operations in sequence and the idle gap before each job          |
| **Equipment**         | Cleanings, waiting time, and tightest slack by equipment                  |
| **All batches**       | Complete batch-level scheduling information                               |
| **Definitions**       | Explanations of waiting, slack, busy, idle, and other terms               |

Waiting batches are highlighted in the report to make scheduling conflicts easier to identify.

### Example

A sample output is provided in:

```text
sample_output/
```

For example, with **4 batches, 3 equipment units, and 2 cleaning resources**, using a **15-minute setup time**, one batch (`B004`) waits for 15 minutes.

Its only compatible resource is still performing the required flush after a previous cleaning, even though that resource is idle for most of the day.

This illustrates an important scheduling principle:

> **Overall resource idle time does not necessarily mean that no batch has to wait.**

A resource can be idle for long periods while still causing waiting at a specific point in the schedule because of its availability and compatibility constraints.

---

## 6. Limitations

The current model has several simplifying assumptions:

* **Clean Hold Time (CHT)** is not modeled yet.
* Setup time depends only on the cleaning resource and not on the sequence of products.
* The plant is small and uses simulated data:

  * 4 batches
  * 3 equipment units
  * 2 cleaning resources
* Maintenance scheduling is not currently modeled.

---

## 7. Possible Next Steps

Potential extensions include:

* Model **CHT** as a soft constraint with a penalty for re-cleaning.
* Add **frozen cleaning operations** that are already fixed in the schedule.
* Add **what-if scenarios**, such as:

  * Production delays
  * Cleaning-resource outages
  * Changes in DHT
  * Changes in setup time
* Extend the model to larger production plans and additional cleaning resources.
* Add maintenance constraints and resource availability windows.

---

## 8. Requirements

* Python 3.9+
* Pandas
* Google OR-Tools
* OpenPyXL

See `requirements.txt` for the required packages.

---

## 9. License

This project is licensed under the **MIT License**.
