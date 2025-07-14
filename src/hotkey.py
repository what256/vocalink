
from pynput import keyboard
import pyperclip

class HotkeyManager:
    """Manages global hotkeys for starting and stopping recording."""

    def __init__(self, hotkey_str, on_press_callback, on_release_callback):
        self.hotkey_str = hotkey_str
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback
        self.listener = None
        self.pressed_keys = set()
        self.hotkey_keys = self._parse_hotkey_string(hotkey_str)
        self.hotkey_active = False

    def _parse_hotkey_string(self, hotkey_str):
        """Parses the hotkey string into a set of pynput key objects."""
        keys = set()
        parts = hotkey_str.split('+')
        for part in parts:
            part = part.strip().lower()
            if part.startswith('<') and part.endswith('>'):
                key_name = part[1:-1]
                if key_name == 'ctrl':
                    keys.add(keyboard.Key.ctrl) # Use generic ctrl
                elif key_name == 'shift':
                    keys.add(keyboard.Key.shift) # Use generic shift
                elif key_name == 'alt':
                    keys.add(keyboard.Key.alt) # Use generic alt
                else:
                    try:
                        keys.add(getattr(keyboard.Key, key_name))
                    except AttributeError:
                        keys.add(keyboard.KeyCode.from_char(key_name))
            else:
                keys.add(keyboard.KeyCode.from_char(part))
        return keys

    def _canonicalize_key(self, key):
        if isinstance(key, keyboard.Key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return keyboard.Key.ctrl
            if key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                return keyboard.Key.shift
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                return keyboard.Key.alt
        return key

    def _on_press(self, key):
        """Handles key press events."""
        print(f"Key pressed: {key}", flush=True)
        canonical_key = self._canonicalize_key(key)
        if canonical_key in self.hotkey_keys or canonical_key in {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.Key.alt}:
            self.pressed_keys.add(canonical_key)
        print(f"Pressed keys: {self.pressed_keys}", flush=True)
        print(f"Hotkey keys: {self.hotkey_keys}", flush=True)

        # Check if all hotkey keys are pressed and hotkey was not active
        if all(k in self.pressed_keys for k in self.hotkey_keys) and not self.hotkey_active:
            self.hotkey_active = True
            print("Hotkey activated! Calling on_press_callback.", flush=True)
            self.on_press_callback()

    def _on_release(self, key):
        """Handles key release events."""
        print(f"Key released: {key}", flush=True)
        canonical_key = self._canonicalize_key(key)
        if canonical_key in self.pressed_keys:
            self.pressed_keys.remove(canonical_key)
        print(f"Pressed keys: {self.pressed_keys}", flush=True)
        print(f"Hotkey keys: {self.hotkey_keys}", flush=True)

        # Check if hotkey was active and is no longer fully pressed
        if self.hotkey_active and not all(k in self.pressed_keys for k in self.hotkey_keys):
            self.hotkey_active = False
            print("Hotkey deactivated! Calling on_release_callback.", flush=True)
            self.on_release_callback()

    def start_listening(self):
        """Starts listening for hotkey events."""
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def stop_listening(self):
        """Stops listening for hotkey events."""
        if self.listener:
            self.listener.stop()

def paste_text(text):
    """Pastes the given text using pyperclip."""
    pyperclip.copy(text)
    # Simulate Ctrl+V to paste the text
    keyboard_controller = keyboard.Controller()
    keyboard_controller.press(keyboard.Key.ctrl_l)
    keyboard_controller.press('v')
    keyboard_controller.release('v')
    keyboard_controller.release(keyboard.Key.ctrl_l)
