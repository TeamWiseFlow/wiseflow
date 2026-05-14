#!/usr/bin/env python3
"""
pptx_to_png.py — Convert PPTX slides to individual PNG images for visual verification.

Requires LibreOffice installed on the system.
Each slide is rendered as a separate PNG at screen resolution.

Usage:
  python3 pptx_to_png.py --input presentation.pptx --outdir ./tmp/ppt-pngs
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

_CONVERSION_TIMEOUT = 120  # seconds


def find_libreoffice() -> str | None:
    """Locate the libreoffice binary on the system."""
    # Try direct command first
    for candidate in ("libreoffice", "soffice"):
        if shutil.which(candidate):
            return candidate

    # Check common install paths
    for path in (
        "/usr/bin/libreoffice",
        "/usr/lib/libreoffice/program/soffice",
        "/opt/libreoffice/program/soffice",
        "/snap/bin/libreoffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ):
        if Path(path).exists():
            return path

    return None


def convert_pptx_to_png(pptx_path: str, outdir: str) -> list[str]:
    """Convert each slide of a PPTX file to a PNG image.

    Returns a sorted list of generated PNG file paths.
    """
    pptx_path_obj = Path(pptx_path).resolve()
    out_path_obj = Path(outdir).resolve()

    if not pptx_path_obj.exists():
        print(f"[error] PPTX file not found: {pptx_path_obj}", file=sys.stderr)
        sys.exit(1)

    lo_bin = find_libreoffice()
    if lo_bin is None:
        print(
            "[error] LibreOffice not found. Install it to enable visual verification:\n"
            "  sudo apt install libreoffice-impress   # Debian/Ubuntu\n"
            "  brew install --cask libreoffice        # macOS",
            file=sys.stderr,
        )
        sys.exit(1)

    # Clean stale PNGs from previous runs, then create output directory
    if out_path_obj.exists():
        for f in out_path_obj.iterdir():
            if f.suffix == ".png":
                f.unlink()
    out_path_obj.mkdir(parents=True, exist_ok=True)

    print(f"[pptx2png] Converting {pptx_path_obj} → {out_path_obj}/")
    cmd = [
        lo_bin,
        "--headless",
        "--convert-to", "png",
        "--outdir", str(out_path_obj),
        str(pptx_path_obj),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=_CONVERSION_TIMEOUT)
    except subprocess.TimeoutExpired:
        print(
            f"[error] LibreOffice conversion timed out after {_CONVERSION_TIMEOUT}s. "
            "The PPTX file may be too large or corrupted.",
            file=sys.stderr,
        )
        sys.exit(1)

    if result.returncode != 0:
        print(f"[error] LibreOffice conversion failed (exit={result.returncode})",
              file=sys.stderr)
        if result.stderr:
            print(f"  stderr: {result.stderr.strip()}", file=sys.stderr)
        if result.stdout:
            print(f"  stdout: {result.stdout.strip()}", file=sys.stderr)
        sys.exit(1)

    # Collect generated PNGs (LibreOffice names them "Slide1.png", "Slide2.png", ...)
    png_files = sorted(
        out_path_obj.glob("*.png"),
        key=lambda p: _slide_sort_key(p.name),
    )

    if not png_files:
        print("[error] No PNG files generated", file=sys.stderr)
        sys.exit(1)

    print(f"[pptx2png] Generated {len(png_files)} slide image(s):")
    for f in png_files:
        print(f"  {f}")

    return [str(f) for f in png_files]


def _slide_sort_key(filename: str) -> int:
    """Extract slide number from filename like 'Slide1.png' or 'slide_1.png'."""
    stem = Path(filename).stem
    m = re.search(r"(\d+)$", stem)
    return int(m.group(1)) if m else 0


def main() -> None:
    """Parse CLI arguments and run PPTX-to-PNG conversion."""
    parser = argparse.ArgumentParser(
        description="Convert PPTX slides to PNG images for visual verification"
    )
    parser.add_argument("--input", required=True, help="Path to .pptx file")
    parser.add_argument("--outdir", required=True, help="Output directory for PNG images")
    args = parser.parse_args()

    convert_pptx_to_png(args.input, args.outdir)


if __name__ == "__main__":
    main()
