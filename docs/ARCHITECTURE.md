# Architecture

## Runtime Flow

```text
RFID tag
  -> multi_tag_rfid_playlist_controls.py
  -> rfid_library.py
  -> album/tracklist.txt
  -> mpv via Unix IPC socket
  -> HiFiBerry DAC
```

The main process keeps one RFID monitor and one hardware-control session alive. Scanning a different mapped tag replaces only the mpv process, preserving button, LED, and potentiometer behavior.

## Modules

- `multi_tag_rfid_playlist_controls.py`: Main executable, RFID monitoring, album switching, and shutdown.
- `rfid_library.py`: SQLite tag mappings, tag normalization, and tracklist creation/validation.
- `rfid_playlist_controls.py`: mpv startup plus buttons, shuffle LED, and potentiometer volume.
- `mpv_button_controller.py`: Unix socket transport using newline-delimited JSON IPC.
- `album_tracklist.py`: Metadata-first track ordering with alphabetical fallback.
- `button_handler.py`: Debounced active-low button polling.
- `led_handler.py`: Shuffle status LED.
- `potentiometer_handler.py`: PCF8591 ADC polling and volume callbacks.

## Data

`data/rfid_library.db` stores `content`, `content_entries`, and unique `tag_mappings`. Media remains outside the repository on the Raspberry Pi. Each album directory contains a generated `tracklist.txt` with absolute paths.

## mpv Control

mpv is started with:

```bash
mpv --no-audio-display --audio-device=alsa/default \
    --audio-samplerate=48000 --loop-playlist=inf \
    --no-input-terminal --input-ipc-server=/tmp/rfid-mpv.sock \
    --playlist=/path/to/tracklist.txt
```

Commands are sent as JSON, for example:

```json
{"command": ["cycle", "pause"]}
```

## Scope

The project is offline local-audio playback only. CD playback and display support are intentionally excluded.
