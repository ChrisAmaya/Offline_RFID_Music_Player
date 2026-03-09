# RFID/CD Music Player

A Raspberry Pi 3B-based music player that combines RFID tag recognition with CD playback capabilities. Play Spotify-ripped albums via RFID tags or insert physical CDs with automatic metadata lookup.

## Features

- **RFID Playback**: Tap RFID tags to play custom playlists and albums
- **CD Support**: Insert CDs with automatic TOC-based album identification
- **Local Database**: Pre-loaded MusicBrainz database for CD metadata and album art
- **Physical Controls**: 5 buttons for skip, previous, play/pause, shuffle toggle, and volume
- **High Audio Quality**: HiFiBerry DAC+ Light for clean audio output
- **3.5" Display**: Real-time album art, track info, and interface
- **Offline Operation**: No internet required for playback

## Hardware

- Raspberry Pi 3B Model v1.2
- 3.5" TFT SPI 480x320 Display + LCD Shield
- RFID-RC522 Reader
- HiFiBerry DAC+ Light
- USB CD/DVD Reader
- Powered Speakers (20W+)
- 5 Momentary Push Buttons
- 256GB microSD Card (music + database)
- 5V/2.5A Power Supply

## Software Stack

- **OS**: Raspberry Pi OS Lite
- **Audio Player**: mpv
- **Database**: SQLite3
- **Backend**: Python 3.9+
- **UI**: pygame (TFT display)
- **RFID**: mfrc522-python
- **CD Handling**: libcdio + cdparanoia

## Project Structure

```
RFID_Player/
├── README.md
├── requirements.txt
├── setup.sh
├── config/
│   ├── gpio_config.py
│   ├── audio_config.py
│   └── database_schema.sql
├── src/
│   ├── main.py
│   ├── rfid_reader.py
│   ├── audio_player.py
│   ├── cd_player.py
│   ├── button_handler.py
│   ├── display_manager.py
│   └── database.py
├── data/
│   ├── music/
│   ├── cd_database/
│   └── jukebox.db
├── tests/
│   └── test_*.py
└── docs/
    ├── GPIO_PINOUT.md
    ├── SETUP_GUIDE.md
    └── ARCHITECTURE.md
```

## Installation

1. Clone the repository
2. Run setup script: `bash setup.sh`
3. Configure settings in `config/`
4. See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed instructions

## Usage

```bash
python src/main.py
```

## Timeline

- **Phase 1-2** (Weeks 1-3): Hardware assembly and testing
- **Phase 3-5** (Weeks 3-7): Core software and playback
- **Phase 6-7** (Weeks 7-11): CD support and database integration
- **Phase 8-9** (Weeks 9-13): Testing, optimization, and finalization

## License

MIT

## Authors

- neonkon
