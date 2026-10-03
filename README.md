CIP SCHEDULING WITH CP-SAT

A small scheduler for cleaning-in-place (CIP) jobs in a manufacturing plant.
Given a fixed production plan, it decides WHEN each piece of equipment is
cleaned, and WHICH cleaning resource does it, so that equipment waits dirty
for as little time as possible.

Built with Python, pandas, and Google OR-Tools CP-SAT.
All data is simulated.

1. THE PROBLEM

---

* Production batches use equipment on a fixed timetable.
* After each batch, the equipment must be cleaned.
* Cleaning must start after production ends, and finish before the
dirty-hold limit (DHT) runs out and before the equipment is used again.
* Only certain cleaning resources can reach each piece of equipment.
* A cleaning resource handles one cleaning at a time and needs a setup
(flush) time afterwards.

When several batches need the same resource at the same time, some have to
wait. The scheduler finds the plan with the least total waiting.

1. HOW IT WORKS

---

Step 1 - 01_create_data.py
Builds the production plan and computes each batch’s cleaning window
(earliest start, latest start, slack). Stops if any window is impossible.

Step 2 - 02_cleaning_tasks.py
Lists every possible (batch, cleaning resource) pair using the
compatibility table.

Step 3 - 03_scheduler.py
CP-SAT model: one start time per batch, one resource per batch, no
overlap on a resource (including setup), minimize total waiting.

Step 4 - 04_validator.py
Re-checks the result in plain pandas: one cleaning per batch, compatible
resource, time window, DHT/next-use deadline, no overlap with setup.

Step 5 - 05_report.py
Writes cleaning_report.xlsx with the details listed in section 5.

1. KEY IDEAS

---

* Slack: the size of a batch’s allowed start window. Negative slack means
the production plan itself is infeasible, which no scheduler can fix.
* Waiting: the time between the equipment being ready and its cleaning
starting.
* Optional intervals: let the solver choose between resources; a cleaning
only blocks the resource it is assigned to.
* Setup time: modeled by making each interval longer than the cleaning
itself, so the next job on that resource cannot start until the flush
is done.
* Independent validator: a separate script checks the solver’s answer with
different logic, so modeling mistakes are caught.
1. RUN IT

---

pip install -r requirements.txt
python 01_create_data.py
python 02_cleaning_tasks.py
python 03_scheduler.py
python 04_validator.py
python 05_report.py

NOTE: The scheduler, the validator

and the report use the setup time (SETUP_MIN). Keep the same value in every place it appears; otherwise
the validator and report will not match the schedule.

1. OUTPUT

---

cleaning_report.xlsx has these sheets:

* Summary            : Total waiting, which batches wait, busiest resource,
tightest batch
* Waiting batches    : Each waiting batch, which cleaning blocked it, and
the reason
* Resource workload: Cleaning, setup, busy and idle minutes per resource,
and job order
* Resource timeline: Each cleaning in sequence with the idle gap before it
* Equipment          : Cleanings, waiting, and tightest slack per equipment
* All batches        : Everything per batch, with waiting rows highlighted
* Definitions        : Waiting, slack, busy, idle, and other terms explained

A sample is in sample_output/.

Example (simulated data, setup 15 min):
With 4 batches, 3 equipment units and 2 cleaning resources, one batch
(B004) waits 15 minutes. Its only compatible resource is still flushing
after a previous cleaning, even though that resource is idle for most of
the day. This shows why idle time alone does not tell you whether anyone
waits.

1. LIMITATIONS

---

* Clean-hold time (CHT) is not modeled yet.
* Setup time depends on the resource only, not on the sequence of products.
* The plant is small and simulated (4 batches, 3 equipment, 2 resources).
* Maintenance scheduling is not modeled (possible extension).
1. POSSIBLE NEXT STEPS

---

* Model CHT as a soft rule with a penalty for re-cleaning.
* Add frozen (already fixed) cleanings.
* Add what-if scenarios (late production, resource outage) to test whether
a plan can change.
1. REQUIREMENTS

---

Python 3.9+, pandas, ortools, openpyxl (see requirements.txt).

1. LICENSE

---

MIT
