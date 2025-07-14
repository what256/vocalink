
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from src.config import AppConfig, save_config
from src.audio import AudioRecorder

class SettingsWindow(tk.Toplevel):
    """Settings window for the application."""

    def __init__(self, parent, config: AppConfig):
        super().__init__(parent)
        self.config = config
        self.title("VocalInk Settings")
        self.geometry("400x300")
        ttkb.Style(theme=self.config.theme)

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the settings window."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.general_frame = ttk.Frame(self.notebook)
        self.audio_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.general_frame, text="General")
        self.notebook.add(self.audio_frame, text="Audio")

        self.create_general_settings()
        self.create_audio_settings()

        self.save_button = ttk.Button(self, text="Save", command=self.save_and_close)
        self.save_button.pack(pady=10)

    def create_general_settings(self):
        """Creates the widgets for the general settings tab."""
        # Theme
        theme_label = ttk.Label(self.general_frame, text="Theme:")
        theme_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_menu = ttk.Combobox(
            self.general_frame,
            textvariable=self.theme_var,
            values=ttkb.Style().theme_names(),
        )
        theme_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Hotkey
        hotkey_label = ttk.Label(self.general_frame, text="Hotkey:")
        hotkey_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.hotkey_var = tk.StringVar(value=self.config.hotkey)
        hotkey_entry = ttk.Entry(self.general_frame, textvariable=self.hotkey_var)
        hotkey_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    def create_audio_settings(self):
        """Creates the widgets for the audio settings tab."""
        # Model Size
        model_label = ttk.Label(self.audio_frame, text="Model Size:")
        model_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.model_var = tk.StringVar(value=self.config.model_size)
        model_menu = ttk.Combobox(
            self.audio_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
        )
        model_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Microphone
        mic_label = ttk.Label(self.audio_frame, text="Microphone:")
        mic_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.mic_var = tk.StringVar(value=str(self.config.mic_device) if self.config.mic_device is not None else "Default")
        recorder = AudioRecorder()
        mics = recorder.list_microphones()
        mic_menu = ttk.Combobox(
            self.audio_frame,
            textvariable=self.mic_var,
            values=["Default"] + mics,
        )
        mic_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    def save_and_close(self):
        """Saves the configuration and closes the window."""
        self.config.theme = self.theme_var.get()
        self.config.hotkey = self.hotkey_var.get()
        self.config.model_size = self.model_var.get()
        mic_selection = self.mic_var.get()
        if mic_selection == "Default":
            self.config.mic_device = None
        else:
            recorder = AudioRecorder()
            mics = recorder.list_microphones()
            self.config.mic_device = mics.index(mic_selection)

        save_config(self.config)
        self.destroy()
