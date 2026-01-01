import re
import csv
from pathlib import Path


# Traffic level order for sorting
TRAFFIC_ORDER = {"Low": 1, "Mid": 2, "High": 3}

# Map file suffixes to algorithm labels
FILE_TO_ALGO = {
    "CPLEX_output.txt": "CPLEX",
    "H_output.txt": "H",
}


def parse_traffic_level(folder_name: str):
    """Return traffic level from folder name (Low, Mid, or High)."""
    # Capitalize first letter to handle case variations
    folder_name_cap = folder_name.capitalize()
    if folder_name_cap in TRAFFIC_ORDER:
        return folder_name_cap
    return None


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
    """Heuristic logs sometimes include runtime lines."""
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
    match = re.search(r"Runtime:\s*([\d.]+)\s*seconds?", content, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def process_all(base_dir: Path):
    """Process each scenario folder and collect metrics."""
    results = {
        "travelTime": {},
        "energy": {},
        "distance": {},
        "modulesSwapped": {},
        "runtime": {},
    }

    # Look for subdirectories (like "16") that contain traffic level folders
    for node_folder in sorted(base_dir.iterdir()):
        if not node_folder.is_dir():
            continue

        # Look for traffic level folders (Low, Mid, High) inside the node folder
        for traffic_folder in sorted(node_folder.iterdir()):
            if not traffic_folder.is_dir():
                continue

            traffic_level = parse_traffic_level(traffic_folder.name)
            if traffic_level is None:
                print(f"Skipping {traffic_folder.name}: not a recognized traffic level (Low/Mid/High)")
                continue

            for file_suffix, algo in FILE_TO_ALGO.items():
                matching = list(traffic_folder.glob(f"*{file_suffix}"))
                if not matching:
                    print(f"Warning: No file matching *{file_suffix} in {traffic_folder.name}")
                    continue

                file_path = matching[0]
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

                key = (traffic_level, algo)
                if travel_time is not None:
                    results["travelTime"][key] = travel_time
                if energy is not None:
                    results["energy"][key] = energy
                if distance is not None:
                    results["distance"][key] = distance
                if modules is not None:
                    results["modulesSwapped"][key] = modules
                if runtime is not None:
                    results["runtime"][key] = runtime

                print(f"Processed {node_folder.name}/{traffic_folder.name}/{file_path.name}")

    return results


def write_csvs(results: dict, output_dir: Path):
    """Write per-metric CSVs with CPLEX and H columns."""
    algo_order = ["CPLEX", "H"]

    # Extract unique traffic levels and sort them by order
    traffic_levels_set = {key[0] for metric in results.values() for key in metric}
    traffic_levels = sorted(traffic_levels_set, key=lambda x: TRAFFIC_ORDER.get(x, 999))

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
            writer.writerow(["trafficLevel"] + algo_order)
            for traffic_level in traffic_levels:
                row = [traffic_level]
                for algo in algo_order:
                    row.append(results[metric_name].get((traffic_level, algo), ""))
                writer.writerow(row)
        print(f"Wrote {filename}")


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    print("Extracting metrics for CPLEX and Heuristic scenarios...")
    metrics = process_all(base_dir)
    print("\nCreating CSV files...")
    write_csvs(metrics, base_dir)
    print("\nDone!")

