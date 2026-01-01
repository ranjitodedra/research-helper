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

def extract_module_count(path: Path) -> int:
    """
    Extracts module count value from filename.
    Examples:
      3module.csv           -> 3
      4module.csv           -> 4
      5module.csv           -> 5
      6module.csv           -> 6
    """
    s = path.stem
    # Match number before "module" (e.g., "3module", "4module")
    m = re.search(r"^(\d+)module", s, re.IGNORECASE)
    if m:
        return int(m.group(1))
    raise ValueError(f"Could not extract module count from filename: {path.name}")

def summarize_one(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    # ensure numeric
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    means = df[NUM_COLS].mean()

    module_count = extract_module_count(csv_path)
    
    out = {
        "Modules": module_count,
        "Total Travel Time": float(f"{means['Total Travel Time']:.2f}"),
        "Total Energy Consumed": float(f"{means['Total Energy Consumed']:.3f}"),
        "Total Distance Covered": float(f"{means['Total Distance Covered']:.2f}"),
        "Run Time": float(f"{means['Run Time']:.3f}"),
        "Total Module Swapped": int(round(means["Total Module Swapped"])),
    }
    return out

def main():
    rows = []
    # Match files like *module.csv (e.g., 3module.csv, 4module.csv)
    for csv_path in sorted(INPUT_DIR.glob("*module.csv")):
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
        "Modules",
        "Total Travel Time",
        "Total Energy Consumed",
        "Total Distance Covered",
        "Run Time",
        "Total Module Swapped",
    ])
    # Sort by Modules
    data = data.sort_values("Modules")
    data.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(data)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()

