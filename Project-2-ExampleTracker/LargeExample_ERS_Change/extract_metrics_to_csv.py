"""
Extract metrics from GA/AC/CW output txt files into CSV files.
Processes subfolders named like X_Y (ERS config, e.g. 0_15, 0_20, 0_25, 0_30)
and writes runtime, travelTime, distance, energy_consumption,
energy_charge_CS, energy_charge_ERS.
"""

import argparse
import csv
import logging
import re
from pathlib import Path

# Regex patterns for GA/AC/CW output format
RE_TRAVEL_TIME = re.compile(
    r"Total Travel Time:\s+[\d.]+\s+hours\s+\(([\d.]+)\s+min\)"
)
RE_DISTANCE = re.compile(r"Total Distance:\s+([\d.]+)\s+km")
RE_ENERGY_DEPLETION = re.compile(r"Total Energy Depletion:\s+([\d.]+)\s+kWh")
RE_ENERGY_CHARGE_SC = re.compile(r"Total Energy Charged \(SC\):\s+([\d.]+)\s+kWh")
RE_ENERGY_CHARGE_DWC = re.compile(r"Total Energy Charged \(DWC\):\s+([\d.]+)\s+kWh")
RE_RUNTIME_GA = re.compile(r"Runtime:\s+([\d.]+)\s+seconds")
RE_RUNTIME_AC_CW = re.compile(r"Total Runtime:\s+([\d.]+)\s+seconds")
RE_ERS_CONFIG = re.compile(r"^(\d+)_(\d+)$")

OUTPUT_FILES = (
    "GA_output.txt",
    "AC_output.txt",
    "CW_output.txt",
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


def parse_output_file(filepath: Path, is_ga: bool) -> dict | None:
    """
    Parse a GA/AC/CW output txt file and return extracted metrics.
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

    travel_time = search(RE_TRAVEL_TIME)
    distance = search(RE_DISTANCE)
    energy_depletion = search(RE_ENERGY_DEPLETION)
    energy_charge_sc = search(RE_ENERGY_CHARGE_SC)
    energy_charge_dwc = search(RE_ENERGY_CHARGE_DWC)
    runtime = search(RE_RUNTIME_GA) if is_ga else search(RE_RUNTIME_AC_CW)

    return {
        "travel_time_min": travel_time,
        "distance_km": distance,
        "energy_depletion": energy_depletion,
        "energy_charge_CS": energy_charge_sc,
        "energy_charge_DWC": energy_charge_dwc,
        "runtime_sec": runtime,
    }


def discover_ers_config_folders(base_dir: Path) -> list[tuple[str, Path]]:
    """
    Find subdirs named like X_Y (e.g. 0_15, 0_20) and return (config_label, path)
    sorted by (int(part1), int(part2)). If none match, fall back to any directory
    that contains GA_output.txt, using dir name as label and sorting alphabetically.
    """
    pairs: list[tuple[str, Path]] = []
    for p in base_dir.iterdir():
        if not p.is_dir():
            continue
        m = RE_ERS_CONFIG.match(p.name)
        if m:
            pairs.append((p.name, p))

    if pairs:
        # Sort by numeric parts: (0, 15), (0, 20), (0, 25), (0, 30)
        def sort_key(item: tuple[str, Path]) -> tuple[int, int]:
            m = RE_ERS_CONFIG.match(item[0])
            return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
        pairs.sort(key=sort_key)
        return pairs

    # Fallback: any directory that contains GA_output.txt
    for p in base_dir.iterdir():
        if not p.is_dir():
            continue
        if (p / "GA_output.txt").exists():
            pairs.append((p.name, p))
    pairs.sort(key=lambda x: x[0])
    return pairs


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Extract metrics from GA/AC/CW output txt files to CSV (ERS config folders)."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Root directory containing X_Y ERS config subfolders (default: script dir)",
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

    pairs = discover_ers_config_folders(input_dir)
    if not pairs:
        logging.warning("No ERS config subfolders (X_Y or with GA_output.txt) found in %s", input_dir)
        return

    # Collect one row per config: ers_config -> { GA: parsed, AC: parsed, CW: parsed }
    rows_by_metric: list[list[dict]] = [
        [] for _ in CSV_METRIC_KEYS
    ]

    for config_label, folder in pairs:
        row_ga = parse_output_file(folder / "GA_output.txt", is_ga=True)
        row_ac = parse_output_file(folder / "AC_output.txt", is_ga=False)
        row_cw = parse_output_file(folder / "CW_output.txt", is_ga=False)

        for i, key in enumerate(CSV_METRIC_KEYS):
            r = {"ers_config": config_label}
            r["GA"] = (row_ga or {}).get(key, "")
            r["AC"] = (row_ac or {}).get(key, "")
            r["CW"] = (row_cw or {}).get(key, "")
            rows_by_metric[i].append(r)

    # Write CSVs
    fieldnames = ["ers_config", "GA", "AC", "CW"]
    for csv_name, rows in zip(CSV_NAMES, rows_by_metric):
        out_path = output_dir / csv_name
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        logging.info("Wrote %s", out_path)


if __name__ == "__main__":
    main()
