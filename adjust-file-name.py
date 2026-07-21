#!/usr/bin/env python3
"""
Rename audio files in a directory by prepending an artist name.

Examples:
  python3 adjust-file-name.py --artist "Mac Miller" --files "So It Goes.mp3" "2009.mp3"
  python3 adjust-file-name.py --artist "Mac Miller" --dir ~/All_Songs --pattern "*.mp3"

The script will rename files to:
  Artist-SongName.ext

It preserves the original file extension and works on one or many files.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List


def rename_files(artist: str, files: List[Path], dry_run: bool = False) -> List[str]:
    artist_prefix = artist.strip()
    if not artist_prefix:
        raise ValueError("Artist name cannot be empty")

    renamed = []
    for path in files:
        if not path.exists():
            print(f"Skipping missing file: {path}", file=sys.stderr)
            continue
        if not path.is_file():
            print(f"Skipping non-file: {path}", file=sys.stderr)
            continue

        ext = path.suffix
        stem = path.stem
        new_name = f"{artist_prefix}-{stem}{ext}"
        new_path = path.with_name(new_name)

        if new_path.exists() and new_path.resolve() != path.resolve():
            print(f"Target already exists: {new_path}", file=sys.stderr)
            continue

        if dry_run:
            renamed.append(f"{path.name} -> {new_path.name}")
        else:
            path.rename(new_path)
            renamed.append(f"{path.name} -> {new_path.name}")

    return renamed


def discover_files(directory: Path, pattern: str) -> List[Path]:
    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")
    return sorted(directory.glob(pattern))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rename audio files to Artist-SongName.ext")
    parser.add_argument("--artist", required=True, help="Artist or band name to prepend")
    parser.add_argument("--files", nargs="+", help="One or more files to rename")
    parser.add_argument("--dir", default="~/All_Songs", help="Directory containing files to rename")
    parser.add_argument("--pattern", default="*.mp3", help="Glob pattern to match files in the directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be renamed without changing anything")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artist = args.artist
    directory = Path(args.dir).expanduser()

    if args.files:
        files = [Path(f).expanduser() for f in args.files]
    else:
        files = discover_files(directory, args.pattern)

    if not files:
        print("No files matched the input", file=sys.stderr)
        return 1

    renamed = rename_files(artist, files, dry_run=args.dry_run)
    for item in renamed:
        print(item)

    return 0


if __name__ == "__main__":
    main()
