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
    "Number of Modules Swapped",
    "Runtime",
]

def infer_label(path: Path) -> str:
    """
    Tries to infer 'nodes N' from filename.
    Examples:
      summary_nodes1000.csv   -> nodes 1000
      nodes_1500_summary.csv  -> nodes 1500
      summary_1000.csv        -> nodes 1000
    Fallback: use stem as-is.
    """
    s = path.stem
    m = re.search(r"(?:nodes[_-]?)?(\d{3,5})", s)  # grabs 1000, 1500, etc.
    return f"nodes {m.group(1)}" if m else s

def summarize_one(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    # ensure numeric
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    means = df[NUM_COLS].mean()

    out = {
        "Examples": infer_label(csv_path),
        "Total Travel Time": float(f"{means['Total Travel Time']:.2f}"),
        "Total Energy Consumed": float(f"{means['Total Energy Consumed']:.3f}"),
        "Total Distance Covered": float(f"{means['Total Distance Covered']:.2f}"),
        # keep as int (rounded)
        "Number of Modules Swapped": int(round(means["Number of Modules Swapped"])),
        "Runtime": float(f"{means['Runtime']:.3f}"),
    }
    return out

def main():
    rows = []
    for csv_path in sorted(INPUT_DIR.glob("*.csv")):
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
        "Examples",
        "Total Travel Time",
        "Total Energy Consumed",
        "Total Distance Covered",
        "Number of Modules Swapped",
        "Runtime",
    ])
    data.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(data)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()
