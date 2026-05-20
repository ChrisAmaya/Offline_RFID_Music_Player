#!/usr/bin/env python3
"""
Button Handler Module
Handles physical button input detection with debouncing
"""

import logging
import threading
import time
from typing import Optional, Callable
from dataclasses import dataclass

try:
    import RPi.GPIO as GPIO
except ImportError:
    raise ImportError("RPi.GPIO library not installed")

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class ButtonEvent:
    """Represents a button press event"""
    button_name: str
    button_id: int
    gpio_pin: int
    press_time: float
    
    def __repr__(self):
        return f"ButtonEvent({self.button_name}, pin={self.gpio_pin}, time={self.press_time:.3f})"


class ButtonHandler:
    """
    Handles physical button input detection
    
    Features:
    - Debouncing to prevent false triggers
    - Event-driven callbacks for button presses
    - Background polling thread
    - Multiple button support
    """
    
    def __init__(self, debounce_ms: int = 50):
        """
        Initialize button handler
        
        Args:
            debounce_ms: Debounce time in milliseconds (default 50ms)
        """
        self.debounce_time = debounce_ms / 1000.0  # Convert to seconds
        self.buttons = {}
        self.callbacks = {}
        self.last_press = {}
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        logger.info(f"ButtonHandler initialized with {debounce_ms}ms debounce")
    
    def register_button(self, button_id: int, gpio_pin: int, button_name: str):
        """
        Register a button
        
        Args:
            button_id: Unique button identifier
            gpio_pin: GPIO pin number (BCM)
            button_name: Human-readable button name
        """
        try:
            GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.buttons[button_id] = {
                "gpio": gpio_pin,
                "name": button_name,
                "state": GPIO.input(gpio_pin)
            }
            self.last_press[button_id] = 0
            logger.info(f"✓ Registered button: {button_name} (ID: {button_id}, GPIO: {gpio_pin})")
        except Exception as e:
            logger.error(f"Failed to register button {button_name} on GPIO {gpio_pin}: {e}")
            raise
    
    def set_button_callback(self, button_id: int, callback: Callable):
        """
        Set callback function for button press
        
        Args:
            button_id: Button identifier
            callback: Function to call when button is pressed (receives ButtonEvent)
        """
        if button_id not in self.buttons:
            logger.warning(f"Button ID {button_id} not registered")
            return
        
        self.callbacks[button_id] = callback
        logger.info(f"Callback registered for button ID {button_id}")
    
    def start(self):
        """Start background button polling thread"""
        if self._running:
            logger.warning("Button handler already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_buttons, daemon=True)
        self._thread.start()
        logger.info("Button handler started")
    
    def stop(self):
        """Stop background polling thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        logger.info("Button handler stopped")
    
    def _poll_buttons(self):
        """Background thread that polls buttons for presses"""
        logger.debug("Button polling thread started")
        
        while self._running:
            try:
                current_time = time.time()
                
                for button_id, button_info in self.buttons.items():
                    gpio_pin = button_info["gpio"]
                    button_name = button_info["name"]
                    
                    # Read current state (buttons are active LOW with pull-up)
                    current_state = GPIO.input(gpio_pin)
                    previous_state = button_info["state"]
                    
                    # Detect falling edge (button press: HIGH → LOW)
                    if current_state == GPIO.LOW and previous_state == GPIO.HIGH:
                        # Check debounce time
                        time_since_last = current_time - self.last_press[button_id]
                        
                        if time_since_last > self.debounce_time:
                            # Valid button press detected
                            event = ButtonEvent(
                                button_name=button_name,
                                button_id=button_id,
                                gpio_pin=gpio_pin,
                                press_time=current_time
                            )
                            
                            # Call registered callback if exists
                            if button_id in self.callbacks:
                                try:
                                    self.callbacks[button_id](event)
                                except Exception as e:
                                    logger.error(f"Error in button callback for {button_name}: {e}")
                            
                            # Update last press time
                            self.last_press[button_id] = current_time
                            logger.debug(f"Button press detected: {button_name}")
                    
                    # Update stored state
                    button_info["state"] = current_state
                
                time.sleep(0.01)  # Poll every 10ms
                
            except Exception as e:
                logger.error(f"Error in button polling loop: {e}")
                break
        
        logger.debug("Button polling thread ended")
    
    def read_buttons_once(self) -> dict:
        """
        Read all button states once (non-blocking)
        
        Returns:
            Dict mapping button_id to pressed (True/False)
        """
        with self._lock:
            states = {}
            for button_id, button_info in self.buttons.items():
                # Button is pressed when GPIO is LOW (active low with pull-up)
                states[button_id] = GPIO.input(button_info["gpio"]) == GPIO.LOW
            return states
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.stop()
        GPIO.cleanup()
        logger.info("ButtonHandler cleanup complete")
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        try:
            self.cleanup()
        except:
            pass
