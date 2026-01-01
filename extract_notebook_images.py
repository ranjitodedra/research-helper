#!/usr/bin/env python3
"""
Extract images from Jupyter notebook (.ipynb) files and organize them by # Title sections.

Structure:
- images/
  - # Title 1/
    - graph_title_1.png
    - graph_title_2.png
  - # Title 2/
    - graph_title_3.png
    ...

Rules:
- Only # Title (level 1 headers) create new folders
- ## and other headers are ignored for folder organization
- Images are named after their graph title (from title= parameter or ax.set_title())
- Images go into the folder of the current # Title section
"""

import json
import base64
import re
from pathlib import Path
from typing import Optional, List, Tuple
import argparse


def sanitize_filename(name: str) -> str:
    """Convert a string to a valid filename."""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    # Replace multiple spaces/underscores with single underscore
    name = re.sub(r'[_\s]+', '_', name)
    # Limit length
    if len(name) > 200:
        name = name[:200]
    return name or 'untitled'


def extract_h1_title(markdown_text: str) -> Optional[str]:
    """Extract # Title from markdown cell (only level 1, not ##)."""
    if not markdown_text:
        return None
    
    lines = markdown_text.split('\n')
    for line in lines:
        line = line.strip()
        # Match only # Title (not ## or ###)
        match = re.match(r'^#\s+(.+)$', line)
        if match:
            return match.group(1).strip()
    return None


def extract_graph_title_from_code(code_text: str) -> Optional[str]:
    """Extract graph title from code cell source."""
    if not code_text:
        return None
    
    # Pattern 1: title='...' or title="..."
    patterns = [
        r"title\s*=\s*['\"]([^'\"]+)['\"]",
        r"title\s*=\s*['\"]([^'\"]+)['\"]",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, code_text)
        if matches:
            # Get the last match (most likely the actual title, not a default)
            return matches[-1]
    
    # Pattern 2: ax.set_title('...') or ax.set_title("...")
    pattern = r"ax\.set_title\(['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, code_text)
    if matches:
        return matches[-1]
    
    # Pattern 3: plt.title('...')
    pattern = r"plt\.title\(['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, code_text)
    if matches:
        return matches[-1]
    
    return None


def extract_images_from_cell(cell: dict) -> List[bytes]:
    """Extract PNG images from a cell's outputs."""
    images = []
    
    if cell.get('cell_type') != 'code':
        return images
    
    outputs = cell.get('outputs', [])
    for output in outputs:
        if output.get('output_type') in ['display_data', 'execute_result']:
            data = output.get('data', {})
            if 'image/png' in data:
                png_data = data['image/png']
                # Handle both string and list formats
                if isinstance(png_data, list):
                    png_b64 = ''.join(png_data)
                else:
                    png_b64 = str(png_data)
                
                try:
                    image_bytes = base64.b64decode(png_b64)
                    images.append(image_bytes)
                except Exception as e:
                    print(f"  Warning: Failed to decode image: {e}")
                    continue
    
    return images


def process_notebook(notebook_path: Path, output_dir: Path):
    """Process a notebook and extract images organized by # Title sections."""
    print(f"Processing: {notebook_path.name}")
    
    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells = notebook.get('cells', [])
    current_section = None
    image_counter = {}  # Track image numbers per section for unique naming
    
    for cell_idx, cell in enumerate(cells):
        cell_type = cell.get('cell_type', '')
        source = ''.join(cell.get('source', []))
        
        # Check for # Title in markdown cells
        if cell_type == 'markdown':
            h1_title = extract_h1_title(source)
            if h1_title:
                current_section = h1_title
                print(f"  Found section: {current_section}")
                image_counter[current_section] = 0
        
        # Extract images from code cells
        if cell_type == 'code':
            images = extract_images_from_cell(cell)
            
            if images:
                # Try to get graph title from code
                graph_title = extract_graph_title_from_code(source)
                
                # Create section folder if we have images
                if current_section:
                    section_folder = output_dir / sanitize_filename(current_section)
                    section_folder.mkdir(parents=True, exist_ok=True)
                else:
                    # Images before any # Title go to "Untitled"
                    section_folder = output_dir / "Untitled"
                    section_folder.mkdir(parents=True, exist_ok=True)
                    current_section = "Untitled"
                    if current_section not in image_counter:
                        image_counter[current_section] = 0
                
                # Save each image
                for img_idx, img_data in enumerate(images):
                    image_counter[current_section] += 1
                    
                    # Determine filename
                    if graph_title:
                        filename = sanitize_filename(graph_title)
                    else:
                        filename = f"image_{image_counter[current_section]}"
                    
                    # Add extension
                    if not filename.endswith('.png'):
                        filename += '.png'
                    
                    # Ensure unique filename
                    filepath = section_folder / filename
                    counter = 1
                    while filepath.exists():
                        name_part = filename.rsplit('.', 1)[0]
                        ext = filename.rsplit('.', 1)[1] if '.' in filename else 'png'
                        filepath = section_folder / f"{name_part}_{counter}.{ext}"
                        counter += 1
                    
                    # Save image
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    
                    print(f"    Saved: {filepath.relative_to(output_dir)}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract images from Jupyter notebooks organized by # Title sections'
    )
    parser.add_argument(
        'notebooks',
        nargs='+',
        type=Path,
        help='Path(s) to .ipynb file(s) or directory containing notebooks'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('images'),
        help='Output directory (default: images/)'
    )
    
    args = parser.parse_args()
    
    # Collect all notebook files
    notebook_files = []
    for path in args.notebooks:
        path = Path(path)
        if path.is_file() and path.suffix == '.ipynb':
            notebook_files.append(path)
        elif path.is_dir():
            notebook_files.extend(path.glob('*.ipynb'))
        else:
            print(f"Warning: Skipping {path} (not a .ipynb file or directory)")
    
    if not notebook_files:
        print("No notebook files found!")
        return
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Process each notebook
    for notebook_path in notebook_files:
        try:
            process_notebook(notebook_path, args.output)
        except Exception as e:
            print(f"Error processing {notebook_path}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nDone! Images saved to: {args.output.absolute()}")


if __name__ == '__main__':
    main()

