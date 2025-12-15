import re
import csv
from pathlib import Path


# Extract identifier from filenames like "42.txt", "101.txt", "0_1.txt", "0_07.txt", "1min.txt", "2min.txt", "5p.txt", "10p.txt"
FILE_PATTERN = re.compile(r"^([\d_]+[a-z]*|[\d_]+min)\.txt$", re.IGNORECASE)


def extract_travel_time(content: str):
    # CPLEX uses "Travel time:", heuristic uses "Total Travel Time:"
    if re.search(r"Travel Time:\s*inf", content, re.IGNORECASE):
        return "inf"
    match = re.search(r"Travel time:\s*([\d.]+)", content, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r"Total Travel Time:\s*([\d.]+)\s*minutes?", content, re.IGNORECASE)
    return float(match.group(1)) if match else None


def extract_energy(content: str):
    # CPLEX uses "Total energy depletion:", heuristic uses "Total Energy Consumed:"
    if re.search(r"Total Energy (Consumed|depletion):\s*inf", content, re.IGNORECASE):
        return "inf"
    match = re.search(r"Total energy depletion:\s*([\d.]+)", content, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r"Total Energy Consumed:\s*([\d.]+)\s*kWh", content, re.IGNORECASE)
    return float(match.group(1)) if match else None


def extract_distance(content: str):
    # CPLEX uses "Total distance:", heuristic uses "Total Distance Covered:"
    match = re.search(r"Total distance:\s*([\d.]+)\s*km", content, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r"Total Distance Covered:\s*([\d.]+)\s*km", content, re.IGNORECASE)
    return float(match.group(1)) if match else None


def extract_modules_swapped(content: str):
    match = re.search(r"Number of Modules Swapped:\s*(\d+)", content, re.IGNORECASE)
    return int(match.group(1)) if match else None


def extract_runtime(content: str):
    """Extract runtime from SUMO scenario logs."""
    match = re.search(r"Program Runtime:\s*(\d+)m\s*([\d.]+)s", content, re.IGNORECASE)
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes * 60 + seconds
    match = re.search(r"Program Runtime:\s*([\d.]+)\s*seconds?", content, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r"JSON Scenario runtime:\s*([\d.]+)\s*seconds?", content, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r"SUMO Scenario runtime:\s*([\d.]+)\s*seconds?", content, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r"Runtime:\s*([\d.]+)\s*seconds?", content, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def process_all(base_dir: Path):
    """Process each .txt file and collect metrics."""
    results = {
        "travelTime": {},
        "energy": {},
        "distance": {},
        "modulesSwapped": {},
        "runtime": {},
    }

    for file_path in sorted(base_dir.glob("*.txt")):
        # Extract identifier from filename
        match = FILE_PATTERN.match(file_path.name)
        if not match:
            print(f"Skipping {file_path.name}: filename does not match expected pattern")
            continue

        file_id = match.group(1)  # Keep as string to preserve format like "0_1", "0_07"

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - defensive log
            print(f"Error reading {file_path}: {exc}")
            continue

        travel_time = extract_travel_time(content)
        energy = extract_energy(content)
        distance = extract_distance(content)
        modules = extract_modules_swapped(content)
        runtime = extract_runtime(content)

        if travel_time is not None:
            results["travelTime"][file_id] = travel_time
        if energy is not None:
            results["energy"][file_id] = energy
        if distance is not None:
            results["distance"][file_id] = distance
        if modules is not None:
            results["modulesSwapped"][file_id] = modules
        if runtime is not None:
            results["runtime"][file_id] = runtime

        print(f"Processed {file_path.name}")

    return results


def write_csvs(results: dict, output_dir: Path):
    """Write per-metric CSVs with file ID as the key."""
    # Extract unique file IDs for ordering
    # Try to sort numerically if possible, otherwise alphabetically
    file_ids = {key for metric in results.values() for key in metric}
    
    # Sort file IDs: try numeric first, then string
    def sort_key(fid):
        try:
            fid_str = str(fid)
            # Handle "1min", "2min" format - extract number before "min"
            if fid_str.endswith('min'):
                return float(fid_str[:-3])
            # Handle "5p", "10p" format - extract number before "p"
            if fid_str.endswith('p'):
                return float(fid_str[:-1])
            # Handle "0_1" format - convert to float
            if '_' in fid_str:
                return float(fid_str.replace('_', '.'))
            return float(fid_str)
        except (ValueError, TypeError):
            return str(fid)
    
    file_ids = sorted(file_ids, key=sort_key)

    csv_files = {
        "travelTime": "travelTime.csv",
        "energy": "energy.csv",
        "distance": "distance.csv",
        "modulesSwapped": "modulesSwapped.csv",
        "runtime": "runtime.csv",
    }

    for metric_name, filename in csv_files.items():
        path = output_dir / filename
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["file_id", "value"])
            for file_id in file_ids:
                value = results[metric_name].get(file_id, "")
                writer.writerow([file_id, value])
        print(f"Wrote {filename}")


if __name__ == "__main__":
    # Process files in the ThresholdChange folder
    base_dir = Path(__file__).parent / "sumo_examples" / "ThresholdChange"
    print(f"Extracting metrics from files in {base_dir}...")
    metrics = process_all(base_dir)
    print("\nCreating CSV files...")
    write_csvs(metrics, base_dir)
    print("\nDone!")

