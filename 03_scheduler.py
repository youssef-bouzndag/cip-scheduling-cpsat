import pandas as pd
from ortools.sat.python import cp_model

SETUP_MIN = 15  # flush time a cleaning resource needs after each cleaning

# Load the cleaning tasks from Lesson 2
tasks = pd.read_csv(
    "cleaning_tasks.csv",
    parse_dates=["earliest_clean_start", "latest_clean_start"]
)

# The solver only works with integers, so we use "minutes since origin"
origin = tasks["earliest_clean_start"].min().normalize()

tasks["earliest_min"] = ((tasks["earliest_clean_start"] - origin)
                         .dt.total_seconds() / 60).astype(int)
tasks["latest_min"] = ((tasks["latest_clean_start"] - origin)
                       .dt.total_seconds() / 60).astype(int)

model = cp_model.CpModel()

start = {}      # batch -> start time of its cleaning
chosen = {}     # (batch, resource) -> 1 if this resource cleans this batch
intervals = {}  # resource -> list of blocked intervals

for _, row in tasks.iterrows():
    b = row["batch_id"]
    r = row["cleaning_resource"]
    duration = int(row["cleaning_duration_min"])

    # One start variable per batch, limited to its window from Lesson 1
    if b not in start:
        start[b] = model.NewIntVar(
            int(row["earliest_min"]), int(row["latest_min"]), f"start_{b}"
        )

    # Yes/no: is batch b cleaned by resource r?
    chosen[(b, r)] = model.NewBoolVar(f"{b}_{r}")

    # The resource is blocked for the cleaning AND the setup time after it
    interval = model.NewOptionalFixedSizeIntervalVar(
        start[b], duration + SETUP_MIN, chosen[(b, r)], f"interval_{b}_{r}"
    )
    intervals.setdefault(r, []).append(interval)

# Rule 1: each batch is cleaned by exactly one resource
for b in start:
    options = [chosen[(bb, r)] for (bb, r) in chosen if bb == b]
    model.AddExactlyOne(options)

# Rule 2: a resource handles only one cleaning (plus setup) at a time
for r in intervals:
    model.AddNoOverlap(intervals[r])

# Goal: minimize total waiting time after production ends
earliest = tasks.groupby("batch_id")["earliest_min"].first()
model.Minimize(sum(start[b] - int(earliest[b]) for b in start))

# Solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print("Total waiting time (min):", solver.ObjectiveValue())

    rows = []
    for (b, r), var in chosen.items():
        if solver.Value(var) == 1:
            duration = int(tasks[(tasks["batch_id"] == b) &
                                 (tasks["cleaning_resource"] == r)]
                           ["cleaning_duration_min"].iloc[0])
            t_start = origin + pd.Timedelta(minutes=solver.Value(start[b]))
            t_end = t_start + pd.Timedelta(minutes=duration)
            waiting = solver.Value(start[b]) - int(earliest[b])
            rows.append({"batch_id": b, "resource": r,
                         "start": t_start, "end": t_end,
                         "waiting_min": waiting})

    schedule = pd.DataFrame(rows).sort_values(["resource", "start"])

    # Save full dates for the validator
    schedule.to_csv("schedule.csv", index=False)

    # Readable version
    show = schedule.copy()
    show["start"] = show["start"].dt.strftime("%m-%d %H:%M")
    show["end"] = show["end"].dt.strftime("%m-%d %H:%M")
    print()
    print(show.to_string(index=False))

    # Which batches wait?
    late = schedule[schedule["waiting_min"] > 0]
    if len(late) == 0:
        print("\nNo batch waits.")
    else:
        print("\nBatches that wait:")
        print(late[["batch_id", "resource", "waiting_min"]].to_string(index=False))
else:
    print("No feasible schedule found")