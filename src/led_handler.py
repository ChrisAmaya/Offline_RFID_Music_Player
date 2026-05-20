#!/usr/bin/env python3
"""
LED Handler Module
Handles status indicator LEDs (e.g., shuffle status, play status)
"""

import logging
from typing import Dict

try:
    import RPi.GPIO as GPIO
except ImportError:
    raise ImportError("RPi.GPIO library not installed")

# Setup logging
logger = logging.getLogger(__name__)


class LEDHandler:
    """
    Handles status indicator LEDs
    
    Features:
    - Simple on/off control
    - Toggle functionality
    - State tracking
    """
    
    def __init__(self):
        """Initialize LED handler"""
        self.leds = {}
        self.states = {}
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        logger.info("LEDHandler initialized")
    
    def register_led(self, led_id: str, gpio_pin: int, initial_state: bool = False):
        """
        Register an LED
        
        Args:
            led_id: Unique LED identifier (e.g., "shuffle")
            gpio_pin: GPIO pin number (BCM)
            initial_state: Initial state (True=on, False=off)
        """
        try:
            GPIO.setup(gpio_pin, GPIO.OUT)
            self.leds[led_id] = gpio_pin
            self.states[led_id] = initial_state
            
            # Set initial state
            GPIO.output(gpio_pin, GPIO.HIGH if initial_state else GPIO.LOW)
            
            logger.info(f"✓ Registered LED: {led_id} on GPIO {gpio_pin} (initial: {'ON' if initial_state else 'OFF'})")
        except Exception as e:
            logger.error(f"Failed to register LED {led_id} on GPIO {gpio_pin}: {e}")
            raise
    
    def on(self, led_id: str):
        """Turn LED on"""
        if led_id not in self.leds:
            logger.warning(f"LED {led_id} not registered")
            return False
        
        try:
            GPIO.output(self.leds[led_id], GPIO.HIGH)
            self.states[led_id] = True
            logger.debug(f"LED {led_id} turned ON")
            return True
        except Exception as e:
            logger.error(f"Error turning on LED {led_id}: {e}")
            return False
    
    def off(self, led_id: str):
        """Turn LED off"""
        if led_id not in self.leds:
            logger.warning(f"LED {led_id} not registered")
            return False
        
        try:
            GPIO.output(self.leds[led_id], GPIO.LOW)
            self.states[led_id] = False
            logger.debug(f"LED {led_id} turned OFF")
            return True
        except Exception as e:
            logger.error(f"Error turning off LED {led_id}: {e}")
            return False
    
    def toggle(self, led_id: str) -> bool:
        """
        Toggle LED state
        
        Args:
            led_id: LED identifier
            
        Returns:
            New state (True=on, False=off)
        """
        if led_id not in self.leds:
            logger.warning(f"LED {led_id} not registered")
            return False
        
        current_state = self.states[led_id]
        if current_state:
            self.off(led_id)
            return False
        else:
            self.on(led_id)
            return True
    
    def set_state(self, led_id: str, state: bool):
        """
        Set LED to specific state
        
        Args:
            led_id: LED identifier
            state: Desired state (True=on, False=off)
        """
        if state:
            self.on(led_id)
        else:
            self.off(led_id)
    
    def get_state(self, led_id: str) -> bool:
        """
        Get current LED state
        
        Args:
            led_id: LED identifier
            
        Returns:
            Current state (True=on, False=off)
        """
        return self.states.get(led_id, False)
    
    def get_all_states(self) -> Dict[str, bool]:
        """Get all LED states"""
        return self.states.copy()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup()
        logger.info("LEDHandler cleanup complete")
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        try:
            self.cleanup()
        except:
            pass
