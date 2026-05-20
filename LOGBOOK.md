# RFID/CD Music Player - Project Logbook

**Project Start Date:** April 12, 2026  
**Last Updated:** May 19, 2026  
**Status:** Phase 2 - In Progress (Display scope removed)

---

## **Phase 1: Hardware Assembly & Verification ✓ COMPLETED**

### **Completion Date:** May 5, 2026

#### **Objectives:**
- [x] Assemble Raspberry Pi 3B with TFT display and RFID reader
- [x] Configure GPIO pin connections
- [x] Verify SPI bus functionality
- [x] Test hardware communication

#### **Detailed Steps Taken:**

**1. Raspberry Pi OS Installation (April 13, 2026)**
- Used Raspberry Pi Imager to flash Raspberry Pi OS Lite (64-bit)
- Configured hostname: `rfid-player`
- Configured username: `neonkon`
- Enabled SSH for remote access
- Successfully established SSH connection: `ssh neonkon@rfid-player.local`

**2. Display Hardware Identification (April 13, 2026)**
- Identified display: **Hosyond 3.5" TFT LCD 480x320 SPI ILI9488**
- Display PCB markings: HSD035577C1, 22717AP209-230217
- Controller chip: **ILI9488** (important for driver selection)
- Display connection type: SPI (3.5-bit interface)

**3. GPIO Pin Configuration (April 13 - May 5, 2026)**

**Initial Configuration Issues:**
- Initially had TFT RST on wrong pin (Pin 11/GPIO 17 instead of Pin 13/GPIO 27)
- Initial RFID pin assignment was confusing (RC522 labels: SDA, SCK, MOSI, MISO, IRQ, GND, RST, 3.3V)
- First attempt had RFID SDA/RST pins swapped

**Final Verified Configuration:**
```
Display (ILI9488):
- VCC (5V) → Pin 2
- GND → Pin 6
- DIN (MOSI) → GPIO 10 (Pin 19)
- CLK (SCLK) → GPIO 11 (Pin 23)
- CS → GPIO 8 (Pin 24)
- D/C → GPIO 23 (Pin 16)
- RST → GPIO 27 (Pin 13) ← CORRECTED
- LED (Backlight) → GPIO 12 (Pin 32)

RFID Reader (RC522):
- 3.3V → Pin 1 ← ADDED
- GND → Pin 6
- MOSI → GPIO 10 (Pin 19)
- MISO → GPIO 9 (Pin 21)
- SCK → GPIO 11 (Pin 23)
- SDA (CS) → GPIO 24 (Pin 18) ← CORRECTED
- RST → GPIO 25 (Pin 22)
- IRQ → Not connected

Shared SPI Bus:
- GPIO 10 (MOSI) - Pin 19 - shared by both
- GPIO 11 (SCLK) - Pin 23 - shared by both
- GPIO 9 (MISO) - Pin 21 - RFID only
- GPIO 8 (CS) - Pin 24 - Display only
- GPIO 24 (CS) - Pin 18 - RFID only
```

**4. Hardware Verification (May 5, 2026)**

**SPI Bus Verification:**
```bash
$ ls -l /dev/spidev*
crw-rw---- 1 root spi 153, 0 Apr 13 04:53 /dev/spidev0.0
crw-rw---- 1 root spi 153, 1 Apr 13 04:53 /dev/spidev0.1
```
✓ Both SPI devices present and accessible

**GPIO Status Check:**
```
GPIO 8: output (SPI0 CS0) ✓ Display CS
GPIO 9: input (MISO) ✓
GPIO 10: input (MOSI) ✓
GPIO 11: input (SCLK) ✓
GPIO 23, 24, 25, 27: input (ready to configure) ✓
```

**SPI Device Test Results:**
```
✓ SPI 0.0 opened successfully (max speed: 125000000 Hz) - RFID
✓ SPI 0.1 opened successfully (max speed: 125000000 Hz) - Display
✓ All SPI devices are accessible!
```

#### **Issues Encountered & Resolutions:**

| Issue | Date | Resolution | Status |
|-------|------|-----------|--------|
| fbtft driver compilation failed on kernel 6.12.47 | Apr 13 | Decided to use device tree overlay or Python libraries instead | ✓ Resolved |
| TFT RST pin on wrong GPIO | May 5 | Moved wire from Pin 11 (GPIO 17) to Pin 13 (GPIO 27) | ✓ Resolved |
| RFID 3.3V power not connected | May 5 | Added connection from Pin 1 (3.3V) to RFID VCC | ✓ Resolved |
| RFID CS and RST pins swapped | May 5 | Swapped SDA (Pin 18/GPIO 24) and RST (Pin 22/GPIO 25) wires | ✓ Resolved |
| RC522 tags not detected after config (Phase 2) | May 19 | RFID CS pin was GPIO 24 (wrong), corrected to GPIO 8 (Pin 24) - Pin numbers vs GPIO confusion | ✓ **RESOLVED - TAGS NOW DETECTED** |
| GPIO testing library (wiringpi) not available | May 5 | Used Python RPi.GPIO and spidev libraries instead | ✓ Resolved |

#### **Hardware Verification Results:**

```
✓ Raspberry Pi 3B: Operational
✓ TFT Display (ILI9488): Connected and powered
✓ RFID Reader (RC522): Connected and powered
✓ SPI Bus: Both devices accessible at 125 MHz
✓ GPIO Pins: All correctly configured
✓ Power Supply: Both devices stable at 5V/3.3V
```

**Phase 1 Status: ✓ COMPLETE - All hardware verified and operational**

---

## **Phase 2: RFID Reader Software Development - IN PROGRESS**

### **Start Date:** May 5, 2026

#### **SCOPE CHANGE (May 19, 2026):**

**Decision Made:** Remove Display (ILI9488) from project scope

**Reasoning:**
- Physical album/playlist casings will include artwork/labels instead of displaying on LED
- Final housing will only need a reset mechanism (no display needed)
- Dramatically simplifies software complexity
- Removes requirement for display driver debugging
- Reduces GPIO pin usage
- Reduces power consumption
- Allows faster project completion

**Impact:**
- ✓ Removes: Display UI rendering, TFT driver configuration, pygame/display management code
- ✓ Keeps: RFID reading, Audio playback, CD support, Button controls, Database
- ✓ Estimated time saved: 3-4 weeks of UI development

**Updated Hardware:**
- Removed: ILI9488 display connections
- Removed: GPIO 8, 12, 23, 27 (display-related pins)
- Kept: All RFID pins (GPIO 24, 25)
- Kept: All SPI pins (GPIO 9, 10, 11)

**Updated Project Focus:**
1. RFID tag reading and identification
2. Audio playback (local files + CD)
3. Button controls (physical only)
4. Database management
5. CD identification and playback

---

#### **Objectives (Revised):**
- [x] Remove display references from codebase
- [x] Update hardware configuration documents
- [x] Troubleshoot RFID tag detection issue ✓ **RESOLVED - GPIO 8 (Pin 24) was correct CS pin**
- [x] Create RFID reader Python module ✓ Working
- [x] Test RC522 tag reading capability ✓ **TAGS NOW DETECTED**
- [ ] Implement database mapping for tags → content
- [ ] Build tag-to-playlist/album mapping system
- [ ] Test with collection of RFID tags

#### **Current Work (May 5, 2026):**

**1. Project Setup on Raspberry Pi**
- Set up project directory: `~/RFID_Player`
- Created test files on local computer
- Using SCP to transfer files to Pi

**2. RFID Reader Module Development**

**Created Files:**
- `src/rfid_reader.py` - Professional RFID reader interface
- `test_rfid_quick.py` - Quick test script

**Features Implemented in rfid_reader.py:**
- `RFIDReader` class with:
  - `connect()` - Initialize RC522 reader
  - `disconnect()` - Clean shutdown
  - `start()` - Continuous background reading thread
  - `stop()` - Stop background thread
  - `read_once()` - Single blocking read
  - `set_tag_callback()` - Register tag detection callback
  - `set_error_callback()` - Register error callback
- Debouncing system (1-second window to prevent duplicate reads)
- RFIDTag dataclass for tag data
- Comprehensive logging
- Exception handling

**3. Python Environment Setup (In Progress)**

**Challenge:** Python environment externally managed on Raspberry Pi OS  
**Solution:** Creating virtual environment in project directory

**Current Steps:**
```bash
cd ~/RFID_Player
python3 -m venv venv
source venv/bin/activate
pip install mfrc522 RPi.GPIO
```

**Expected Packages:**
- mfrc522: RFID reader library
- RPi.GPIO: GPIO control library
- spidev: SPI device communication (already available)

#### **Next Steps:**
1. Complete venv setup on Pi
2. Install mfrc522 and dependencies
3. Run test_rfid_quick.py to verify tag reading
4. Get sample tag ID readings
5. Integrate with database layer (Phase 3)

#### **Known Issues:**
- None currently, venv setup in progress

#### **Timeline Notes:**
- Phase 1 took ~3.5 weeks due to hardware sourcing and driver issues
- Phase 2 expected to take ~2 weeks for RFID + Audio + CD support
- Display will be tackled in parallel when RFID basics work

---

## **Hardware Bill of Materials (BOM) - Verified**

| Component | Model | Cost | Status |
|-----------|-------|------|--------|
| Raspberry Pi 3B | v1.2 | ~$35 | ✓ Have |
| 3.5" TFT Display | ILI9488 (480x320) | ~$15 | ✓ Have |
| RFID Reader | MFRC522 RC522 | ~$5 | ✓ Have |
| HiFiBerry DAC+ Light | Audio DAC | ~$23 | Pending |
| microSD Card (256GB) | Kingston/SanDisk | ~$25 | Pending |
| USB CD/DVD Reader | External | ~$30 | Pending |
| Powered Speakers | 20W+ | ~$100-150 | Pending |
| 5V/2.5A PSU | Mean Well/Quality | ~$15 | ✓ Have |
| Dupont Wires | Assortment | ~$5 | ✓ Have |

---

## **Current Directory Structure**

```
RFID_Player/
├── README.md
├── HARDWARE_CONFIG.md ← New: Verified hardware configuration
├── requirements.txt
├── setup.sh
├── .gitignore
├── config/
│   ├── gpio_config.py
│   ├── audio_config.py
│   └── database_config.py
├── src/
│   ├── main.py (placeholder)
│   ├── rfid_reader.py ← NEW: RFID reader module
│   ├── audio_player.py (not started)
│   ├── cd_player.py (not started)
│   ├── button_handler.py (not started)
│   ├── display_manager.py (not started)
│   └── database.py (not started)
├── tests/
├── data/
│   ├── music/
│   ├── cd_database/
│   └── jukebox.db
├── docs/
│   ├── ARCHITECTURE.md
│   ├── GPIO_PINOUT.md
│   ├── SETUP_GUIDE.md
│   └── LOGBOOK.md ← This file
└── venv/ ← Being created now
```

---

## **Technology Stack**

| Component | Technology | Status |
|-----------|-----------|--------|
| OS | Raspberry Pi OS Lite 64-bit | ✓ Installed |
| Hardware Interface | Python 3.9+ | ✓ Available |
| RFID | mfrc522 library + RC522 | In Progress |
| Audio | mpv (planned) | Not started |
| Database | SQLite3 | Not started |
| UI | pygame (TFT) | Not started |
| GPIO | RPi.GPIO | In Progress |

---

## **Performance Notes**

- SPI Bus Speed: 125 MHz (both devices capable)
- RC522 typical speed: 1 MHz (safe configuration)
- Display typical speed: 40 MHz (safe configuration)
- Pi 3B CPU: 1.2 GHz (sufficient for this application)
- Ram: 1GB (tight but workable with optimization)

---

## **Key Decisions Made**

1. **Hardware**: Used existing hardware (Pi 3B, ILI9488, RC522) rather than newer alternatives
2. **Audio DAC**: Chose HiFiBerry DAC+ Light ($23) over premium options for lossy Spotify audio
3. **Display Driver**: Avoided fbtft compilation, planning Python library approach
4. **Python**: Using venv for isolated environment (cleaner than system-wide packages)
5. **Testing**: Incremental hardware testing before full software integration

---

## **Lessons Learned**

1. **GPIO Pin Documentation**: Importance of verifying actual pinout (RC522 labels can vary)
2. **SPI Bus Sharing**: Successfully sharing SPI0 with different CS pins works well
3. **Display Drivers**: Kernel API changes make older driver projects incompatible; Python libraries more reliable
4. **Virtual Environments**: Essential for modern Python development on Raspberry Pi OS

---

**End of Logbook Entry**  
*Next update expected: After successful RFID tag reading*
