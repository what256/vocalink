
import sys
import os
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pystray
from PIL import Image, ImageDraw
from src.config import AppConfig, load_config
from src.audio import AudioRecorder
from src.transcriber import Transcriber
from src.hotkey import HotkeyManager, paste_text
from src.gui import SettingsWindow
from src.overlay import RecordingOverlay
import tkinter as tk

class VocalInkApp:
    """Main application class for VocalInk."""

    def __init__(self):
        self.config = load_config()
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(configured_model_size=self.config.model_size)
        self.hotkey_manager = HotkeyManager(
            self.config.hotkey,
            self.start_recording,
            self.stop_and_transcribe,
        )
        self.tray_icon = self._create_tray_icon()
        self.settings_window = None
        self.settings_root = tk.Tk() # Create the Tkinter root for settings
        self.settings_root.withdraw() # Hide it initially
        self.overlay = RecordingOverlay(self.settings_root) # Initialize the overlay
        self.overlay.withdraw() # Hide overlay initially

    def _create_tray_icon(self):
        """Creates the system tray icon."""
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        os.makedirs(assets_dir, exist_ok=True) # Ensure assets directory exists
        icon_path = os.path.join(assets_dir, 'logo.png')

        try:
            image = Image.open(icon_path)
        except FileNotFoundError:
            print(f"Warning: Icon file not found at {icon_path}. Using default icon.")
            image = Image.new("RGB", (64, 64), "black")
            dc = ImageDraw.Draw(image)
            dc.rectangle([0, 0, 64, 64], fill="black")

        menu = pystray.Menu(
            pystray.MenuItem("Settings", self.open_settings),
            pystray.MenuItem("Exit", self.exit_app),
        )
        return pystray.Icon("VocalInk", image, "VocalInk", menu)

    def start_recording(self):
        """Starts the audio recording."""
        print("Started recording...")
        self.recorder.start_recording(self.config.mic_device)
        self.overlay.show_overlay()

    def stop_and_transcribe(self):
        """Stops recording, transcribes the audio, and pastes the text."""
        print("Stopped recording.")
        self.overlay.hide_overlay()
        output_filename = "output.wav"
        self.recorder.stop_recording(output_filename)
        try:
            transcription = self.transcriber.transcribe(output_filename)
            print(f"Transcription: {transcription}")
            if transcription and not transcription.isspace():
                paste_text(transcription)
            else:
                print("No speech detected or transcription was empty.")
        except Exception as e:
            print(f"ERROR: Failed to transcribe or paste text: {e}", flush=True)

    def open_settings(self):
        """Opens the settings window."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.deiconify()
        else:
            self.settings_window = SettingsWindow(self.settings_root, self.config, self.apply_settings)
            self.settings_window.protocol("WM_DELETE_WINDOW", self.settings_window.on_closing)
            # If minimize_to_tray is false, we want to destroy the root when settings window is destroyed
            if not self.config.minimize_to_tray:
                self.settings_window.bind("<Destroy>", lambda e: self.settings_root.destroy())

    def exit_app(self):
        """Exits the application."""
        self.hotkey_manager.stop_listening()
        self.tray_icon.stop()
        self.settings_root.quit() # Terminate the Tkinter mainloop
        self.overlay.destroy() # Destroy the overlay window

    def apply_settings(self):
        """Applies the updated settings to the running application components."""
        # Re-initialize transcriber if model size changed
        if self.transcriber.configured_model_size != self.config.model_size:
            self.transcriber = Transcriber(configured_model_size=self.config.model_size)

        # Re-initialize hotkey manager if hotkey changed
        if self.hotkey_manager.hotkey_str != self.config.hotkey:
            self.hotkey_manager.stop_listening()
            self.hotkey_manager = HotkeyManager(
                self.config.hotkey,
                self.start_recording,
                self.stop_and_transcribe,
            )
            self.hotkey_manager.start_listening()

        # Update the tray icon menu if minimize_to_tray setting changes
        # This part might need more complex logic if the menu itself needs to change dynamically
        # For now, we'll assume the tray icon's behavior is handled by the main app's exit logic.

        print("Settings applied successfully.")

    def run(self):
        """Runs the application."""
        self.hotkey_manager.start_listening()
        # Run the tray icon in a separate thread to keep the main thread free
        # for other tasks or to prevent it from blocking.
        print("Starting tray icon in a separate thread.", flush=True)
        threading.Thread(target=self.tray_icon.run).start() # Run tray icon in non-daemon thread
        print("Tray icon thread started.", flush=True)
        # Keep the main thread alive by running the Tkinter mainloop
        self.settings_root.mainloop()

if __name__ == "__main__":
    app = VocalInkApp()
    try:
        app.run()
    except Exception as e:
        print(f"An unhandled error occurred: {e}", flush=True)
