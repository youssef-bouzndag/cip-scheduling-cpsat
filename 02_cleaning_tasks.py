import pandas as pd

# Load the data from Lesson 1
production = pd.read_csv(
    "production.csv",
    parse_dates=["usage_start", "usage_end",
                 "earliest_clean_start", "latest_clean_start"]
)
# Pipe network: which cleaning resource can reach which equipment
compatibility = pd.DataFrame([
    {"cleaning_resource": "CIP_1", "equipment": "EQ01"},
    {"cleaning_resource": "CIP_1", "equipment": "EQ02"},
    {"cleaning_resource": "CIP_2", "equipment": "EQ02"},
    {"cleaning_resource": "CIP_2", "equipment": "EQ03"},
])
# One row for every possible (batch, cleaning resource) pair
tasks = production.merge(compatibility, on="equipment")
# Count how many options each batch has
options = tasks.groupby("batch_id")["cleaning_resource"].count()
tasks["n_options"] = tasks["batch_id"].map(options)
tasks.to_csv("cleaning_tasks.csv", index=False)
print(tasks[["batch_id", "equipment", "cleaning_resource",
             "earliest_clean_start", "latest_clean_start",
             "cleaning_duration_min", "n_options"]]
      .to_string(index=False))
# Workload per cleaning resource
print()
print("Cleaning minutes if each batch used this resource:")
print(tasks.groupby("cleaning_resource")["cleaning_duration_min"].sum())
