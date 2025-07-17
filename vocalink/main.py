import sys
import os
import time
import threading
import subprocess # Import subprocess
import pyaudio # Re-add pyaudio import



import pystray
from PIL import Image, ImageDraw
import wave # Re-add wave import
from vocalink.config import AppConfig, load_config
from vocalink.audio import AudioRecorder
from vocalink.transcriber import Transcriber
from vocalink.hotkey import HotkeyManager, paste_text
from vocalink.gui import SettingsWindow
from vocalink.overlay import RecordingOverlay
from vocalink.localization import LocalizationManager
import customtkinter as ctk # Re-add customtkinter import

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
        self.animation_process = None # Placeholder for the animation process
        self.last_recorded_audio_path = None # Store path to last recorded audio
        self.localization_manager = LocalizationManager(self.config.interface_language) # Initialize localization manager
        self.exit_lock = threading.Lock() # Add a lock for exit synchronization

        # Start hotkey listener and tray icon immediately
        self.hotkey_manager.start_listening()
        print("Starting tray icon in a separate thread.", flush=True)
        threading.Thread(target=self.tray_icon.run).start() # Run tray icon in non-daemon thread
        print("Tray icon thread started.", flush=True)

    def _create_tray_icon(self):
        """Creates the system tray icon."""
        try:
            import importlib.resources as pkg_resources
        except ImportError:
            # Try backported version for older Python versions
            import importlib_resources as pkg_resources

        try:
            # Use importlib.resources to get the path to the asset
            with pkg_resources.files('vocalink.assets').joinpath('logo.png').open('rb') as icon_file:
                image = Image.open(icon_file)
        except FileNotFoundError:
            print("WARNING: Icon file not found. Using a placeholder. Expected at vocalink/assets/logo.png", flush=True)
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
        # Launch animation.py as a separate process
        if self.animation_process is None:
            self.animation_process = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), 'animation.py')])

    def stop_and_transcribe(self):
        """Stops recording, transcribes the audio, and pastes the text."""
        with self.exit_lock:
            print(self.localization_manager.get_string("stopped_recording"), flush=True)
            # Terminate the animation process
            if self.animation_process:
                self.animation_process.terminate()
                self.animation_process = None
            output_filename = "output.wav"
            self.recorder.stop_recording(output_filename)
            self.last_recorded_audio_path = output_filename # Store the path
            try:
                transcription = self.transcriber.transcribe(output_filename, word_replacements=self.config.word_replacements)
                print(f"Transcription: {transcription}")
                if transcription and not transcription.isspace():
                    paste_text(transcription)
                else:
                    print(self.localization_manager.get_string("no_speech_detected"), flush=True)
            except Exception as e:
                print(f"ERROR: Failed to transcribe or paste text: {e}", flush=True)

    def open_settings(self):
        """Schedules opening the settings window on the main thread."""
        self.after(0, self._open_settings_on_main_thread)

    def _open_settings_on_main_thread(self):
        """Opens the settings window on the main thread."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.deiconify()
        else:
            self.settings_window = SettingsWindow(self, self.config, self.apply_settings, self.play_last_recording, self.localization_manager)
            self.settings_window.protocol("WM_DELETE_WINDOW", self.settings_window.on_closing)

    def play_last_recording(self):
        """Plays the last recorded audio file."""
        if not self.last_recorded_audio_path or not os.path.exists(self.last_recorded_audio_path):
            print(self.localization_manager.get_string("no_last_recording"), flush=True)
            return

        print(self.localization_manager.get_string("playing_recording", self.last_recorded_audio_path), flush=True)
        try:
            wf = wave.open(self.last_recorded_audio_path, 'rb')
            p = pyaudio.PyAudio()

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)

            stream.stop_stream()
            stream.close()
            p.terminate()
            wf.close()
            print(self.localization_manager.get_string("finished_playing"), flush=True)
        except Exception as e:
            print(self.localization_manager.get_string("error_playing_audio", e), flush=True)

    def exit_app(self):
        """Exits the application."""
        with self.exit_lock:
            self.hotkey_manager.stop_listening()
            self.tray_icon.stop()
            if self.animation_process:
                self.animation_process.terminate()
                self.animation_process = None
            self.recorder.close() # Terminate PyAudio instance
            self.cleanup_temp_files() # Clean up temporary files
            self.destroy() # Destroy the main CTk window

    def cleanup_temp_files(self):
        """Cleans up temporary files like output.wav and log.txt."""
        temp_files = ["output.wav", "log.txt"]
        for file_name in temp_files:
            file_path = os.path.join(os.path.dirname(__file__), '..', file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Cleaned up: {file_name}", flush=True)
                except Exception as e:
                    print(f"Error cleaning up {file_name}: {e}", flush=True)

    def apply_settings(self):
        """Applies the updated settings to the running application components."""
        # Re-initialize transcriber if model size changed or language changed
        if self.transcriber.configured_model_size != self.config.model_size or self.transcriber.language != self.config.transcription_language:
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

def run():
    app = VocalInkApp()
    try:
        app.mainloop() # Start the CustomTkinter mainloop
    except Exception as e:
        print(f"An unhandled error occurred: {e}", flush=True)

def main():
    run()

if __name__ == "__main__":
    main()