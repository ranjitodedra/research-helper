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

def extract_swap_time(path: Path) -> int:
    """
    Extracts swap time value from filename.
    Examples:
      1min_summary.csv           -> 1
      2min_summary.csv           -> 2
      3min_summary.csv           -> 3
      4min_summary.csv           -> 4
    """
    s = path.stem
    # Match number before "min" (e.g., "1min", "3min")
    m = re.search(r"(\d+)min", s, re.IGNORECASE)
    if m:
        return int(m.group(1))
    raise ValueError(f"Could not extract swap time from filename: {path.name}")

def summarize_one(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    # ensure numeric
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    means = df[NUM_COLS].mean()

    swap_time = extract_swap_time(csv_path)
    
    out = {
        "Swap Time (min)": swap_time,
        "Total Travel Time": float(f"{means['Total Travel Time']:.2f}"),
        "Total Energy Consumed": float(f"{means['Total Energy Consumed']:.3f}"),
        "Total Distance Covered": float(f"{means['Total Distance Covered']:.2f}"),
        "Run Time": float(f"{means['Run Time']:.3f}"),
        "Total Module Swapped": int(round(means["Total Module Swapped"])),
    }
    return out

def main():
    rows = []
    # Match files like *min*.csv (e.g., 1min_summary.csv, 2min_summary.csv)
    for csv_path in sorted(INPUT_DIR.glob("*min*.csv")):
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
        "Swap Time (min)",
        "Total Travel Time",
        "Total Energy Consumed",
        "Total Distance Covered",
        "Run Time",
        "Total Module Swapped",
    ])
    # Sort by Swap Time (min)
    data = data.sort_values("Swap Time (min)")
    data.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(data)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()

