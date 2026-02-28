import re
import csv
from pathlib import Path


# Extract identifier from filenames like "200c_100bss_500total_High.txt", "200c_100bss_500total_Mid.txt", etc.
FILE_PATTERN = re.compile(r"^[\w_]+total_([\w_]+)\.txt$", re.IGNORECASE)


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

        file_id = match.group(1)  # Extract traffic level (High, Mid, Low, etc.)

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
    """Write a single combined CSV with all metrics."""
    # Extract unique file IDs for ordering
    file_ids = {key for metric in results.values() for key in metric}
    
    # Sort file IDs: prioritize High, Mid, Low order
    def sort_key(fid):
        fid_str = str(fid).lower()
        order = {"high": 1, "mid": 2, "low": 3}
        return order.get(fid_str, 99)
    
    file_ids = sorted(file_ids, key=sort_key)

    # Write single combined CSV
    path = output_dir / "results.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Modules", "Total Travel Time", "Total Energy Consumed", "Total Distance Covered", "Run Time", "Total Module Swapped"])
        for file_id in file_ids:
            travel_time = results["travelTime"].get(file_id, "")
            energy = results["energy"].get(file_id, "")
            distance = results["distance"].get(file_id, "")
            runtime = results["runtime"].get(file_id, "")
            modules_swapped = results["modulesSwapped"].get(file_id, "")
            writer.writerow([file_id, travel_time, energy, distance, runtime, modules_swapped])
    print(f"Wrote results.csv")


if __name__ == "__main__":
    # Process files in the current directory (Traffic folder)
    base_dir = Path(__file__).parent
    print(f"Extracting metrics from files in {base_dir}...")
    metrics = process_all(base_dir)
    print("\nCreating CSV files...")
    write_csvs(metrics, base_dir)
    print("\nDone!")

