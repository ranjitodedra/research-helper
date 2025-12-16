import os
import re
import csv
from pathlib import Path

# Mapping of folder names to node counts
FOLDER_TO_NODES = {
    "20c_10bss_50total": 50,
    "40c_20bss_100total": 100,
    "60c_30bss_150total": 150,
    "80c_40bss_200total": 200
}

# Mapping of file patterns to algorithm names
FILE_TO_ALGO = {
    "H_output.txt": "H",
    "AC_ouput.txt": "AC",  # Note: typo in filename "ouput" instead of "output"
    "GA_ouput.txt": "GA",  # Note: typo in filename "ouput" instead of "output"
    "C&W_output.txt": "C&W"
}

def extract_travel_time(content):
    """Extract total travel time in minutes"""
    # Check for "inf" first
    if re.search(r'Total Travel Time:\s*inf', content, re.IGNORECASE):
        return 'inf'
    match = re.search(r'Total Travel Time:\s*([\d.]+)\s*minutes?', content)
    if match:
        return float(match.group(1))
    return None

def extract_energy(content):
    """Extract total energy consumed in kWh"""
    # Check for "inf" first
    if re.search(r'Total Energy Consumed:\s*inf', content, re.IGNORECASE):
        return 'inf'
    match = re.search(r'Total Energy Consumed:\s*([\d.]+)\s*kWh', content)
    if match:
        return float(match.group(1))
    return None

def extract_modules_swapped(content):
    """Extract number of modules swapped"""
    # Try "Total Modules Swapped" first
    match = re.search(r'Total Modules Swapped:\s*(\d+)', content)
    if match:
        return int(match.group(1))
    # Try "Number of Modules Swapped"
    match = re.search(r'Number of Modules Swapped:\s*(\d+)', content)
    if match:
        return int(match.group(1))
    return None

def extract_runtime(content):
    """Extract program runtime in seconds"""
    # Try "Program Runtime" format (may be "Xm Y.XXs" or "X.XX seconds")
    match = re.search(r'Program Runtime:\s*(\d+)m\s*([\d.]+)s', content)
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes * 60 + seconds
    
    match = re.search(r'Program Runtime:\s*([\d.]+)\s*seconds?', content)
    if match:
        return float(match.group(1))
    
    # Try "JSON Scenario runtime"
    match = re.search(r'JSON Scenario runtime:\s*([\d.]+)\s*seconds?', content)
    if match:
        return float(match.group(1))
    
    return None

def extract_distance(content):
    """Extract total distance covered in km"""
    match = re.search(r'Total Distance Covered:\s*([\d.]+)\s*km', content)
    if match:
        return float(match.group(1))
    return None

def process_all_files(base_dir):
    """Process all output files and extract metrics"""
    results = {
        'travelTime': {},
        'energy': {},
        'modulesSwapped': {},
        'runtime': {},
        'distance': {}
    }
    
    base_path = Path(base_dir)
    
    for folder_name, node_count in FOLDER_TO_NODES.items():
        folder_path = base_path / folder_name
        
        if not folder_path.exists():
            print(f"Warning: Folder {folder_name} not found")
            continue
        
        for file_pattern, algo in FILE_TO_ALGO.items():
            # Find the file matching the pattern
            matching_files = list(folder_path.glob(f"*{file_pattern}"))
            
            if not matching_files:
                print(f"Warning: No file matching {file_pattern} in {folder_name}")
                continue
            
            file_path = matching_files[0]
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract all metrics
                travel_time = extract_travel_time(content)
                energy = extract_energy(content)
                modules_swapped = extract_modules_swapped(content)
                runtime = extract_runtime(content)
                distance = extract_distance(content)
                
                # Store results
                key = (node_count, algo)
                
                if travel_time is not None:
                    results['travelTime'][key] = travel_time
                if energy is not None:
                    results['energy'][key] = energy
                if modules_swapped is not None:
                    results['modulesSwapped'][key] = modules_swapped
                if runtime is not None:
                    results['runtime'][key] = runtime
                if distance is not None:
                    results['distance'][key] = distance
                
                print(f"Processed {folder_name}/{file_path.name}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    return results

def create_csv_files(results, output_dir):
    """Create CSV files from extracted results"""
    output_path = Path(output_dir)
    
    # Define the order of algorithms
    algo_order = ['H', 'AC', 'GA', 'C&W']
    node_order = [50, 100, 150, 200]
    
    # Create each CSV file
    csv_files = {
        'travelTime': 'travelTime.csv',
        'energy': 'energy.csv',
        'modulesSwapped': 'modulesSwapped.csv',
        'runtime': 'runtime.csv',
        'distance': 'distance.csv'
    }
    
    for metric_name, csv_filename in csv_files.items():
        csv_path = output_path / csv_filename
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['node'] + algo_order)
            
            # Write data rows
            for node_count in node_order:
                row = [node_count]
                for algo in algo_order:
                    key = (node_count, algo)
                    value = results[metric_name].get(key, '')
                    row.append(value)
                writer.writerow(row)
        
        print(f"Created {csv_filename}")

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Process all files
    print("Extracting metrics from output files...")
    results = process_all_files(script_dir)
    
    # Create CSV files
    print("\nCreating CSV files...")
    create_csv_files(results, script_dir)
    
    print("\nDone!")

