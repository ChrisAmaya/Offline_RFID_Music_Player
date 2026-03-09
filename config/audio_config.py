"""
Audio Configuration for RFID Music Player
"""

# HiFiBerry DAC+ Light Configuration
AUDIO_INTERFACE = "hifiberry-dac-plus-light"
AUDIO_DEVICE = "default"

# Volume Configuration
DEFAULT_VOLUME = 70  # Percentage (0-100)
MIN_VOLUME = 5
MAX_VOLUME = 100
VOLUME_STEP = 5  # % per button press

# Audio Player Configuration
AUDIO_PLAYER = "mpv"
MPV_CONFIG = {
    "ao": "alsa",  # Audio output driver
    "audio_device": "default",
    "volume": DEFAULT_VOLUME,
    "softvol": "yes",  # Software volume control
}

# Supported Audio Formats
SUPPORTED_FORMATS = [
    "mp3",
    "flac",
    "wav",
    "ogg",
    "aac",
    "m4a",
]

# CD Audio Configuration
CD_AUDIO_FORMAT = "wav"  # Extract as WAV from CD
CD_RIP_QUALITY = "best"  # cdparanoia quality setting

# Buffer settings
AUDIO_BUFFER_SIZE = 4096
AUDIO_SAMPLE_RATE = 44100  # CD quality default

# Equalizer (if needed)
EQUALIZER_ENABLED = False

print(f"Audio Configuration loaded")
