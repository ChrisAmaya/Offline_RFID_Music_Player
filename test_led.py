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
    print("LED TESTING - Shuffle Indicator (Continuous ON)")
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
        print("Turning LED ON and keeping it on...")
        print("(Press Ctrl+C to stop)")
        print()
        
        # Turn LED on
        led_handler.on("shuffle")
        print(f"LED State: ON")
        print(f"GPIO 27 voltage: Should be 3.3V")
        print()
        
        # Keep it on
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print()
        print()
        print("✓ Test interrupted by user")
    
    finally:
        print()
        print("Cleaning up...")
        led_handler.cleanup()
        print("✓ LED test cleanup complete")

if __name__ == "__main__":
    main()
