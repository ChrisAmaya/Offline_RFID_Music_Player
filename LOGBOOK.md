# RFID/CD Music Player - Project Logbook

**Project Start Date:** April 12, 2026  
**Last Updated:** May 23, 2026  
**Status:** Phase 3 In Progress - Audio system verified and working

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

## **Phase 3: Button Control Implementation - IN PROGRESS**

### **Start Date:** May 19, 2026
### **Current Status:** Button + LED Integration Complete

#### **Objectives:**
- [x] Create button handler module with debouncing
- [x] Test all 4 buttons individually ✓ Working
- [x] Verify button detection and callbacks ✓ Working
- [x] Create LED handler module ✓ Working
- [x] Test LED on/off/toggle ✓ Working
- [x] Integrate shuffle button with shuffle LED ✓ Working
- [ ] Integrate with audio playback controls
- [ ] Integrate with RFID reader

#### **Button Configuration:**
```
Button 1: Play/Pause  → GPIO 26
Button 2: Next        → GPIO 6
Button 3: Previous    → GPIO 5
Button 4: Shuffle     → GPIO 22
```

#### **LED Configuration:**
```
LED 1: Shuffle Status → GPIO 27 (ON = shuffle enabled)
```

#### **Potentiometer Configuration (May 21, 2026):**
```
PCF8591 ADC:
  I2C Bus: 1
  Address: 0x48
  SDA: GPIO 2 (Pin 3)
  SCL: GPIO 3 (Pin 5)

Potentiometer (R2k, 2102):
  Pin 1 (GND)      → Pi GND
  Pin 2 (Signal)   → PCF8591 AIN0
  Pin 3 (3.3V)     → Pi 3.3V

Volume Range: 0-100%
```

#### **Files Created:**
- `src/button_handler.py` - Button detection with debouncing and callbacks
- `src/led_handler.py` - LED control with on/off/toggle support
- `src/potentiometer_handler.py` - Potentiometer (ADC) handler with value callbacks ✓ Working
- `test_buttons.py` - Individual button test
- `test_led.py` - Individual LED test
- `test_potentiometer.py` - Potentiometer test ✓ Working
- `test_button_led_integration.py` - Shuffle button + LED integration test ✓ Working

#### **Integration Details (May 20, 2026):**

**Shuffle Button + LED Integration:**
- Shuffle button (GPIO 22) now controls LED (GPIO 27)
- Pressing shuffle button toggles between ON/OFF states
- LED state reflects shuffle status (ON = shuffle enabled)
- Debouncing prevents false triggers (50ms)
- State persists across button presses

#### **Potentiometer Volume Control (May 21, 2026):**
- Successfully identified potentiometer pin configuration
- Wired Pin 1 (GND) → Pi GND
- Wired Pin 2 (Signal) → PCF8591 AIN0
- Wired Pin 3 (3.3V) → Pi 3.3V
- PCF8591 connected via I2C (GPIO 2 SDA, GPIO 3 SCL)
- Potentiometer reading: 0-2kΩ (converted to 0-100% volume)
- Real-time volume updates with callback system
- Deadzone filtering prevents jitter (±3 raw units)
- **Status**: ✓ Working and tested successfully

#### **Audio System Setup (May 23, 2026):**
- HiFiBerry DAC+ Light mounted on Raspberry Pi 3B
- Enabled I2S in `/boot/config.txt`
- Loaded HiFiBerry device tree overlay: `dtoverlay=hifiberry-dac`
- Audio chain: HiFiBerry RCA → Amplifier RCA In → Powered Speakers
- Verified audio output using: `speaker-test -D hw:1,0 -t sine -f 1000 -c 2 -l 3`
- **Status**: ✓ Audio confirmed working through speakers
- Note: Left speaker had minor hardware issue (now fixed)

#### **Audio Testing & Discoveries (May 23, 2026):**

**Issue 1: No Controls in alsamixer**
- Ran `alsamixer -c 1` → "This sound device does not have any controls"
- Investigation: HiFiBerry driver loaded but audio control interface not fully initialized
- Resolution: Not needed for basic playback; audio works without controls
- Audio can be controlled via application level (mpv, etc.)

**Issue 2: Mono vs Stereo Confusion**
- Initial test with `aplay /usr/share/sounds/alsa/Front_Center.wav` produced no sound
- File format: "Signed 16 bit Little Endian, Rate 48000 Hz, **Mono**"
- HiFiBerry expects: **Stereo (2 channels)**
- Discovery: Physical connectors (RCA/3.5mm) ≠ audio channels
  - RCA red/white = Left/Right channels (always stereo on HiFiBerry)
  - 3.5mm jack (on HiFiBerry) = Also stereo internally
  - Mono/Stereo refers to NUMBER OF CHANNELS, not connector type
- Resolution: Use stereo audio sources (or mono-to-stereo conversion)

**Issue 3: aplay vs speaker-test Device Specification**
- Initial test: `aplay -D hw:1,0` + mono file = no sound
- Working test: `speaker-test -D hw:1,0 -t sine -f 1000 -c 2 -l 3` = confirmed audio
- Key difference: speaker-test with `-c 2` (2 channels/stereo)
- Updated test_audio_repeat.sh to use stereo speaker-test instead of mono file

**Issue 4: Default Audio Device Configuration**
- After HiFiBerry setup, system still defaulting to bcm2835 (Card 0)
- Created `/etc/asound.conf` to set HiFiBerry (Card 1) as default
- Configuration: `defaults.pcm.card 1` and `defaults.ctl.card 1`
- Effect: All audio applications automatically use HiFiBerry without device specification

**Key Learnings:**
1. HiFiBerry outputs stereo on both RCA and 3.5mm connectors
2. Stereo/mono refers to channels, not physical connectors
3. Always specify `-c 2` for stereo output to HiFiBerry
4. Set default audio device to avoid specifying `hw:1,0` in every application
5. RCA cables can be swapped between different amplifiers/speakers without software changes

**Status**: ✓ Audio system fully tested and configured for stereo output

#### **CD Player Module Setup (May 23, 2026):**
- Created USB CD module support to test CD playback capability
- Implemented three test scripts for CD functionality testing
- Created Python CD player module for future integration

**Test Scripts Created:**

1. **test_cd_detect.sh** - CD Device Detection
   - Lists available block devices
   - Searches for /dev/sr*, /dev/cdrom, /dev/dvd devices
   - Queries CD information using cdparanoia and cd-info
   - Auto-installs required dependencies if missing
   - Usage: `bash test_cd_detect.sh`

2. **test_cd_play.sh** - CD Playback Testing
   - Attempts to play CD using available backend (mpv → mplayer → cdparanoia)
   - Supports device path and duration arguments
   - Usage: `bash test_cd_play.sh [device] [duration_seconds]`
   - Example: `bash test_cd_play.sh /dev/sr0 30` (plays for 30 seconds)

3. **src/cd_player.py** - Python CD Player Module
   - Object-oriented interface for CD detection and playback
   - Automatically detects best available backend
   - Key Methods:
     - `CDPlayer(device_path)` - Initialize with CD device
     - `play()` - Start CD playback
     - `stop()` - Stop playback
     - `is_playing()` - Check current status
     - `detect_cd_devices()` - Find all available CD/DVD devices
   - Supports multiple backends: mpv, mplayer, cdparanoia
   - Can run directly for quick testing: `python3 src/cd_player.py`

**Expected Device Paths:**
- `/dev/sr0`, `/dev/sr1`, `/dev/sr2` (SCSI CD-ROM devices)
- `/dev/cdrom`, `/dev/cdrom0` (CD-ROM symlinks)
- `/dev/dvd`, `/dev/dvd0` (DVD device symlinks)

**Dependencies to Install on Raspberry Pi:**
```bash
# At least one of these required:
sudo apt-get install mpv              # Recommended - modern, works well
sudo apt-get install mplayer          # Alternative player
sudo apt-get install cdparanoia       # Audio extraction (last resort)
```

**Next Steps - Sanity Check on Raspberry Pi:**
1. Connect USB CD module to Raspberry Pi
2. Insert a CD into the module
3. Run: `bash test_cd_detect.sh` - Verify device is detected
4. Run: `bash test_cd_play.sh /dev/sr0` - Test playback
5. Verify audio comes through HiFiBerry speakers

**Status**: ⏳ Ready for testing on Raspberry Pi with physical USB CD module

---

#### **Objectives (Revised):**
- [x] Remove display references from codebase
- [x] Update hardware configuration documents
- [x] Troubleshoot RFID tag detection issue ✓ **RESOLVED - GPIO 8 (Pin 24) was correct CS pin**
- [x] Create RFID reader Python module ✓ Working
- [x] Test RC522 tag reading capability ✓ **TAGS NOW DETECTED**
- [x] Create button handler module ✓ Debouncing and callbacks implemented
- [ ] Test all 4 buttons
- [ ] Implement database mapping for tags → content

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
