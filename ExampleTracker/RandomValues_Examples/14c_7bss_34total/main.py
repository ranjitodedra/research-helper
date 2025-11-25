import os
import re
import csv
import glob

def parse_value(content, patterns):
    """
    Searches for the first match of any pattern in the content.
    Returns the extracted value or None.
    """
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def get_file_info(filename):
    """
    Parses filename to extract the Prefix (Instance ID) and the Method.
    Handles 'output.txt', 'ouput.txt', and 'example.txt' variations.
    """
    base = os.path.basename(filename)
    
    # Remove extension
    name_no_ext = os.path.splitext(base)[0]
    
    # Split by underscore
    parts = name_no_ext.split('_')
    
    # Logic to identify Method and Prefix
    # Case 1: ends in _output or _ouput (e.g., 9c_4bss_22total_AC_ouput)
    if parts[-1].lower() in ['output', 'ouput']:
        method = parts[-2]
        prefix_parts = parts[:-2]
    # Case 2: ends in _example (e.g., 9c_4bss_22total_example)
    elif parts[-1].lower() == 'example':
        method = 'example'
        prefix_parts = parts[:-1]
    else:
        # Fallback: assume last part is method if fairly short, otherwise generic
        method = parts[-1]
        prefix_parts = parts[:-1]

    prefix = "_".join(prefix_parts)
    
    # Optional: Try to extract just the "22total" part for a shorter ID, 
    # matching the user's requested CSV format.
    # If standard pattern "total" is found in prefix, use that as the simplified ID.
    short_id_match = re.search(r'(\d+total)', prefix)
    short_id = short_id_match.group(1) if short_id_match else prefix
    
    return short_id, method, prefix

def main():
    # 1. Setup Regex Patterns
    # Matches "Total Travel Time: 123" OR "Travel time: 123"
    time_patterns = [
        r"(?:Total Travel Time|Travel time)[:\s]+([\d\.]+)",
    ]
    
    # Matches "Total Energy Consumed: 123" OR "Total energy depletion: 123"
    energy_patterns = [
        r"(?:Total Energy Consumed|Total energy depletion)[:\s]+([\d\.]+)",
    ]

    # Data structure: data[instance_id][method] = {time: X, energy: Y}
    data = {}
    all_methods = set()

    # 2. Iterate over all .txt files in current directory
    txt_files = glob.glob("*.txt")
    
    print(f"Found {len(txt_files)} text files. Processing...")

    for filepath in txt_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            short_id, method, full_prefix = get_file_info(filepath)
            
            # Extract values
            time_val = parse_value(content, time_patterns)
            energy_val = parse_value(content, energy_patterns)
            
            # Clean up values (strip whitespace)
            if time_val: time_val = time_val.strip()
            if energy_val: energy_val = energy_val.strip()

            # Initialize dict entry if not exists
            if short_id not in data:
                data[short_id] = {}
            
            data[short_id][method] = {
                'time': time_val,
                'energy': energy_val
            }
            
            all_methods.add(method)
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    # 3. Sort methods and instances for consistent CSV output
    # We want 'example' generic header, then sorted methods: AC, C&W, CPLEX, example, GA, H
    sorted_methods = sorted(list(all_methods))
    sorted_ids = sorted(data.keys())

    # 4. Write CSV files
    # Define headers: First column generic "example" (as requested), then methods
    headers = ['example'] + sorted_methods

    # --- Write Time CSV ---
    with open('output_time.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for instance in sorted_ids:
            row = [instance]
            for method in sorted_methods:
                val = data[instance].get(method, {}).get('time', 'N/A')
                row.append(val)
            writer.writerow(row)
    
    print("Created output_time.csv")

    # --- Write Energy CSV ---
    with open('output_energy.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for instance in sorted_ids:
            row = [instance]
            for method in sorted_methods:
                val = data[instance].get(method, {}).get('energy', 'N/A')
                row.append(val)
            writer.writerow(row)

    print("Created output_energy.csv")

if __name__ == "__main__":
    main()