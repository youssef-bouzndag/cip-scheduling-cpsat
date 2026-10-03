import pandas as pd

# Simulated pharmaceutical production data
production = pd.DataFrame([
    {"batch_id": "B001", "equipment": "EQ01", "product": "Product_A",
     "usage_start": "2026-10-05 08:00", "usage_end": "2026-10-05 12:00",
     "cleaning_duration_min": 90, "dht_hours": 4, "cht_hours": 24},
    {"batch_id": "B002", "equipment": "EQ02", "product": "Product_B",
     "usage_start": "2026-10-05 09:00", "usage_end": "2026-10-05 13:00",
     "cleaning_duration_min": 60, "dht_hours": 5, "cht_hours": 24},
    {"batch_id": "B003", "equipment": "EQ01", "product": "Product_C",
     "usage_start": "2026-10-05 15:00", "usage_end": "2026-10-05 18:00",
     "cleaning_duration_min": 120, "dht_hours": 3, "cht_hours": 12},
    {"batch_id": "B004", "equipment": "EQ03", "product": "Product_A",
     "usage_start": "2026-10-05 10:00", "usage_end": "2026-10-05 14:00",
     "cleaning_duration_min": 90, "dht_hours": 4, "cht_hours": 24},
])
# Convert dates to datetime
production["usage_start"] = pd.to_datetime(production["usage_start"])
production["usage_end"] = pd.to_datetime(production["usage_end"])
# Sort so batches on the same equipment are in time order
production = production.sort_values(["equipment", "usage_start"]).reset_index(drop=True)
# When does the same equipment get used next? (empty if never)
production["next_use_start"] = production.groupby("equipment")["usage_start"].shift(-1)
# Cleaning can start as soon as production ends
production["earliest_clean_start"] = production["usage_end"]
# Cleaning must FINISH before the DHT limit...
production["dht_deadline"] = (
    production["usage_end"] + pd.to_timedelta(production["dht_hours"], unit="h")
)
# ...and before the next use of the equipment, whichever comes first
production["finish_deadline"] = production["dht_deadline"]
for i in range(len(production)):
    next_use = production.loc[i, "next_use_start"]
    if pd.notna(next_use) and next_use < production.loc[i, "dht_deadline"]:
        production.loc[i, "finish_deadline"] = next_use
# Latest cleaning start = finish deadline minus cleaning time
production["latest_clean_start"] = (
    production["finish_deadline"]
    - pd.to_timedelta(production["cleaning_duration_min"], unit="min")
)
# Slack = how much room the scheduler has
production["slack_min"] = (
    production["latest_clean_start"] - production["earliest_clean_start"]
).dt.total_seconds() / 60
production.to_csv("production.csv", index=False)
print(production[["batch_id", "equipment", "usage_end", "next_use_start",
                  "earliest_clean_start", "latest_clean_start", "slack_min"]]
      .to_string(index=False))
if (production["slack_min"] < 0).any():
    print("\nIMPOSSIBLE: negative slack for", list(production[production["slack_min"] < 0]["batch_id"]))
    raise SystemExit