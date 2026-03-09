# RFID/CD Music Player Architecture

## System Overview

```
┌─────────────────────────────────────────────────────┐
│            RFID/CD Music Player                       │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Input     │  │   Playback   │  │  Database  │ │
│  ├─────────────┤  ├──────────────┤  ├────────────┤ │
│  │ · RFID      │  │ · mpv        │  │ · SQLite   │ │
│  │ · Buttons   │  │ · CD Audio   │  │ · Albums   │ │
│  │ · CD TOC    │  │ · Volume     │  │ · Playlists│ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
│         │                │                │           │
└────────┼────────────────┼────────────────┼───────────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                   ┌──────▼──────┐
                   │   Display   │
                   │  (TFT 480x320)
                   │             │
                   └─────────────┘
```

## Module Structure

### 1. **rfid_reader.py**
Handles RFID tag reading and detection.
- RC522 interface via SPI
- Tag ID parsing
- Database lookup (tag → content mapping)
- Event callbacks on tag detection

### 2. **audio_player.py**
Manages music playback via mpv.
- Play/pause/stop commands
- Volume control (software)
- Playlist management
- Audio format support
- Event callbacks (track changed, playback finished)

### 3. **cd_player.py**
Manages CD reading and playback.
- CD drive detection
- TOC (Table of Contents) reading
- MusicBrainz fingerprint matching
- Audio extraction/streaming
- Album metadata retrieval

### 4. **button_handler.py**
GPIO button input handling.
- Debouncing logic
- Button press events
- Long-press detection
- Command routing to player

### 5. **display_manager.py**
TFT display rendering and UI.
- Album art display
- Now playing info
- Playback controls UI
- Status indicators
- Framebuffer rendering

### 6. **database.py**
SQLite database management.
- Music library schema
- RFID tag mappings
- CD metadata storage
- Query operations
- Data persistence

### 7. **main.py**
Application entry point and orchestration.
- Component initialization
- Event loop
- Error handling
- Graceful shutdown

## Data Flow

### Playing via RFID
```
RFID Tag Detected
    ↓
rfid_reader.parse_tag_id()
    ↓
database.lookup_rfid_tag(tag_id)
    ↓
Retrieve: {content_type, content_id}
    ↓
IF content_type == "album":
    database.get_album_tracks(album_id)
    audio_player.queue_playlist(tracks)
    audio_player.play()
    ↓
IF content_type == "playlist":
    database.get_playlist_tracks(playlist_id)
    audio_player.queue_playlist(tracks)
    audio_player.play()
    ↓
display_manager.show_now_playing()
```

### Playing from CD
```
CD Inserted
    ↓
cd_player.detect_cd()
    ↓
cd_player.read_toc()
    ↓
cd_player.get_musicbrainz_fingerprint()
    ↓
database.lookup_cd_by_toc(fingerprint)
    ↓
IF match found:
    database.get_cd_metadata(cd_id)
    display_manager.show_album_art()
ELSE:
    display_manager.show_generic_cd_icon()
    ↓
cd_player.play_track(track_number)
    ↓
audio_player.play_cd_audio_stream()
```

### Button Press
```
Button GPIO Interrupt
    ↓
button_handler.debounce_check()
    ↓
button_handler.identify_button()
    ↓
Execute Command:
  · PLAY_PAUSE → audio_player.toggle_pause()
  · NEXT → audio_player.next_track()
  · PREV → audio_player.prev_track()
  · SHUFFLE → audio_player.toggle_shuffle()
  · VOL_UP → audio_player.volume_up()
  · VOL_DOWN → audio_player.volume_down()
    ↓
display_manager.update_status()
```

## State Management

The player maintains these states:
- **Playback State**: IDLE, PLAYING, PAUSED, STOPPED
- **Source State**: LOCAL_FILE, CD, STREAMING
- **RFID State**: TAG_DETECTED, TAG_NOT_DETECTED
- **UI State**: NOW_PLAYING, MENU, SETTINGS

## Database Schema

See `config/database_config.py` for complete schema.

Key relationships:
```
Albums ──┬──→ RFID Tags (via rfid_tags.content_id)
         └──→ Playlists (many-to-many via playlist_tracks)

Playlists ──→ Playlist Tracks ──→ Audio Files

CDs ──→ CD Tracks ──→ TOC Fingerprints
```

## GPIO Bus Topology

```
┌─────────────────────┐
│   Raspberry Pi 3B   │
├─────────────────────┤
│                     │
│  SPI0 Bus (Shared)  │
│  ├─ CLK   (GPIO 11) │
│  ├─ MOSI  (GPIO 10) │
│  ├─ MISO  (GPIO 9)  │
│  ├─ CE0   (GPIO 8)  ──→ TFT Display CS
│  └─ CE1   (GPIO 7)  
│                     │
│  Custom CS Pins:    │
│  ├─ GPIO 24 ───────→ RFID RC522 CS
│  ├─ GPIO 23 ───────→ TFT DC (Data/Cmd)
│  └─ GPIO 27 ───────→ TFT RST (Reset)
│                     │
│  I2S (Audio)        │
│  ├─ GPIO 12 (CLK)  │
│  ├─ GPIO 35 (DATA) │
│  └─ GPIO 40 (SYNC) │
│  ──────────────────→ HiFiBerry DAC+ Light
│                     │
│  GPIO Buttons       │
│  ├─ GPIO 17 ───────→ Play/Pause
│  ├─ GPIO 18 ───────→ Next
│  ├─ GPIO 22 ───────→ Previous
│  ├─ GPIO 26 ───────→ Shuffle
│  ├─ GPIO 5  ───────→ Volume Up
│  └─ GPIO 6  ───────→ Volume Down
│                     │
│  USB (Audio + CD)   │
│  ├─ Audio DAC ─────→ USB Port
│  └─ CD Drive ──────→ USB Port
│                     │
└─────────────────────┘
```

## Error Handling

### RFID Reader Failures
- Timeout and retry
- Log to file
- Display error on TFT

### Audio Playback Errors
- Graceful fallback
- Queue next track
- User notification

### CD Read Errors
- Fallback to generic CD name
- Skip corrupted tracks
- Log details

### Database Errors
- Connection pooling
- Automatic retry
- Corruption recovery

## Performance Considerations

- **Memory**: Monitor with `psutil`
- **CPU**: Profile hot paths
- **I/O**: Async file operations where possible
- **Latency**: Keep button response < 100ms

## Testing Strategy

```
tests/
├── test_rfid_reader.py
├── test_audio_player.py
├── test_cd_player.py
├── test_button_handler.py
├── test_display_manager.py
├── test_database.py
└── integration/
    └── test_end_to_end.py
```

## Deployment Phases

1. **Phase 1-2**: Hardware validation
2. **Phase 3-5**: Core software (local playback)
3. **Phase 6-7**: CD support + database
4. **Phase 8-9**: UI + optimization + testing

See main [README.md](../README.md) for timeline details.
