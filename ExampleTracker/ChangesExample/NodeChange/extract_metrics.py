import re
import csv
from pathlib import Path


FOLDER_PATTERN = re.compile(
    r"erdos_renyi_(\d+)nodes_(\d+)customers_seed_(\d+)", re.IGNORECASE
)


def extract_travel_time(content: str):
    """Extract total travel time in minutes."""
    if re.search(r"Total Travel Time:\s*inf", content, re.IGNORECASE):
        return "inf"
    match = re.search(r"Total Travel Time:\s*([\d.]+)\s*minutes?", content)
    return float(match.group(1)) if match else None


def extract_energy(content: str):
    """Extract total energy consumed in kWh."""
    if re.search(r"Total Energy Consumed:\s*inf", content, re.IGNORECASE):
        return "inf"
    match = re.search(r"Total Energy Consumed:\s*([\d.]+)\s*kWh", content)
    return float(match.group(1)) if match else None


def extract_distance(content: str):
    """Extract total distance covered in km."""
    match = re.search(r"Total Distance Covered:\s*([\d.]+)\s*km", content)
    return float(match.group(1)) if match else None


def extract_modules_swapped(content: str):
    """Extract number of modules swapped."""
    match = re.search(r"Number of Modules Swapped:\s*(\d+)", content)
    return int(match.group(1)) if match else None


def extract_runtime(content: str):
    """Extract runtime in seconds from generator output logs."""
    matches = re.findall(r"Runtime:\s*([\d.]+)\s*seconds", content)
    if not matches:
        return None
    return float(matches[-1])


def parse_folder_info(folder_path: Path):
    """Return nodes, customers, seed extracted from folder name."""
    match = FOLDER_PATTERN.search(folder_path.name)
    if not match:
        return None
    nodes, customers, seed = match.groups()
    return int(nodes), int(customers), int(seed)


def process_all_folders(base_dir: Path):
    """Process each scenario folder and collect metrics."""
    results = []

    for folder in sorted(base_dir.iterdir()):
        if not folder.is_dir():
            continue

        folder_info = parse_folder_info(folder)
        if not folder_info:
            print(f"Skipping {folder.name}: name does not match expected pattern")
            continue

        nodes, customers, seed = folder_info

        final_files = list(folder.glob("final_status_*.txt"))
        if not final_files:
            print(f"Warning: No final_status file in {folder.name}")
            continue

        generator_logs = list(folder.glob("example_generator_output_*.txt"))
        final_path = final_files[0]
        generator_path = generator_logs[0] if generator_logs else None

        try:
            final_content = final_path.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover - defensive log
            print(f"Error reading {final_path}: {exc}")
            continue

        runtime_value = None
        if generator_path:
            try:
                runtime_value = extract_runtime(generator_path.read_text(encoding="utf-8"))
            except Exception as exc:  # pragma: no cover - defensive log
                print(f"Error reading {generator_path}: {exc}")

        metrics = {
            "nodes": nodes,
            "customers": customers,
            "seed": seed,
            "travelTime": extract_travel_time(final_content),
            "energy": extract_energy(final_content),
            "distance": extract_distance(final_content),
            "modulesSwapped": extract_modules_swapped(final_content),
            "runtime": runtime_value,
        }

        results.append(metrics)
        print(f"Processed {folder.name}")

    return results


def write_csv(results, output_dir: Path):
    """Write per-metric CSV files."""
    metrics = [
        ("travelTime", "travelTime.csv"),
        ("energy", "energy.csv"),
        ("distance", "distance.csv"),
        ("modulesSwapped", "modulesSwapped.csv"),
        ("runtime", "runtime.csv"),
    ]

    # Sort by node count to keep rows ordered
    ordered = sorted(results, key=lambda item: item["nodes"])

    for metric_key, filename in metrics:
        csv_path = output_dir / filename
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["nodes", "customers", metric_key])
            for entry in ordered:
                writer.writerow(
                    [entry["nodes"], entry["customers"], entry.get(metric_key, "")]
                )
        print(f"Wrote {filename}")


if __name__ == "__main__":
    base_path = Path(__file__).parent
    print("Extracting metrics from NodeChange scenarios...")
    collected = process_all_folders(base_path)
    print("\nCreating CSV files...")
    write_csv(collected, base_path)
    print("\nDone!")

