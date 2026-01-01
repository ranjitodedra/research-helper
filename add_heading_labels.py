#!/usr/bin/env python3
"""
Automatically add sequence labels (a), (b), (c)... to markdown ## headings
in Jupyter notebooks, grouped by their parent # section.

Usage:
    python add_heading_labels.py notebook.ipynb
    python add_heading_labels.py notebook.ipynb --backup
    python add_heading_labels.py notebook.ipynb --dry-run
"""

import json
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


def extract_h1_title(markdown_text: str) -> Optional[str]:
    """Extract # Title (H1) from markdown text."""
    # Match lines that start with # (but not ##)
    pattern = r'^#\s+(.+?)\s*$'
    match = re.search(pattern, markdown_text, re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_h2_headings(markdown_text: str) -> List[Tuple[int, str]]:
    """
    Extract all ## headings from markdown text.
    Returns list of (line_index, heading_text) tuples.
    """
    headings = []
    lines = markdown_text.split('\n')
    
    for i, line in enumerate(lines):
        # Match lines that start with ## (but not ###)
        match = re.match(r'^##\s+(.+?)\s*$', line)
        if match:
            heading_text = match.group(1).strip()
            # Check if it already has a label like (a), (b), etc.
            if not re.match(r'^\([a-z]\)\s+', heading_text):
                headings.append((i, heading_text))
    
    return headings


def add_sequence_label(heading_text: str, sequence_num: int) -> str:
    """
    Add sequence label (a), (b), (c)... to heading text.
    sequence_num: 0 -> (a), 1 -> (b), etc.
    """
    label = chr(ord('a') + sequence_num)
    return f"({label}) {heading_text}"


def process_notebook(notebook_path: Path, dry_run: bool = False, backup: bool = False) -> None:
    """
    Process a notebook and add sequence labels to ## headings.
    
    Args:
        notebook_path: Path to the .ipynb file
        dry_run: If True, only print what would be changed without modifying the file
        backup: If True, create a backup file before modifying
    """
    print(f"Processing: {notebook_path.name}")
    
    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells = notebook.get('cells', [])
    current_section = None
    h2_counter = {}  # Track H2 count per section
    changes_made = []
    
    for cell_idx, cell in enumerate(cells):
        if cell.get('cell_type') != 'markdown':
            continue
        
        # Get markdown source (can be string or list)
        source = cell.get('source', '')
        if isinstance(source, list):
            markdown_text = ''.join(source)
        else:
            markdown_text = source
        
        # Check for H1 (section title)
        h1_title = extract_h1_title(markdown_text)
        if h1_title:
            current_section = h1_title
            h2_counter[current_section] = 0
            print(f"  Found section: {current_section}")
            continue
        
        # Process H2 headings in this cell
        h2_headings = extract_h2_headings(markdown_text)
        if h2_headings and current_section:
            # Update markdown text with sequence labels
            lines = markdown_text.split('\n')
            modified = False
            
            for line_idx, heading_text in h2_headings:
                # Get current sequence number for this section
                seq_num = h2_counter[current_section]
                new_heading = add_sequence_label(heading_text, seq_num)
                
                # Replace the line
                old_line = lines[line_idx]
                new_line = re.sub(r'^##\s+(.+?)\s*$', f'## {new_heading}', old_line, count=1)
                lines[line_idx] = new_line
                
                # Increment counter
                h2_counter[current_section] += 1
                modified = True
                
                changes_made.append({
                    'section': current_section,
                    'cell': cell_idx,
                    'old': old_line.strip(),
                    'new': new_line.strip()
                })
            
            if modified:
                # Update cell source
                new_text = '\n'.join(lines)
                if isinstance(cell['source'], list):
                    # Preserve list format if original was list
                    cell['source'] = new_text.splitlines(keepends=True)
                else:
                    cell['source'] = new_text
    
    # Print summary
    if changes_made:
        print(f"\n  Made {len(changes_made)} changes:")
        for change in changes_made:
            print(f"    [{change['section']}]")
            print(f"      {change['old']}")
            print(f"      -> {change['new']}")
    else:
        print("  No changes needed.")
    
    # Write back if not dry run
    if not dry_run and changes_made:
        if backup:
            backup_path = notebook_path.with_suffix('.ipynb.bak')
            print(f"\n  Creating backup: {backup_path.name}")
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
        
        print(f"  Writing updated notebook...")
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"  ✓ Done!")
    elif dry_run:
        print(f"\n  [DRY RUN] No changes written to file.")


def main():
    parser = argparse.ArgumentParser(
        description='Add sequence labels (a), (b), (c)... to markdown ## headings in Jupyter notebooks'
    )
    parser.add_argument(
        'notebook',
        type=Path,
        help='Path to .ipynb file'
    )
    parser.add_argument(
        '--backup', '-b',
        action='store_true',
        help='Create a backup file before modifying'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Show what would be changed without modifying the file'
    )
    
    args = parser.parse_args()
    
    if not args.notebook.exists():
        print(f"Error: File not found: {args.notebook}")
        return
    
    if args.notebook.suffix != '.ipynb':
        print(f"Error: File must be a .ipynb file: {args.notebook}")
        return
    
    try:
        process_notebook(args.notebook, dry_run=args.dry_run, backup=args.backup)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()