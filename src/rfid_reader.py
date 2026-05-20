#!/usr/bin/env python3
"""
RFID Reader Module
Handles reading RFID tags from RC522 reader
"""

import logging
import threading
import time
from typing import Optional, Callable, Tuple
from dataclasses import dataclass

try:
    from mfrc522 import SimpleMFRC522
    import RPi.GPIO as GPIO
except ImportError as e:
    raise ImportError(f"Required library not installed: {e}")

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class RFIDTag:
    """Represents a detected RFID tag"""
    id: int
    text: str
    timestamp: float
    
    def __repr__(self):
        return f"RFIDTag(id={self.id}, text='{self.text}', timestamp={self.timestamp})"


class RFIDReader:
    """
    RFID Reader interface for RC522
    
    Handles continuous tag reading with event callbacks
    """
    
    def __init__(self, cs_pin: int = 8, rst_pin: int = 25):
        """
        Initialize RFID reader
        
        Args:
            cs_pin: GPIO pin for chip select (default: 24)
            rst_pin: GPIO pin for reset (default: 25)
        """
        self.cs_pin = cs_pin
        self.rst_pin = rst_pin
        self.reader = None
        self.running = False
        self.read_thread = None
        
        # Callbacks
        self.on_tag_detected = None
        self.on_read_error = None
        
        # Debouncing
        self.last_tag_id = None
        self.last_tag_time = 0
        self.debounce_time = 1.0  # seconds
        
        logger.info(f"RFIDReader initialized (CS={cs_pin}, RST={rst_pin})")
    
    def connect(self) -> bool:
        """
        Connect to RC522 reader
        
        Returns:
            True if successful, False otherwise
        """
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            self.reader = SimpleMFRC522()
            logger.info("✓ RC522 reader connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to connect RC522: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from RC522 reader
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.running:
                self.stop()
            
            if self.reader:
                self.reader = None
            
            GPIO.cleanup()
            logger.info("✓ RC522 disconnected")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error disconnecting RC522: {e}")
            return False
    
    def set_tag_callback(self, callback: Callable[[RFIDTag], None]):
        """
        Set callback function to be called when a tag is detected
        
        Args:
            callback: Function that takes RFIDTag as argument
        """
        self.on_tag_detected = callback
        logger.debug(f"Tag callback set: {callback.__name__}")
    
    def set_error_callback(self, callback: Callable[[Exception], None]):
        """
        Set callback function to be called on read errors
        
        Args:
            callback: Function that takes Exception as argument
        """
        self.on_read_error = callback
        logger.debug(f"Error callback set: {callback.__name__}")
    
    def start(self):
        """Start continuous tag reading in background thread"""
        if self.running:
            logger.warning("Reader already running")
            return
        
        if not self.reader:
            logger.error("Reader not connected. Call connect() first.")
            return
        
        self.running = True
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        logger.info("✓ RFID reader started")
    
    def stop(self):
        """Stop continuous tag reading"""
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=2)
        logger.info("✓ RFID reader stopped")
    
    def _read_loop(self):
        """
        Continuous reading loop (runs in background thread)
        """
        logger.info("Read loop started")
        
        while self.running:
            try:
                # Attempt to read a tag
                tag_id, text = self.reader.read()
                
                # Check if this is a new tag (debouncing)
                current_time = time.time()
                if (tag_id != self.last_tag_id or 
                    current_time - self.last_tag_time > self.debounce_time):
                    
                    # Create tag object
                    tag = RFIDTag(
                        id=tag_id,
                        text=text.strip() if text else "",
                        timestamp=current_time
                    )
                    
                    # Update debounce state
                    self.last_tag_id = tag_id
                    self.last_tag_time = current_time
                    
                    logger.info(f"Tag detected: {tag}")
                    
                    # Call callback if set
                    if self.on_tag_detected:
                        try:
                            self.on_tag_detected(tag)
                        except Exception as e:
                            logger.error(f"Error in tag callback: {e}")
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.debug(f"Read error (expected if no tag present): {e}")
                
                # Call error callback if set
                if self.on_read_error:
                    try:
                        self.on_read_error(e)
                    except Exception as callback_error:
                        logger.error(f"Error in error callback: {callback_error}")
                
                time.sleep(0.5)
        
        logger.info("Read loop ended")
    
    def read_once(self, timeout: float = 30.0) -> Optional[RFIDTag]:
        """
        Read a single tag (blocking)
        
        Args:
            timeout: Maximum time to wait for a tag in seconds
        
        Returns:
            RFIDTag if successful, None if timeout
        """
        start_time = time.time()
        
        logger.info(f"Waiting for tag (timeout: {timeout}s)...")
        
        while time.time() - start_time < timeout:
            try:
                tag_id, text = self.reader.read()
                
                tag = RFIDTag(
                    id=tag_id,
                    text=text.strip() if text else "",
                    timestamp=time.time()
                )
                
                logger.info(f"Tag read: {tag}")
                return tag
                
            except Exception as e:
                logger.debug(f"Read error: {e}")
                time.sleep(0.1)
        
        logger.warning("Read timeout - no tag detected")
        return None


# Convenience functions
def test_reader():
    """Simple test of RFID reader"""
    logger.basicConfig(level=logging.INFO)
    
    reader = RFIDReader()
    
    # Connect
    if not reader.connect():
        logger.error("Failed to connect to reader")
        return False
    
    # Define callback
    def on_tag(tag):
        logger.info(f"Callback: {tag}")
    
    # Set callback and start
    reader.set_tag_callback(on_tag)
    reader.start()
    
    try:
        # Read for 60 seconds
        time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        reader.stop()
        reader.disconnect()
    
    return True


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    test_reader()
