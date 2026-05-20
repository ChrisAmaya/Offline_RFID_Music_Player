"""
GPIO Pin Configuration for RFID Music Player
Raspberry Pi 3B with 40-pin GPIO header
"""

# RFID-RC522 SPI Configuration
RFID_SPI_PORT = 0
RFID_SPI_DEVICE = 0
RFID_CS_PIN = 8           # GPIO 8 (Physical Pin 24, Chip Select)
RFID_RST_PIN = 25         # GPIO 25 (Physical Pin 22, Reset)

# Button GPIO Pins (TBD - To be configured during integration)
# BUTTON_PLAY_PAUSE = 17    # GPIO 17
# BUTTON_NEXT = 27          # GPIO 27
# BUTTON_PREV = 22          # GPIO 22
# BUTTON_SHUFFLE = 18       # GPIO 18
# BUTTON_VOLUME_UP = 23     # GPIO 23

# Debounce time in milliseconds
DEBOUNCE_TIME = 50

# Button hold time for long press (ms)
LONG_PRESS_TIME = 1000

# SPI Speed (Hz)
SPI_SPEED = 1000000  # 1 MHz (RC522 typical)
DISPLAY_SPI_SPEED = 40000000  # 40 MHz (TFT typical)

# GPIO Mode
GPIO_MODE = "BCM"  # Broadcom numbering

# Pin mapping as dict for reference
GPIO_PINS = {
    "rfid": {
        "cs": RFID_CS_PIN,
        "rst": RFID_RST_PIN,
    },
    "display": {
        "cs": DISPLAY_CS_PIN,
        "dc": DISPLAY_DC_PIN,
        "rst": DISPLAY_RST_PIN,
        "backlight": DISPLAY_BACKLIGHT_PIN,
    },
    "buttons": {
        "play_pause": BUTTON_PLAY_PAUSE,
        "next": BUTTON_NEXT,
        "prev": BUTTON_PREV,
        "shuffle": BUTTON_SHUFFLE,
        "volume_up": BUTTON_VOLUME_UP,
        "volume_down": BUTTON_VOLUME_DOWN,
    }
}

print(f"GPIO Configuration loaded for Raspberry Pi 3B")
