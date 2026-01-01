#!/usr/bin/env python3
"""
Extract graph images from Jupyter notebook outputs.
Organizes images by # section (folder) and ## subsection (filename).
"""

import json
import base64
import re
from pathlib import Path


def sanitize_name(name: str) -> str:
    """
    Sanitize a string to be a valid folder/file name.
    - Remove invalid characters: < > : " / \\ | ? *
    - Collapse whitespace, trim, replace spaces with _
    """
    # Remove markdown header prefixes
    name = re.sub(r'^#+\s*', '', name)
    # Remove invalid filename characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Collapse whitespace and trim
    name = ' '.join(name.split())
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    return name


def extract_images_from_notebook(notebook_path: Path, output_root: Path):
    """
    Extract images from a single notebook.
    Returns count of images extracted.
    """
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    current_section = None  # # header (folder name)
    current_subsection = None  # ## header (file name)
    section_counts = {}  # Track duplicate ## names within sections
    images_extracted = 0
    
    for cell in nb.get('cells', []):
        cell_type = cell.get('cell_type', '')
        source = ''.join(cell.get('source', []))
        
        if cell_type == 'markdown':
            # Check for # or ## headers
            lines = source.strip().split('\n')
            if lines:
                first_line = lines[0].strip()
                if first_line.startswith('## '):
                    # Subsection header
                    current_subsection = sanitize_name(first_line)
                elif first_line.startswith('# '):
                    # Section header
                    current_section = sanitize_name(first_line)
                    current_subsection = None
                    section_counts = {}  # Reset counts for new section
        
        elif cell_type == 'code':
            # Check for image outputs
            outputs = cell.get('outputs', [])
            for output in outputs:
                # Check for display_data or execute_result with image
                data = output.get('data', {})
                image_data = data.get('image/png')
                
                if image_data and current_section and current_subsection:
                    # Build output path
                    section_folder = output_root / current_section
                    section_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Handle duplicates
                    key = (current_section, current_subsection)
                    if key in section_counts:
                        section_counts[key] += 1
                        filename = f"{current_subsection}_{section_counts[key]}.png"
                    else:
                        section_counts[key] = 1
                        filename = f"{current_subsection}.png"
                    
                    output_path = section_folder / filename
                    
                    # Decode base64 and save
                    image_bytes = base64.b64decode(image_data)
                    with open(output_path, 'wb') as img_file:
                        img_file.write(image_bytes)
                    
                    print(f"  Saved: {output_path.relative_to(output_root)}")
                    images_extracted += 1
    
    return images_extracted


def main():
    viz_folder = Path('viz')
    output_root = Path('images')
    
    # Find all .ipynb files
    notebooks = list(viz_folder.glob('*.ipynb'))
    
    if not notebooks:
        print(f"No notebooks found in {viz_folder}")
        return
    
    print(f"Found {len(notebooks)} notebook(s) in {viz_folder}")
    print(f"Output folder: {output_root}")
    print()
    
    total_images = 0
    
    for nb_path in notebooks:
        print(f"Processing: {nb_path.name}")
        count = extract_images_from_notebook(nb_path, output_root)
        print(f"  Extracted {count} images")
        total_images += count
        print()
    
    print(f"Done! Total images extracted: {total_images}")


if __name__ == '__main__':
    main()

