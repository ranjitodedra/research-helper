# aggregate_means.py
import re
from pathlib import Path
import pandas as pd

INPUT_DIR = Path(".")            # put all your per-run CSVs here
OUTPUT = Path("data.csv")           # aggregated table

NUM_COLS = [
    "Total Travel Time",
    "Total Energy Consumed",
    "Total Distance Covered",
    "Run Time",
    "Total Module Swapped",
]

# Define sort order for traffic levels
TRAFFIC_ORDER = {"Low": 1, "Mid": 2, "High": 3}

def extract_traffic_level(path: Path) -> str:
    """
    Extracts traffic level from filename.
    Examples:
      Low_batch.csv   -> Low
      Mid_batch.csv   -> Mid
      High_batch.csv  -> High
    """
    s = path.stem
    # Remove "_batch" suffix if present
    level = s.replace("_batch", "")
    if level in TRAFFIC_ORDER:
        return level
    raise ValueError(f"Could not extract traffic level from filename: {path.name}")

def summarize_one(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    # ensure numeric
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    means = df[NUM_COLS].mean()

    traffic_level = extract_traffic_level(csv_path)
    
    out = {
        "Traffic Level": traffic_level,
        "Total Travel Time": float(f"{means['Total Travel Time']:.2f}"),
        "Total Energy Consumed": float(f"{means['Total Energy Consumed']:.3f}"),
        "Total Distance Covered": float(f"{means['Total Distance Covered']:.2f}"),
        "Run Time": float(f"{means['Run Time']:.3f}"),
        "Total Module Swapped": int(round(means["Total Module Swapped"])),
    }
    return out

def main():
    rows = []
    for csv_path in sorted(INPUT_DIR.glob("*_batch.csv")):
        if csv_path.name.lower() == OUTPUT.name.lower():
            continue
        try:
            rows.append(summarize_one(csv_path))
        except Exception as e:
            print(f"Skip {csv_path.name}: {e}")

    if not rows:
        print("No input CSVs found.")
        return

    data = pd.DataFrame(rows, columns=[
        "Traffic Level",
        "Total Travel Time",
        "Total Energy Consumed",
        "Total Distance Covered",
        "Run Time",
        "Total Module Swapped",
    ])
    # Sort by traffic level order (Low, Mid, High)
    data["_sort_order"] = data["Traffic Level"].map(TRAFFIC_ORDER)
    data = data.sort_values("_sort_order")
    data = data.drop(columns=["_sort_order"])
    data.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(data)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()

