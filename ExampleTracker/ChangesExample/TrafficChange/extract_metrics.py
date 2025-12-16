import re
import csv
from pathlib import Path


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


def process_all_folders(base_dir: Path):
    """Process all location/traffic folders and collect metrics."""
    results = []

    for folder in sorted(base_dir.iterdir()):
        if not folder.is_dir():
            continue

        # Try to parse the folder name as a number (location/traffic value)
        try:
            location_traffic = int(folder.name)
        except ValueError:
            print(f"Skipping {folder.name}: not a valid number")
            continue

        # Find the text file in the folder (should be named {location_traffic}.txt)
        file_path = folder / f"{location_traffic}.txt"
        if not file_path.exists():
            # Try to find any .txt file in the folder
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
            "locationTraffic": location_traffic,
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

    ordered = sorted(results, key=lambda item: item["locationTraffic"])

    for metric_key, filename in metrics:
        csv_path = output_dir / filename
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["locationTraffic", metric_key])
            for entry in ordered:
                writer.writerow([entry["locationTraffic"], entry.get(metric_key, "")])
        print(f"Wrote {filename}")


if __name__ == "__main__":
    base_path = Path(__file__).parent
    print("Extracting metrics for Locations&TrafficChange...")
    collected = process_all_folders(base_path)
    print("\nCreating CSV files...")
    write_csv(collected, base_path)
    print("\nDone!")

