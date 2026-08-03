#!/usr/bin/env python3
"""Simple script to test whether a local .mp3 file can be played."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PLAYER_OPTIONS = [
    (["vlc", "--intf", "dummy", "--play-and-exit"], "VLC"),
    (["mpv", "--no-video", "--really-quiet"], "mpv"),
    (["mplayer"], "mplayer"),
    (["ffplay", "-nodisp", "-autoexit"], "ffplay"),
]


def check_package(name: str) -> bool:
    return shutil.which(name) is not None


def check_requirements() -> None:
    print("Checking audio playback dependencies...")
    available = []
    missing = []

    for cmd, label in PLAYER_OPTIONS:
        if check_package(cmd[0]):
            available.append(label)
        else:
            missing.append(label)

    if available:
        print("Available players:", ", ".join(available))
    else:
        print("No supported audio players were found.")

    if missing:
        print("Missing players:", ", ".join(missing))
        print("Install one of them with: sudo apt install vlc mpv mplayer ffmpeg")


def find_player() -> list[str]:
    for cmd, label in PLAYER_OPTIONS:
        if check_package(cmd[0]):
            print(f"Preferred player available: {label}")
            return cmd
    raise RuntimeError("No compatible player found. Install VLC, mpv, mplayer, or ffplay.")


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

    check_requirements()

    player_cmd = find_player()
    print(f"Playing: {audio_path}")
    print(f"Using player: {' '.join(player_cmd)}")
    subprocess.Popen(player_cmd + [str(audio_path)])


if __name__ == "__main__":
    main()
