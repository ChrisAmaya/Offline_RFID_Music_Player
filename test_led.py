#!/usr/bin/env python3
"""
LED Testing Script
Test shuffle indicator LED functionality
"""

import sys
import time

try:
    from src.led_handler import LEDHandler
    from config.gpio_config import LED_SHUFFLE
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure you're running from the project root directory with the virtual environment activated")
    sys.exit(1)

def main():
    print("=" * 60)
    print("LED TESTING - Shuffle Indicator")
    print("=" * 60)
    print()
    print(f"LED Configuration:")
    print(f"  Shuffle Indicator LED → GPIO {LED_SHUFFLE}")
    print()
    print("Initializing LED handler...")
    print()
    
    # Create LED handler
    led_handler = LEDHandler()
    
    # Register the shuffle LED (starts OFF)
    led_handler.register_led("shuffle", LED_SHUFFLE, initial_state=False)
    
    print("✓ Shuffle indicator LED registered")
    print()
    print("-" * 60)
    print()
    
    try:
        # Test 1: LED OFF (initial state)
        print("Test 1: LED OFF (initial state)")
        print(f"  State: {led_handler.get_state('shuffle')}")
        time.sleep(1)
        print()
        
        # Test 2: Turn LED ON
        print("Test 2: Turning LED ON...")
        led_handler.on("shuffle")
        print(f"  State: {led_handler.get_state('shuffle')}")
        time.sleep(2)
        print()
        
        # Test 3: Turn LED OFF
        print("Test 3: Turning LED OFF...")
        led_handler.off("shuffle")
        print(f"  State: {led_handler.get_state('shuffle')}")
        time.sleep(2)
        print()
        
        # Test 4: Toggle (OFF → ON)
        print("Test 4: Toggle (OFF → ON)...")
        new_state = led_handler.toggle("shuffle")
        print(f"  New state: {new_state}")
        time.sleep(1)
        print()
        
        # Test 5: Toggle (ON → OFF)
        print("Test 5: Toggle (ON → OFF)...")
        new_state = led_handler.toggle("shuffle")
        print(f"  New state: {new_state}")
        time.sleep(1)
        print()
        
        # Test 6: Rapid toggle (simulate button presses)
        print("Test 6: Rapid toggle (simulating button presses)...")
        for i in range(5):
            new_state = led_handler.toggle("shuffle")
            print(f"  Toggle {i+1}: {new_state}")
            time.sleep(0.3)
        print()
        
        print("-" * 60)
        print()
        print("✓ LED Test complete!")
        print()
        print(f"Final LED state: {'ON' if led_handler.get_state('shuffle') else 'OFF'}")
        
    except KeyboardInterrupt:
        print()
        print("✓ Test interrupted by user")
    
    finally:
        print()
        print("Cleaning up...")
        led_handler.cleanup()
        print("✓ LED test cleanup complete")

if __name__ == "__main__":
    main()
