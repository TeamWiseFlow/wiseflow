#!/usr/bin/env python3
"""Validate and package the standalone WorkBuddy expert, including hidden metadata."""

import argparse
import json
from pathlib import Path
import sys
import tempfile
import zipfile

from validate_expert import DEFAULT_SOURCE, ValidationError, validate


def build(source, output=None):
    source = source.resolve()
    config, files = validate(source)
    output = (output or source.parent / "dist" / f"{config['name']}-{config['version']}.zip").resolve()
    if output.is_relative_to(source):
        raise ValidationError("output must be outside expert source")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as handle:
            temporary = Path(handle.name)
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file in files:
                member = f"{config['name']}/{file.relative_to(source).as_posix()}"
                info = zipfile.ZipInfo(member, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100755 if file.suffix == '.sh' else 0o100644) << 16
                archive.writestr(info, file.read_bytes())
        temporary.replace(output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        output = build(args.source, args.output)
    except (ValidationError, OSError, TypeError) as error:
        print(json.dumps({"success": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"success": True, "archive": str(output), "bytes": output.stat().st_size}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
