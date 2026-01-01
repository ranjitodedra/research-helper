#!/usr/bin/env python3
"""
Extract summary statistics from SUMO routing output files in outputx directory
and export to CSV format.

Processes sumo_routing_output_*.txt (timestamped) and run_*.txt (numbered) files
and extracts key metrics from each FINAL JOURNEY STATUS section.
"""

import re
import csv
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


def extract_file_data(file_path: Path, run_number: int) -> Optional[Dict[str, float]]:
    """
    Extract key metrics from a single SUMO routing output file.
    
    Args:
        file_path: Path to the output file
        run_number: Run number (for error messages)
        
    Returns:
        Dictionary with extracted values or None if extraction failed
    """
    if not file_path.exists():
        print(f"Warning: File not found: {file_path}", file=sys.stderr)
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as e:
        print(f"Warning: Error reading {file_path}: {e}", file=sys.stderr)
        return None
    
    # Find the FINAL JOURNEY STATUS section (at the end of the file)
    final_status_match = re.search(
        r"============================================================\s*\n"
        r"FINAL JOURNEY STATUS\s*\n"
        r"============================================================\s*\n"
        r"(.*?)"
        r"============================================================",
        file_content,
        re.DOTALL
    )
    
    if not final_status_match:
        print(f"Warning: File {file_path.name} does not contain FINAL JOURNEY STATUS section", 
              file=sys.stderr)
        return None
    
    # Extract from the FINAL JOURNEY STATUS section only
    final_status_section = final_status_match.group(1)
    
    patterns = {
        'Total Travel Time': r"Total Travel Time:\s*([0-9]+(?:\.[0-9]+)?)\s*minutes",
        'Total Energy Consumed': r"Total Energy Consumed:\s*([0-9]+(?:\.[0-9]+)?)\s*kWh",
        'Total Distance Covered': r"Total Distance Covered:\s*([0-9]+(?:\.[0-9]+)?)\s*km",
        'Total Module Swapped': r"Number of Modules Swapped:\s*([0-9]+)"
    }
    
    data = {}
    missing_fields = []
    
    for field_name, pattern in patterns.items():
        match = re.search(pattern, final_status_section)
        if match:
            value_str = match.group(1)
            if field_name == 'Total Module Swapped':
                data[field_name] = int(value_str)
            else:
                data[field_name] = float(value_str)
        else:
            missing_fields.append(field_name)
    
    # Extract Run Time from the end of the file (after FINAL JOURNEY STATUS)
    run_time_match = re.search(
        r"SUMO Scenario runtime:\s*([0-9]+(?:\.[0-9]+)?)\s*seconds",
        file_content
    )
    if run_time_match:
        data['Run Time'] = float(run_time_match.group(1))
    else:
        missing_fields.append('Run Time')
    
    if missing_fields:
        print(f"Warning: File {file_path.name} missing fields: {', '.join(missing_fields)}", 
              file=sys.stderr)
        return None
    
    return data


def process_directory(input_dir: Path) -> List[Dict[str, float]]:
    """
    Process all sumo_routing_output_*.txt and run_*.txt files in the input directory.
    
    Args:
        input_dir: Path to directory containing SUMO routing output files
        
    Returns:
        List of dictionaries containing extracted data for each valid file
    """
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find all sumo_routing_output_*.txt files (new timestamped format)
    timestamped_files = sorted(input_dir.glob("sumo_routing_output_*.txt"))
    
    # Find all run_*.txt files (old numbered format) for backward compatibility
    numbered_files = sorted(input_dir.glob("run_*.txt"), 
                           key=lambda p: int(re.search(r'run_(\d+)\.txt', p.name).group(1)) 
                           if re.search(r'run_(\d+)\.txt', p.name) else 0)
    
    # Combine both patterns, prioritizing timestamped files
    output_files = list(timestamped_files) + list(numbered_files)
    
    if not output_files:
        print(f"Error: No SUMO routing output files found in {input_dir}", file=sys.stderr)
        print("Expected files matching: sumo_routing_output_*.txt or run_*.txt", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(output_files)} SUMO routing output files")
    
    all_data = []
    
    # Process files in sorted order (by filename/timestamp)
    for run_num, output_file in enumerate(output_files, start=1):
        print(f"Processing {output_file.name}...", end=" ", flush=True)
        
        run_data = extract_file_data(output_file, run_num)
        if run_data:
            # Add run number and filename to the data
            run_data['runs'] = run_num
            run_data['filename'] = output_file.name
            all_data.append(run_data)
            print("OK")
        else:
            print("FAILED")
    
    if not all_data:
        print("Error: No valid data extracted from any files", file=sys.stderr)
        sys.exit(1)
    
    return all_data


def write_csv(data: List[Dict[str, float]], output_path: Path) -> None:
    """
    Write extracted data to CSV file.
    
    Args:
        data: List of dictionaries with extracted values
        output_path: Path to output CSV file
    """
    if not data:
        print("Warning: No data to write to CSV", file=sys.stderr)
        return
    
    # Define column order
    fieldnames = [
        'runs',
        'filename',
        'Total Travel Time',
        'Total Energy Consumed',
        'Total Distance Covered',
        'Run Time',
        'Total Module Swapped'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort by run number to ensure correct order
        sorted_data = sorted(data, key=lambda x: x['runs'])
        
        for row_data in sorted_data:
            row = {
                'runs': row_data['runs'],
                'filename': row_data.get('filename', ''),
                'Total Travel Time': row_data['Total Travel Time'],
                'Total Energy Consumed': row_data['Total Energy Consumed'],
                'Total Distance Covered': row_data['Total Distance Covered'],
                'Run Time': row_data['Run Time'],
                'Total Module Swapped': row_data['Total Module Swapped']
            }
            writer.writerow(row)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract summary statistics from SUMO routing output files in outputx directory'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        default='outputx',
        help='Input directory containing sumo_routing_output_*.txt or run_*.txt files (default: outputx)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='outputx_summary.csv',
        help='Output CSV file path (default: outputx_summary.csv)'
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_path = Path(args.output)
    
    # Process the directory
    print(f"Processing files from: {input_dir}")
    data = process_directory(input_dir)
    
    # Write to CSV
    write_csv(data, output_path)
    
    # Print summary
    num_rows = len(data)
    print(f"\nSuccessfully extracted data from {num_rows} files")
    print(f"CSV file written to: {output_path}")


if __name__ == "__main__":
    main()
