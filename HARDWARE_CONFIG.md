# RFID/CD Music Player - Hardware Configuration
## Verified Configuration (May 5, 2026) - Updated May 19, 2026

**SCOPE CHANGE**: Display (ILI9488) removed from project scope. See LOGBOOK.md for details.

### Raspberry Pi 3B GPIO Connections

#### RFID Reader (RC522) Connections
| RFID Pin | Function | Pi Pin | GPIO | Status |
|----------|----------|--------|------|--------|
| 3.3V | Power | 1 | 3V3 | ✓ Connected |
| GND | Ground | 6 | GND | ✓ Connected |
| MOSI | SPI Data In | 19 | GPIO 10 | ✓ Connected |
| MISO | SPI Data Out | 21 | GPIO 9 | ✓ Connected |
| SCK (SCLK) | SPI Clock | 23 | GPIO 11 | ✓ Connected |
| SDA (CS) | Chip Select | 24 | GPIO 8 | ✓ Connected |
| RST (RESET) | Reset | 22 | GPIO 25 | ✓ Connected |
| IRQ | Interrupt (Optional) | - | - | Not connected |

### SPI Bus Configuration
**Shared SPI0 Bus:**
- SCLK (GPIO 11) → Pin 23
- MOSI (GPIO 10) → Pin 19
- MISO (GPIO 9) → Pin 21

**Chip Select Pins (Separate):**
- RFID CS → GPIO 8 (Pin 24)

### GPIO Pin Summary
**SPI0 Bus for RFID:**
- GPIO 9   = SPI MISO        (Pin 21)
- GPIO 10  = SPI MOSI        (Pin 19)
- GPIO 11  = SPI SCLK        (Pin 23)
- GPIO 8   = RFID CS         (Pin 24)
- GPIO 25  = RFID RST        (Pin 22)
### Power and Grounding
- **Pi 3.3V Output**: Connected to RFID 3.3V (Pin 1)
- **Pi GND**: Common ground with RFID (Pin 6, 9, etc)

### Configuration Status
- ✓ RFID 3.3V on Pin 1
- ✓ RFID SDA (CS) on Pin 24 (GPIO 8)
- ✓ RFID RST on Pin 22 (GPIO 25)
- ✓ All SPI pins connected correctly
- ✓ All connections verified and secure

### Testing Status
- **SPI Devices**: Verified and working
- **RFID**: Awaiting tag detection19, 2026
**Verified By**: neonkon
**Status**: ✓ HARDWARE CONFIGURATION CORRECT - RFID ONLY (Display removed from scope)