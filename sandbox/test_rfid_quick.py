#!/usr/bin/env python3
"""
RFID Reader - Quick Test
Simple test to verify RC522 can read RFID tags
"""

import sys
import time

try:
    from mfrc522 import SimpleMFRC522
except ImportError:
    print("Error: mfrc522 library not installed")
    print("Install with: pip3 install --user mfrc522")
    sys.exit(1)

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Error: RPi.GPIO not installed")
    print("Install with: sudo apt-get install python3-rpi.gpio")
    sys.exit(1)

def main():
    print("=" * 50)
    print("RFID Reader - Quick Test")
    print("=" * 50)
    print()
    print("Initializing RC522 reader...")
    
    try:
        reader = SimpleMFRC522()
        print("✓ RC522 initialized successfully")
        print()
        print("Waiting for tags...")
        print("(Hold a tag near the reader)")
        print()
        
        # Read tags for 60 seconds or until user interrupts
        start_time = time.time()
        while time.time() - start_time < 60:
            try:
                print("✓ Attempting to read tag...")
                id, text = reader.read()
                print(f"✓ Tag detected!")
                print(f"  ID: {id}")
                print(f"  Text: {text}")
                print()
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                # Silently ignore read errors and keep waiting
                print("✗ Error reading tag. Keep holding the tag close to the reader.")
                pass
            
            time.sleep(0.1)
        
        print()
        print("✓ Test complete")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Verify RC522 is wired correctly (SPI pins and GPIO 24/25)")
        print("2. Check GPIO pin 24 (CS) and 25 (RST) connections")
        print("3. Ensure RC522 has 3.3V power on pin 1")
        return 1
    
    finally:
        GPIO.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
