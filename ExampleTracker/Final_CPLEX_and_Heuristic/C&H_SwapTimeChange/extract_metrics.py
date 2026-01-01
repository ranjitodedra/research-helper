import re
import csv
from pathlib import Path


# Extract swap time from folder names like "6c_3bss_16total_C&H_SwapTimeChange_4_min"
FOLDER_PATTERN = re.compile(r"_(\d+)_min", re.IGNORECASE)

# Map file suffixes to algorithm labels
FILE_TO_ALGO = {
    "CPLEX_output.txt": "CPLEX",
    "H_output.txt": "H",
}


def parse_folder_info(folder_name: str):
    """Return swap time (in minutes) from folder name."""
    match = FOLDER_PATTERN.search(folder_name)
    if not match:
        return None
    swap_time = match.group(1)
    return int(swap_time)


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

    for folder in sorted(base_dir.iterdir()):
        if not folder.is_dir():
            continue

        swap_time = parse_folder_info(folder.name)
        if swap_time is None:
            print(f"Skipping {folder.name}: name does not match expected pattern")
            continue

        for file_suffix, algo in FILE_TO_ALGO.items():
            matching = list(folder.glob(f"*{file_suffix}"))
            if not matching:
                print(f"Warning: No file matching *{file_suffix} in {folder.name}")
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

            key = (swap_time, algo)
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

            print(f"Processed {folder.name}/{file_path.name}")

    return results


def write_csvs(results: dict, output_dir: Path):
    """Write per-metric CSVs with CPLEX and H columns."""
    algo_order = ["CPLEX", "H"]

    # Extract unique swap times for ordering
    swap_times = sorted({key[0] for metric in results.values() for key in metric})

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
            writer.writerow(["swapTime"] + algo_order)
            for swap_time in swap_times:
                row = [swap_time]
                for algo in algo_order:
                    row.append(results[metric_name].get((swap_time, algo), ""))
                writer.writerow(row)
        print(f"Wrote {filename}")


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    print("Extracting metrics for CPLEX and Heuristic scenarios...")
    metrics = process_all(base_dir)
    print("\nCreating CSV files...")
    write_csvs(metrics, base_dir)
    print("\nDone!")

