#!/usr/bin/env python3
"""Minimal VLC audio player test using python-vlc bindings."""

import argparse
import sys
from pathlib import Path

try:
    import vlc
except ImportError as exc:
    print("python-vlc is not installed. Install it with: pip3 install python-vlc", file=sys.stderr)
    raise SystemExit(1) from exc


def build_player(audio_path: Path):
    instance = vlc.Instance(
        "--intf", "dummy",
        "--no-video",
        "--aout=alsa",
        "--alsa-audio-device=hw:1,0",
    )
    media = instance.media_new(str(audio_path))
    player = instance.media_player_new()
    player.set_media(media)
    return instance, player


def main() -> None:
    parser = argparse.ArgumentParser(description="Play an audio file using python-vlc")
    parser.add_argument("audio_file", help="Path to the audio file to play")
    args = parser.parse_args()

    audio_path = Path(args.audio_file).expanduser()
    if not audio_path.exists():
        print(f"File not found: {audio_path}", file=sys.stderr)
        raise SystemExit(1)

    instance, player = build_player(audio_path)
    print(f"Playing: {audio_path}")
    player.play()

    # Wait briefly so the user can confirm playback started.
    import time
    time.sleep(2)

    # Leave the process running until interrupted.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping playback")
        player.stop()


if __name__ == "__main__":
    main()
