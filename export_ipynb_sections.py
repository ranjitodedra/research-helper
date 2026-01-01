"""
Export first DataFrame-like output (text/plain) + first inline PNG plot per `## Subtitle`
inside each top-level markdown `# Title` section of Jupyter notebooks.

Constraints:
- Parses notebooks with nbformat WITHOUT executing.
- Uses only standard library + nbformat + pandas.
- Robust to missing outputs / malformed notebooks; skips missing pairs and continues.

Output layout:
  ./images/<Title_slug>/<Subtitle_slug>.csv
  ./images/<Title_slug>/<Subtitle_slug>.png

Usage:
  python viz/export_ipynb_sections.py <directory>
If <directory> is omitted, defaults to the script's directory (viz/).
"""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import nbformat
import pandas as pd


WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def slugify(name: str, *, max_len: int = 120) -> str:
    """
    Convert an arbitrary heading into a filesystem-safe name.
    - Windows-safe: removes <>:\"/\\|?* and control chars
    - Collapses whitespace and punctuation to underscores
    - Trims trailing dots/spaces (Windows quirk)
    - Avoids reserved DOS device names
    """
    s = (name or "").strip()
    if not s:
        s = "untitled"

    # Replace path separators and other illegal chars with underscore
    s = re.sub(r"[<>:\"/\\\\|?*\x00-\x1F]", "_", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # Replace remaining non-safe chars with underscore
    s = re.sub(r"[^A-Za-z0-9 .,_\-()]+", "_", s)
    # Collapse runs of underscores/spaces
    s = re.sub(r"[ _]+", "_", s).strip("_")

    # Windows cannot end with dot/space
    s = s.rstrip(". ").strip()
    if not s:
        s = "untitled"

    # Avoid reserved device names (case-insensitive)
    if s.upper() in WINDOWS_RESERVED_NAMES:
        s = f"_{s}"

    # Limit length (keep extension handling outside of this)
    if len(s) > max_len:
        s = s[:max_len].rstrip("_")
        if not s:
            s = "untitled"

    return s


def unique_path(path: Path) -> Path:
    """
    If `path` exists, append _2, _3, ... before suffix.
    """
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 2
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def iter_ipynb_files(root: Path) -> Iterator[Path]:
    """
    Recursively yield .ipynb files under `root`.
    """
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".ipynb"):
                yield Path(dirpath) / fn


def _markdown_heading(md: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Return (level, text) for markdown headings that start a line with '#' or '##'.
    Only cares about levels 1 and 2.
    """
    if not md:
        return None, None
    # Look at first non-empty line
    for line in md.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not m:
            return None, None
        level = len(m.group(1))
        text = m.group(2).strip()
        if level in (1, 2):
            return level, text
        return None, None
    return None, None


@dataclass
class SubtitleBlock:
    title: str
    subtitle: str
    cell_indices: List[int]


def build_subtitle_blocks(nb: nbformat.NotebookNode) -> List[SubtitleBlock]:
    """
    Slice a notebook into `# Title` -> `## Subtitle` blocks.

    Subtitle block boundary rule (per user): from `##` until next `##` or next `#`.
    """
    blocks: List[SubtitleBlock] = []
    current_title: Optional[str] = None
    current_subtitle: Optional[str] = None
    current_cells: List[int] = []

    def flush():
        nonlocal current_cells, current_subtitle, current_title
        if current_title and current_subtitle and current_cells:
            blocks.append(
                SubtitleBlock(
                    title=current_title,
                    subtitle=current_subtitle,
                    cell_indices=current_cells[:],
                )
            )
        current_cells = []

    for idx, cell in enumerate(nb.cells):
        if cell.get("cell_type") == "markdown":
            level, text = _markdown_heading(cell.get("source", ""))
            if level == 1:
                # New title ends any current subtitle block
                flush()
                current_title = text
                current_subtitle = None
                continue
            if level == 2 and current_title:
                # New subtitle ends previous subtitle block
                flush()
                current_subtitle = text
                continue

        # Collect cells inside a subtitle block only if we are inside a title+subtitle
        if current_title and current_subtitle:
            current_cells.append(idx)

    flush()
    return blocks


def _output_text_plain(output: Dict) -> Optional[str]:
    """
    Extract text/plain from a Jupyter output, if present.
    """
    if output.get("output_type") in ("execute_result", "display_data"):
        data = output.get("data", {})
        txt = data.get("text/plain")
        if isinstance(txt, str):
            return txt
        if isinstance(txt, list):
            return "".join(txt)
    if output.get("output_type") == "stream" and output.get("name") == "stdout":
        txt = output.get("text")
        if isinstance(txt, str):
            return txt
        if isinstance(txt, list):
            return "".join(txt)
    return None


def looks_like_dataframe_text(text: str) -> bool:
    """
    Very lightweight heuristic: does this look like a printed pandas DataFrame?
    We keep this permissive but avoid obvious non-tables.
    """
    if not text:
        return False
    s = text.strip()
    if len(s) < 20:
        return False
    # Common trailing lines we ignore (but still can be DF output)
    # We'll handle them in parsing.
    lines = [ln for ln in s.splitlines() if ln.strip()]
    if len(lines) < 2:
        return False
    # Must have some spacing separation typical of DataFrame alignment.
    if not any(re.search(r"\s{2,}", ln) for ln in lines[:5]):
        return False
    # Avoid single-line dict/list repr
    if s.startswith("{") or s.startswith("["):
        return False
    return True


def parse_dataframe_from_text_plain(text: str) -> Optional[pd.DataFrame]:
    """
    Parse a pandas DataFrame-ish `text/plain` block into a DataFrame.
    Uses read_fwf to handle aligned columns.
    """
    if not looks_like_dataframe_text(text):
        return None

    # Drop common trailers that appear in Series prints
    cleaned_lines: List[str] = []
    for ln in text.splitlines():
        if ln.strip().startswith(("dtype:", "Name:")):
            continue
        cleaned_lines.append(ln.rstrip())
    cleaned = "\n".join(cleaned_lines).strip()
    if not cleaned:
        return None

    try:
        df = pd.read_fwf(StringIO(cleaned))
    except Exception:
        return None

    # Heuristic: drop a pure 0..n-1 index column if it appears as first column
    if len(df.columns) >= 2:
        first_col = df.columns[0]
        if str(first_col).startswith("Unnamed"):
            col_vals = df.iloc[:, 0].astype(str).str.strip()
            if col_vals.str.fullmatch(r"\d+").all():
                # If sequential, drop it
                try:
                    nums = col_vals.astype(int).tolist()
                    if nums == list(range(len(nums))):
                        df = df.iloc[:, 1:]
                except Exception:
                    pass

    return df


def _output_png_bytes(output: Dict) -> Optional[bytes]:
    """
    Extract inline PNG bytes from a Jupyter output (image/png base64).
    """
    if output.get("output_type") in ("execute_result", "display_data"):
        data = output.get("data", {})
        b64 = data.get("image/png")
        if isinstance(b64, str) and b64.strip():
            try:
                return base64.b64decode(b64)
            except Exception:
                return None
    return None


def extract_first_df_and_png(
    nb: nbformat.NotebookNode, cell_indices: List[int]
) -> Tuple[Optional[pd.DataFrame], Optional[bytes]]:
    """
    Within the given cells, find:
    - first dataframe-like text/plain output
    - first inline image/png output that follows it (or just first overall if DF found first)
    """
    found_df: Optional[pd.DataFrame] = None
    found_png: Optional[bytes] = None

    for idx in cell_indices:
        cell = nb.cells[idx]
        if cell.get("cell_type") != "code":
            continue
        for output in cell.get("outputs", []) or []:
            if found_df is None:
                txt = _output_text_plain(output)
                if txt:
                    df = parse_dataframe_from_text_plain(txt)
                    if df is not None and not df.empty:
                        found_df = df
                        continue
            # PNG can be found after DF or (if DF already found) in later outputs/cells
            if found_df is not None and found_png is None:
                png = _output_png_bytes(output)
                if png:
                    found_png = png
                    return found_df, found_png

    # If we found DF but no PNG in later outputs, do another pass for the first png in block
    if found_df is not None and found_png is None:
        for idx in cell_indices:
            cell = nb.cells[idx]
            if cell.get("cell_type") != "code":
                continue
            for output in cell.get("outputs", []) or []:
                png = _output_png_bytes(output)
                if png:
                    found_png = png
                    return found_df, found_png

    return found_df, found_png


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Export DF+PNG per notebook Title/Subtitle section.")
    parser.add_argument(
        "directory",
        nargs="?",
        default=str(Path(__file__).resolve().parent),
        help="Directory to scan for .ipynb files (default: viz/).",
    )
    args = parser.parse_args(argv)

    root = Path(args.directory).resolve()
    if not root.exists() or not root.is_dir():
        print(f"[error] Not a directory: {root}", file=sys.stderr)
        return 2

    images_root = Path.cwd() / "images"
    images_root.mkdir(parents=True, exist_ok=True)

    notebooks = list(iter_ipynb_files(root))
    total_notebooks = 0
    total_exported = 0
    total_skipped = 0

    for nb_path in notebooks:
        total_notebooks += 1
        exported_in_nb = 0
        try:
            nb = nbformat.read(nb_path, as_version=4)
        except Exception as e:
            print(f"[skip] {nb_path}: failed to read ({e})")
            total_skipped += 1
            continue

        blocks = build_subtitle_blocks(nb)
        if not blocks:
            print(f"[ok]  {nb_path}: no Title/Subtitle sections found")
            continue

        for block in blocks:
            title_slug = slugify(block.title)
            subtitle_slug = slugify(block.subtitle)
            out_dir = images_root / title_slug
            out_dir.mkdir(parents=True, exist_ok=True)

            df, png_bytes = extract_first_df_and_png(nb, block.cell_indices)
            if df is None or png_bytes is None:
                total_skipped += 1
                continue

            csv_path = unique_path(out_dir / f"{subtitle_slug}.csv")
            png_path = unique_path(out_dir / f"{subtitle_slug}.png")

            try:
                df.to_csv(csv_path, index=False)
                png_path.write_bytes(png_bytes)
            except Exception as e:
                print(f"[skip] {nb_path} :: {block.title} / {block.subtitle}: write failed ({e})")
                total_skipped += 1
                continue

            exported_in_nb += 1
            total_exported += 1
            print(f"[save] {nb_path.name} -> {csv_path} ; {png_path}")

        print(f"[ok]  {nb_path}: exported {exported_in_nb} subtitle(s)")

    print(f"[done] notebooks={total_notebooks} exported={total_exported} skipped={total_skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


