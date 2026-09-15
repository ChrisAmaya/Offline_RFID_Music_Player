# Offline RFID Music Player

An offline Raspberry Pi 3B music player that maps RFID tags to local album playlists and plays them through mpv.

## Features

- RFID tag-to-album mapping stored in SQLite
- Automatic `tracklist.txt` generation from audio metadata
- Alphabetical fallback ordering when track metadata is unavailable
- mpv playback through the HiFiBerry DAC at 48 kHz
- Play/pause, next, previous, and shuffle buttons
- Shuffle status LED
- PCF8591 potentiometer volume control
- Album switching while playback is active
- Infinite playlist looping
- Offline operation

## Runtime

Start the player:

```bash
python3 src/multi_tag_rfid_playlist_controls.py
```

Register a tag to an album directory:

```bash
python3 src/multi_tag_rfid_playlist_controls.py \
  --register 1053655409858 \
  /home/neonkon/Music/mac-miller-swimming
```

Registration creates or refreshes the album's `tracklist.txt` and stores the mapping in `data/rfid_library.db`.

## Project Structure

```text
config/
  gpio_config.py             Shared BCM and BOARD pin configuration
  database_config.py         SQLite database paths
src/
  multi_tag_rfid_playlist_controls.py  Main RFID runtime
  rfid_library.py            Tag mappings and tracklist generation
  rfid_playlist_controls.py  mpv and hardware-control session
  mpv_button_controller.py   mpv JSON IPC transport
  album_tracklist.py         Metadata-based track ordering
  button_handler.py          Debounced button polling
  led_handler.py             Shuffle LED control
  potentiometer_handler.py   PCF8591 volume input
sandbox/
  Hardware and mapping diagnostics
tests/
  Software regression tests
data/rfid_library.db          Runtime tag-to-album database
docs/
  Setup and hardware documentation
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt update
sudo apt install mpv unzip
```

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for setup and [docs/GPIO_PINOUT.md](docs/GPIO_PINOUT.md) for verified pin assignments.

## Testing

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Hardware diagnostics in `sandbox/` require the Raspberry Pi and connected hardware.

## Scope

This project intentionally does not support CD playback or a display. The current scope is local audio, RFID, physical controls, and the HiFiBerry output.
