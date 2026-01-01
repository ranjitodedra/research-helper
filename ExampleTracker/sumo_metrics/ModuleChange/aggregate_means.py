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


def extract_module_count(path: Path) -> int:
    """
    Extract module count from filename.
    Examples:
      3module_summary.csv   -> 3
      5module_summary.csv   -> 5
      4_summary.csv         -> 4
      6_summary.csv         -> 6
    """
    s = path.stem

    m = re.search(r"(\d+)\s*(?:module)?\b", s, re.IGNORECASE)
    if m:
        return int(m.group(1))

    m = re.match(r"^(\d+)", s)
    if m:
        return int(m.group(1))

    raise ValueError(f"Could not extract module count from filename: {path.name}")


def summarize_one(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    means = df[NUM_COLS].mean()

    module_count = extract_module_count(csv_path)

    return {
        "Module Count": module_count,
        "Total Travel Time": float(f"{means['Total Travel Time']:.2f}"),
        "Total Energy Consumed": float(f"{means['Total Energy Consumed']:.3f}"),
        "Total Distance Covered": float(f"{means['Total Distance Covered']:.2f}"),
        "Run Time": float(f"{means['Run Time']:.3f}"),
        "Total Module Swapped": int(round(means["Total Module Swapped"])),
    }


def main() -> None:
    # Only ingest per-run CSVs whose filenames start with the module count
    # (e.g., 3module_summary.csv, 4_summary.csv, 5module.csv, 6_summary.csv).
    # This intentionally excludes already-aggregated files like ModuleChange_summary.csv.
    by_module: dict[int, dict] = {}

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

        k = row["Module Count"]
        # Prefer *_summary.csv over e.g. *module.csv if both exist for the same k.
        existing = by_module.get(k)
        if existing is None:
            by_module[k] = row
        else:
            new_is_summary = "summary" in csv_path.name.lower()
            # We don't know the previous filename; use heuristic: if we're currently on
            # a summary file, overwrite the existing entry.
            if new_is_summary:
                by_module[k] = row

    rows = list(by_module.values())
    if not rows:
        print("No input CSVs found.")
        return

    data = pd.DataFrame(
        rows,
        columns=[
            "Module Count",
            "Total Travel Time",
            "Total Energy Consumed",
            "Total Distance Covered",
            "Run Time",
            "Total Module Swapped",
        ],
    ).sort_values("Module Count")

    data.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(data)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()


