# aggregate_means.py
import re
from pathlib import Path

import pandas as pd

INPUT_DIR = Path(".")   # run from this folder
OUTPUT = Path("data.csv")

NUM_COLS = [
    "Total Travel Time",
    "Total Energy Consumed",
    "Total Distance Covered",
    "Run Time",
    "Total Module Swapped",
]


def extract_threshold(path: Path) -> int:
    """
    Extract threshold value from filename.
    Examples:
      5t_summary.csv            -> 5
      10t_summary.csv           -> 10
      15t_summary.csv           -> 15
      20threshold_summary.csv   -> 20
    """
    s = path.stem

    m = re.search(r"(\d+)\s*(?:t|threshold)\b", s, re.IGNORECASE)
    if m:
        return int(m.group(1))

    # Fallback: leading number (e.g., "20_...").
    m = re.match(r"^(\d+)", s)
    if m:
        return int(m.group(1))

    raise ValueError(f"Could not extract threshold from filename: {path.name}")


def summarize_one(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    means = df[NUM_COLS].mean()

    threshold = extract_threshold(csv_path)

    return {
        "Threshold": threshold,
        "Total Travel Time": float(f"{means['Total Travel Time']:.2f}"),
        "Total Energy Consumed": float(f"{means['Total Energy Consumed']:.3f}"),
        "Total Distance Covered": float(f"{means['Total Distance Covered']:.2f}"),
        "Run Time": float(f"{means['Run Time']:.3f}"),
        "Total Module Swapped": int(round(means["Total Module Swapped"])),
    }


def main() -> None:
    # Only ingest per-run CSVs whose filenames start with the threshold
    # (e.g., 5t_summary.csv, 10t_summary.csv, 20t_summary.csv).
    # If multiple files map to the same threshold (e.g. 20threshold_summary.csv and 20t_summary.csv),
    # prefer the "*t_summary.csv" variant.
    by_threshold: dict[int, dict] = {}
    best_rank: dict[int, int] = {}

    def rank_filename(name: str) -> int:
        n = name.lower()
        # Higher rank = preferred
        if re.search(r"\bt_summary\b", n):
            return 2
        if "threshold" in n:
            return 0
        return 1

    for csv_path in sorted(INPUT_DIR.glob("*.csv")):
        if csv_path.name.lower() == OUTPUT.name.lower():
            continue
        if not re.match(r"^\d", csv_path.name):
            continue

        try:
            row = summarize_one(csv_path)
        except Exception as e:
            print(f"Skip {csv_path.name}: {e}")
            continue

        k = row["Threshold"]
        r = rank_filename(csv_path.name)
        if (k not in best_rank) or (r > best_rank[k]):
            by_threshold[k] = row
            best_rank[k] = r

    rows = list(by_threshold.values())

    if not rows:
        print("No input CSVs found.")
        return

    data = pd.DataFrame(
        rows,
        columns=[
            "Threshold",
            "Total Travel Time",
            "Total Energy Consumed",
            "Total Distance Covered",
            "Run Time",
            "Total Module Swapped",
        ],
    ).sort_values("Threshold")

    data.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(data)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()


