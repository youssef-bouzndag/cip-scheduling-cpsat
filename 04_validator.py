import pandas as pd

SETUP_MIN = 15  # must match 03_scheduler.py

production = pd.read_csv(
    "production.csv",
    parse_dates=["usage_end", "earliest_clean_start",
                 "latest_clean_start", "finish_deadline"]
)
schedule = pd.read_csv("schedule.csv", parse_dates=["start", "end"])
allowed = pd.read_csv("cleaning_tasks.csv")[["batch_id", "cleaning_resource"]]

ok = True

# Check 1: every batch is cleaned exactly once
counts = schedule["batch_id"].value_counts()
for b in production["batch_id"]:
    if counts.get(b, 0) != 1:
        print("CLEANED", counts.get(b, 0), "TIMES:", b)
        ok = False

# Check 2: the resource is connected to the equipment
pairs = set(zip(allowed["batch_id"], allowed["cleaning_resource"]))
for _, row in schedule.iterrows():
    if (row["batch_id"], row["resource"]) not in pairs:
        print("WRONG RESOURCE:", row["batch_id"], row["resource"])
        ok = False

# Check 3: window and deadline
check = schedule.merge(production, on="batch_id")
for _, row in check.iterrows():
    if row["start"] < row["earliest_clean_start"]:
        print("STARTED TOO EARLY:", row["batch_id"])
        ok = False
    if row["start"] > row["latest_clean_start"]:
        print("STARTED TOO LATE:", row["batch_id"])
        ok = False
    if row["end"] > row["finish_deadline"]:
        print("FINISHED AFTER DHT OR NEXT USE:", row["batch_id"])
        ok = False

# Check 4: no overlap on a resource, including the setup time
for r in schedule["resource"].unique():
    sub = schedule[schedule["resource"] == r].sort_values("start").reset_index(drop=True)
    for i in range(len(sub) - 1):
        gap = (sub.loc[i + 1, "start"] - sub.loc[i, "end"]).total_seconds() / 60
        if gap < SETUP_MIN:
            print("OVERLAP on", r, ":", sub.loc[i, "batch_id"], "->", sub.loc[i + 1, "batch_id"])
            ok = False

print("All checks passed" if ok else "Checks FAILED")