import re
import csv
from pathlib import Path


# Folders are named like "1_min", "2_min", etc.
FOLDER_PATTERN = re.compile(r"(\d+)_min", re.IGNORECASE)


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


def parse_folder_info(folder_name: str):
    """Return swap time in minutes parsed from folder name."""
    match = FOLDER_PATTERN.search(folder_name)
    if not match:
        return None
    return int(match.group(1))


def process_all_folders(base_dir: Path):
    """Process all swap time folders and collect metrics."""
    results = []

    for folder in sorted(base_dir.iterdir()):
        if not folder.is_dir():
            continue

        swap_time = parse_folder_info(folder.name)
        if swap_time is None:
            print(f"Skipping {folder.name}: name does not match expected pattern")
            continue

        # Find the text file in the folder (could be X_min.txt or Xmin_swap.txt)
        txt_files = list(folder.glob("*.txt"))
        if not txt_files:
            print(f"Warning: No .txt file found in {folder.name}")
            continue

        file_path = txt_files[0]
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - defensive log
            print(f"Error reading {file_path}: {exc}")
            continue

        metrics = {
            "swapTime": swap_time,
            "travelTime": extract_travel_time(content),
            "energy": extract_energy(content),
            "distance": extract_distance(content),
            "modulesSwapped": extract_modules_swapped(content),
            "runtime": extract_runtime(content),
        }

        results.append(metrics)
        print(f"Processed {folder.name}/{file_path.name}")

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

    ordered = sorted(results, key=lambda item: item["swapTime"])

    for metric_key, filename in metrics:
        csv_path = output_dir / filename
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["swapTime", metric_key])
            for entry in ordered:
                writer.writerow([entry["swapTime"], entry.get(metric_key, "")])
        print(f"Wrote {filename}")


if __name__ == "__main__":
    base_path = Path(__file__).parent
    print("Extracting metrics for SwapTimeChange...")
    collected = process_all_folders(base_path)
    print("\nCreating CSV files...")
    write_csv(collected, base_path)
    print("\nDone!")

