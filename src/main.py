
import sys
import os
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pystray
from PIL import Image, ImageDraw
import threading
from src.config import AppConfig, load_config
from src.audio import AudioRecorder
from src.transcriber import Transcriber
from src.hotkey import HotkeyManager, paste_text
from src.gui import SettingsWindow
import tkinter as tk

class VocalInkApp:
    """Main application class for VocalInk."""

    def __init__(self):
        self.config = load_config()
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(self.config.model_size)
        self.hotkey_manager = HotkeyManager(
            self.config.hotkey,
            self.start_recording,
            self.stop_and_transcribe,
        )
        self.tray_icon = self._create_tray_icon()
        self.settings_window = None
        self.exit_event = threading.Event()

    def _create_tray_icon(self):
        """Creates the system tray icon."""
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

    def stop_and_transcribe(self):
        """Stops recording, transcribes the audio, and pastes the text."""
        print("Stopped recording.")
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
            root = tk.Tk()
            root.withdraw()
            self.settings_window = SettingsWindow(root, self.config)

    def exit_app(self):
        """Exits the application."""
        self.hotkey_manager.stop_listening()
        self.tray_icon.stop()
        self.exit_event.set()

    def run(self):
        """Runs the application."""
        self.hotkey_manager.start_listening()
        # Run the tray icon in a separate thread to keep the main thread free
        # for other tasks or to prevent it from blocking.
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        # Keep the main thread alive until the exit event is set
        self.exit_event.wait()

if __name__ == "__main__":
    app = VocalInkApp()
    try:
        app.run()
    except Exception as e:
        print(f"An unhandled error occurred: {e}", flush=True)
