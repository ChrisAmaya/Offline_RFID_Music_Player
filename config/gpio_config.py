"""
GPIO Pin Configuration for RFID Music Player
Raspberry Pi 3B with 40-pin GPIO header
"""

# RFID-RC522 SPI Configuration
RFID_SPI_PORT = 0
RFID_SPI_DEVICE = 0
RFID_CS_PIN = 8           # GPIO 8 (Physical Pin 24, Chip Select)
RFID_RST_PIN = 25         # GPIO 25 (Physical Pin 22, Reset)

# Button GPIO Pins
BUTTON_PLAY_PAUSE = 26    # GPIO 26 - Play/Pause
BUTTON_NEXT = 6           # GPIO 6 - Next Track
BUTTON_PREV = 5           # GPIO 5 - Previous Track
BUTTON_SHUFFLE = 22       # GPIO 22 - Shuffle On/Off

# LED GPIO Pins
LED_SHUFFLE = 27          # GPIO 27 - Shuffle status indicator

# SPI Speed (Hz)
SPI_SPEED = 1000000  # 1 MHz (RC522 typical)

# GPIO Mode
GPIO_MODE = "BCM"  # Broadcom numbering

# Pin mapping as dict for reference
GPIO_PINS = {
    "rfid": {
        "cs": RFID_CS_PIN,
        "rst": RFID_RST_PIN,
    },
    "buttons": {
        "play_pause": BUTTON_PLAY_PAUSE,
        "next": BUTTON_NEXT,
        "prev": BUTTON_PREV,
        "shuffle": BUTTON_SHUFFLE,
    },
    "leds": {
        "shuffle": LED_SHUFFLE,
    }
}

print(f"GPIO Configuration loaded for RFID/CD Music Player")
