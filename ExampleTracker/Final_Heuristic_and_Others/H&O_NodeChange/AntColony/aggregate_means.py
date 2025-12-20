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

def extract_nodes(path: Path) -> int:
    """
    Extracts node count from filename.
    Examples:
      50_summary.csv   -> 50
      100_summary.csv  -> 100
      150_summary.csv  -> 150
      200_summary.csv  -> 200
    """
    s = path.stem
    m = re.search(r"(\d+)", s)  # grabs first number
    if m:
        return int(m.group(1))
    raise ValueError(f"Could not extract node count from filename: {path.name}")

def summarize_one(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    # ensure numeric
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    means = df[NUM_COLS].mean()

    nodes = extract_nodes(csv_path)
    
    out = {
        "Nodes": nodes,
        "Total Travel Time": float(f"{means['Total Travel Time']:.2f}"),
        "Total Energy Consumed": float(f"{means['Total Energy Consumed']:.3f}"),
        "Total Distance Covered": float(f"{means['Total Distance Covered']:.2f}"),
        "Run Time": float(f"{means['Run Time']:.3f}"),
        "Total Module Swapped": int(round(means["Total Module Swapped"])),
    }
    return out

def main():
    rows = []
    for csv_path in sorted(INPUT_DIR.glob("*_summary.csv")):
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
        "Nodes",
        "Total Travel Time",
        "Total Energy Consumed",
        "Total Distance Covered",
        "Run Time",
        "Total Module Swapped",
    ])
    # Sort by Nodes
    data = data.sort_values("Nodes")
    data.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(data)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()

