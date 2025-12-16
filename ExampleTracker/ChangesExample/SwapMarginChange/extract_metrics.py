import re
import csv
from pathlib import Path


# Files are named like "0_10.txt" where 0_10 means 0.10 swap margin
FILE_PATTERN = re.compile(r"0_(\d+)\.txt", re.IGNORECASE)


def extract_travel_time(content: str):
    """Extract total travel time in minutes."""
    if re.search(r"Total Travel Time:\s*inf", content, re.IGNORECASE):
        return "inf"
    match = re.search(r"Total Travel Time:\s*([\d.]+)\s*minutes?", content, re.IGNORECASE)
    return float(match.group(1)) if match else None


def extract_energy(content: str):
    """Extract total energy consumed in kWh."""
    if re.search(r"Total Energy Consumed:\s*inf", content, re.IGNORECASE):
        return "inf"
    match = re.search(r"Total Energy Consumed:\s*([\d.]+)\s*kWh", content, re.IGNORECASE)
    return float(match.group(1)) if match else None


def extract_distance(content: str):
    """Extract total distance covered in km."""
    match = re.search(r"Total Distance Covered:\s*([\d.]+)\s*km", content, re.IGNORECASE)
    return float(match.group(1)) if match else None


def extract_modules_swapped(content: str):
    """Extract number of modules swapped."""
    match = re.search(r"Number of Modules Swapped:\s*(\d+)", content, re.IGNORECASE)
    return int(match.group(1)) if match else None


def extract_runtime(content: str):
    """Extract runtime in seconds."""
    match = re.search(r"Runtime:\s*([\d.]+)\s*seconds", content, re.IGNORECASE)
    return float(match.group(1)) if match else None


def parse_file_info(path: Path):
    """Return swap margin value parsed from filename (e.g., 0_10 -> 0.10)."""
    match = FILE_PATTERN.search(path.name)
    if not match:
        return None
    decimal_part = match.group(1)
    # Convert "10" to 0.10, "07" to 0.07, etc.
    return float(f"0.{decimal_part}")


def process_all_files(base_dir: Path):
    """Process all swap margin output files and collect metrics."""
    results = []

    for file_path in sorted(base_dir.glob("0_*.txt")):
        swap_margin = parse_file_info(file_path)
        if swap_margin is None:
            print(f"Skipping {file_path.name}: name does not match expected pattern")
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - defensive log
            print(f"Error reading {file_path}: {exc}")
            continue

        metrics = {
            "swapMargin": swap_margin,
            "travelTime": extract_travel_time(content),
            "energy": extract_energy(content),
            "distance": extract_distance(content),
            "modulesSwapped": extract_modules_swapped(content),
            "runtime": extract_runtime(content),
        }

        results.append(metrics)
        print(f"Processed {file_path.name}")

    return results


def write_csv(results, output_dir: Path):
    """Create CSV files for each metric."""
    metrics = [
        ("travelTime", "travelTime.csv"),
        ("energy", "energy.csv"),
        ("distance", "distance.csv"),
        ("modulesSwapped", "modulesSwapped.csv"),
        ("runtime", "runtime.csv"),
    ]

    ordered = sorted(results, key=lambda item: item["swapMargin"])

    for metric_key, filename in metrics:
        csv_path = output_dir / filename
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["swapMargin", metric_key])
            for entry in ordered:
                writer.writerow([entry["swapMargin"], entry.get(metric_key, "")])
        print(f"Wrote {filename}")


if __name__ == "__main__":
    base_path = Path(__file__).parent
    print("Extracting metrics for SwapMarginChange...")
    collected = process_all_files(base_path)
    print("\nCreating CSV files...")
    write_csv(collected, base_path)
    print("\nDone!")

