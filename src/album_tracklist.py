#!/usr/bin/env python3
"""Build an ordered tracklist file for an album from MP3 metadata."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple


try:
    from mutagen import File as MutagenFile
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise SystemExit(f"Missing dependency: {exc}")


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        value = value[0]
    return str(value).strip()


def _extract_track_number(path: Path) -> Tuple[int, int]:
    try:
        audio = MutagenFile(path, easy=True)
    except Exception:
        audio = None

    if audio is None:
        return (999999, 999999)

    track_number = ""
    title = ""

    if hasattr(audio, "get"):
        track_number = _safe_text(audio.get("tracknumber"))
        title = _safe_text(audio.get("title"))

    if not track_number and hasattr(audio, "tags") and audio.tags is not None:
        tag = audio.tags
        if hasattr(tag, "get"):
            track_number = _safe_text(tag.get("TRCK"))
            title = _safe_text(tag.get("TIT2"))

    if not track_number:
        return (999999, 999999)

    try:
        track_number_value = track_number.split("/")[0]
        return (int(track_number_value), 0)
    except ValueError:
        return (999999, 999999)


def _fallback_sort_key(path: Path) -> Tuple[int, int, str]:
    name = path.stem.lower()
    base = name
    if "-" in base:
        base = base.split("-", 1)[1]
    if base.startswith("track"):
        base = base[5:]
    try:
        return (int(base), 0, name)
    except ValueError:
        return (999999, 0, name)


def discover_album_track_order(album_dir: Path) -> List[Path]:
    """Return album tracks ordered by metadata track number, then filename."""
    candidates = [p for p in album_dir.iterdir() if p.is_file() and p.suffix.lower() in {".mp3", ".m4a", ".flac", ".wav", ".ogg"}]
    candidates.sort(key=lambda p: (_extract_track_number(p)[0], _fallback_sort_key(p)[2]))
    return candidates


def build_tracklist_file(album_dir: Path, output_path: Path) -> List[str]:
    """Write a text file containing the absolute paths of each album track."""
    ordered_tracks = discover_album_track_order(album_dir)
    lines = [str(track.resolve()) for track in ordered_tracks]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an ordered tracklist file for an album")
    parser.add_argument("album_dir", nargs="?", default=os.path.expanduser("~/all_songs/mac_miller_swimming"))
    parser.add_argument("--output", default=None, help="Path to the output text file")
    args = parser.parse_args()

    album_dir = Path(args.album_dir).expanduser().resolve()
    if not album_dir.exists():
        print(f"Album directory not found: {album_dir}", file=sys.stderr)
        return 1

    output_path = Path(args.output).expanduser().resolve() if args.output else album_dir / "tracklist.txt"
    lines = build_tracklist_file(album_dir, output_path)
    print(f"Wrote {len(lines)} track paths to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
