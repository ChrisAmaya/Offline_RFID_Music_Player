#!/usr/bin/env python3
"""Simple script to test whether a local .mp3 file can be played."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_player() -> str:
    for cmd in (["mpv", "--no-video", "--really-quiet"], ["mplayer"], ["ffplay", "-nodisp", "-autoexit"]):
        if shutil.which(cmd[0]):
            return " ".join(cmd)
    raise RuntimeError("No compatible player found. Install mpv, mplayer, or ffplay.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test playback of a local MP3 file")
    parser.add_argument("audio_file", help="Path to the .mp3 file")
    args = parser.parse_args()

    audio_path = Path(args.audio_file).expanduser()
    if not audio_path.exists():
        print(f"File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    if audio_path.suffix.lower() != ".mp3":
        print(f"Expected a .mp3 file, got: {audio_path}", file=sys.stderr)
        sys.exit(1)

    player = find_player()
    print(f"Playing: {audio_path}")
    print(f"Using player: {player}")
    subprocess.Popen(player.split() + [str(audio_path)])


if __name__ == "__main__":
    main()
