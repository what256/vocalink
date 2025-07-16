

import sys
import os
import time
import threading


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pystray
from PIL import Image, ImageDraw
import pyaudio
from src.config import AppConfig, load_config
from src.audio import AudioRecorder
from src.transcriber import Transcriber
from src.hotkey import HotkeyManager, paste_text
from src.gui import SettingsWindow
from src.overlay import RecordingOverlay
from src.localization import LocalizationManager
import customtkinter as ctk

class VocalInkApp(ctk.CTk):
    """Main application class for VocalInk."""

    def __init__(self):
        super().__init__() # Initialize CTk parent
        self.withdraw() # Hide the main window
        self.config = load_config()
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber(configured_model_size=self.config.model_size, language=self.config.transcription_language)
        self.hotkey_manager = HotkeyManager(
            self.config.hotkey,
            self.start_recording,
            self.stop_and_transcribe,
        )
        self.tray_icon = self._create_tray_icon()
        self.settings_window = None
        self.overlay = RecordingOverlay(self) # Initialize the overlay
        self.localization_manager = LocalizationManager(self.config.interface_language) # Initialize localization manager
        self.exit_lock = threading.Lock() # Add a lock for exit synchronization

        # Start hotkey listener and tray icon immediately
        self.hotkey_manager.start_listening()
        print("Starting tray icon in a separate thread.", flush=True)
        threading.Thread(target=self.tray_icon.run).start() # Run tray icon in non-daemon thread
        print("Tray icon thread started.", flush=True)

    def _create_tray_icon(self):
        """Creates the system tray icon."""
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        os.makedirs(assets_dir, exist_ok=True) # Ensure assets directory exists
        icon_path = os.path.join(assets_dir, 'logo.png')

        try:
            image = Image.open(icon_path)
        except FileNotFoundError:
            print(self.localization_manager.get_string("warning_icon_not_found", icon_path), flush=True)
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
        print(self.localization_manager.get_string("started_recording"), flush=True)
        self.recorder.start_recording(self.config.mic_device)
        self.overlay.show_overlay()

    def stop_and_transcribe(self):
        """Stops recording, transcribes the audio, and pastes the text."""
        with self.exit_lock:
            print(self.localization_manager.get_string("stopped_recording"), flush=True)
            self.overlay.hide_overlay()
            audio_frames = self.recorder.stop_recording()
            transcription = self.transcriber.transcribe(audio_frames, word_replacements=self.config.word_replacements)
            print(f"Transcription: {transcription}")
            if transcription and not transcription.isspace():
                paste_text(transcription)
            else:
                print(self.localization_manager.get_string("no_speech_detected"), flush=True)

    def open_settings(self):
        """Schedules opening the settings window on the main thread."""
        self.after(0, self._open_settings_on_main_thread)

    def _open_settings_on_main_thread(self):
        """Opens the settings window on the main thread."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.deiconify()
        else:
            self.settings_window = SettingsWindow(self, self.config, self.apply_settings, self.localization_manager)
            self.settings_window.protocol("WM_DELETE_WINDOW", self.settings_window.on_closing)

    

    def exit_app(self):
        """Exits the application."""
        with self.exit_lock:
            self.hotkey_manager.stop_listening()
            self.tray_icon.stop()
            self.overlay.hide_overlay()
            self.recorder.close() # Terminate PyAudio instance
            if self.winfo_exists():
                self.destroy() # Destroy the main CTk window
            

    

    def apply_settings(self):
        """Applies the updated settings to the running application components."""
        # Re-initialize transcriber if model size changed or language changed
        if self.transcriber.configured_model_size != self.config.model_size or \
           self.transcriber.language != self.config.transcription_language:
            self.transcriber = Transcriber(configured_model_size=self.config.model_size, language=self.config.transcription_language)

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

        if self.config.interface_language != self.localization_manager.current_language:
            self.localization_manager.load_translations(self.config.interface_language)

        print(self.localization_manager.get_string("settings_applied"), flush=True)

if __name__ == "__main__":
    app = VocalInkApp()
    try:
        app.mainloop() # Start the CustomTkinter mainloop
    except Exception as e:
        print(f"An unhandled error occurred: {e}", flush=True)
