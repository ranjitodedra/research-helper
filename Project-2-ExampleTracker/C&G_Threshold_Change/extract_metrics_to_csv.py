"""
Extract metrics from GA and CPLEX output txt files into CSV files.
Processes subfolders named by threshold (e.g. 5, 10, 15, 20)
and writes runtime, travelTime, distance, energy_consumption,
energy_charge_CS, energy_charge_ERS.
"""

import argparse
import csv
import logging
import re
from pathlib import Path

# Regex patterns for GA output format
RE_GA_TRAVEL_TIME = re.compile(
    r"Total Travel Time:\s+[\d.]+\s+hours\s+\(([\d.]+)\s+min\)"
)
RE_GA_DISTANCE = re.compile(r"Total Distance:\s+([\d.]+)\s+km")
RE_GA_ENERGY_DEPLETION = re.compile(r"Total Energy Depletion:\s+([\d.]+)\s+kWh")
RE_GA_ENERGY_CHARGE_SC = re.compile(r"Total Energy Charged \(SC\):\s+([\d.]+)\s+kWh")
RE_GA_ENERGY_CHARGE_DWC = re.compile(r"Total Energy Charged \(DWC\):\s+([\d.]+)\s+kWh")
RE_GA_RUNTIME = re.compile(r"Runtime:\s+([\d.]+)\s+seconds")

# Regex patterns for CPLEX output format
RE_CPLEX_TRAVEL_TIME = re.compile(r"Travel time:\s+([\d.]+)")
RE_CPLEX_DISTANCE = re.compile(r"Total distance taken:\s+([\d.]+)")
RE_CPLEX_ENERGY_DEPLETION = re.compile(r"Total energy depletion:\s+([\d.]+)")
RE_CPLEX_ENERGY_CHARGE_CS = re.compile(
    r"Total energy charged at charging stations:\s+([\d.]+)"
)
RE_CPLEX_ENERGY_CHARGE_ERS = re.compile(r"Total energy charged at Eroad:\s+([\d.]+)")

OUTPUT_FILES = (
    "GA_output.txt",
    "CPLEX_output.txt",
)
CSV_NAMES = (
    "runtime.csv",
    "travelTime.csv",
    "distance.csv",
    "energy_consumption.csv",
    "energy_charge_CS.csv",
    "energy_charge_ERS.csv",
)
# For each CSV, key in parsed dict (and column name for value)
CSV_METRIC_KEYS = (
    "runtime_sec",
    "travel_time_min",
    "distance_km",
    "energy_depletion",
    "energy_charge_CS",
    "energy_charge_DWC",
)


def parse_ga_output(filepath: Path) -> dict | None:
    """
    Parse a GA output txt file and return extracted metrics.
    Returns dict with keys: travel_time_min, distance_km, energy_depletion,
    energy_charge_CS, energy_charge_DWC, runtime_sec.
    Returns None if file missing, empty, or unparseable.
    """
    if not filepath.exists():
        return None
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        logging.warning("Could not read %s", filepath)
        return None
    if not text.strip():
        logging.warning("Empty file: %s", filepath)
        return None

    def search(pattern: re.Pattern) -> str:
        m = pattern.search(text)
        return m.group(1).strip() if m else ""

    return {
        "travel_time_min": search(RE_GA_TRAVEL_TIME),
        "distance_km": search(RE_GA_DISTANCE),
        "energy_depletion": search(RE_GA_ENERGY_DEPLETION),
        "energy_charge_CS": search(RE_GA_ENERGY_CHARGE_SC),
        "energy_charge_DWC": search(RE_GA_ENERGY_CHARGE_DWC),
        "runtime_sec": search(RE_GA_RUNTIME),
    }


def parse_cplex_output(filepath: Path) -> dict | None:
    """
    Parse a CPLEX output txt file and return extracted metrics.
    CPLEX uses "Travel time" in minutes, no runtime in file.
    energy_charge_DWC maps to "Total energy charged at Eroad".
    """
    if not filepath.exists():
        return None
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        logging.warning("Could not read %s", filepath)
        return None
    if not text.strip():
        logging.warning("Empty file: %s", filepath)
        return None

    def search(pattern: re.Pattern) -> str:
        m = pattern.search(text)
        return m.group(1).strip() if m else ""

    return {
        "travel_time_min": search(RE_CPLEX_TRAVEL_TIME),
        "distance_km": search(RE_CPLEX_DISTANCE),
        "energy_depletion": search(RE_CPLEX_ENERGY_DEPLETION),
        "energy_charge_CS": search(RE_CPLEX_ENERGY_CHARGE_CS),
        "energy_charge_DWC": search(RE_CPLEX_ENERGY_CHARGE_ERS),
        "runtime_sec": "",  # CPLEX output does not include runtime
    }


def discover_threshold_folders(base_dir: Path) -> list[tuple[str, Path]]:
    """
    Find subdirs named by a single number (e.g. 5, 10, 15, 20) and return
    (threshold_label, path) sorted numerically. If none match, fall back to
    any directory that contains GA_output.txt, using dir name as label.
    """
    pairs: list[tuple[str, Path]] = []
    for p in base_dir.iterdir():
        if not p.is_dir():
            continue
        if p.name.isdigit():
            pairs.append((p.name, p))

    if pairs:
        pairs.sort(key=lambda item: int(item[0]))
        return pairs

    # Fallback: any directory that contains GA_output.txt
    for p in base_dir.iterdir():
        if not p.is_dir():
            continue
        if (p / "GA_output.txt").exists():
            pairs.append((p.name, p))
    pairs.sort(key=lambda x: (int(x[0]) if x[0].isdigit() else 0, x[0]))
    return pairs


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Extract metrics from GA/CPLEX output txt files to CSV (threshold folders)."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Root directory containing threshold subfolders (default: script dir)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to write CSV files (default: same as input-dir)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    input_dir = args.input_dir or script_dir
    output_dir = args.output_dir or input_dir

    if not input_dir.is_dir():
        logging.error("Input directory does not exist: %s", input_dir)
        return

    pairs = discover_threshold_folders(input_dir)
    if not pairs:
        logging.warning(
            "No threshold subfolders (numeric or with GA_output.txt) found in %s",
            input_dir,
        )
        return

    # Collect one row per threshold: threshold -> { GA: parsed, CPLEX: parsed }
    rows_by_metric: list[list[dict]] = [[] for _ in CSV_METRIC_KEYS]

    for threshold_label, folder in pairs:
        row_ga = parse_ga_output(folder / "GA_output.txt")
        row_cplex = parse_cplex_output(folder / "CPLEX_output.txt")

        for i, key in enumerate(CSV_METRIC_KEYS):
            r = {"threshold": threshold_label}
            r["GA"] = (row_ga or {}).get(key, "")
            r["CPLEX"] = (row_cplex or {}).get(key, "")
            rows_by_metric[i].append(r)

    # Write CSVs
    fieldnames = ["threshold", "GA", "CPLEX"]
    for csv_name, rows in zip(CSV_NAMES, rows_by_metric):
        out_path = output_dir / csv_name
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        logging.info("Wrote %s", out_path)


if __name__ == "__main__":
    main()
