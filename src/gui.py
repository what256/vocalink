import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from src.config import AppConfig, save_config
from src.audio import AudioRecorder
from pynput import keyboard # Import pynput for hotkey recording

class SettingsWindow(tk.Toplevel):
    """Settings window for the application."""

    def __init__(self, parent, config: AppConfig, on_save_callback=None):
        super().__init__(parent)
        self.config = config
        self.on_save_callback = on_save_callback
        self.mic_var = tk.StringVar() # Initialize mic_var here
        self.title("VocalInk Settings")
        self.geometry("550x500") # Adjusted size for more modern layout
        self.style = ttkb.Style(theme=self.config.theme)

        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close

        self.create_widgets()
        self.load_current_settings()

        self.hotkey_listener = None
        self.recording_hotkey = False
        self.captured_hotkey_keys = set()

    def create_widgets(self):
        """Creates the widgets for the settings window."""
        # Main container frame with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(pady=10, fill="both", expand=True)

        self.general_frame = ttk.Frame(self.notebook, padding=15)
        self.audio_frame = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.general_frame, text="General")
        self.notebook.add(self.audio_frame, text="Audio")

        self.create_general_settings()
        self.create_audio_settings()

        # Buttons Frame at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0), fill="x")

        self.save_button = ttk.Button(button_frame, text="Save", command=self.save_settings, bootstyle="success")
        self.save_button.pack(side="right", padx=5)

        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_closing, bootstyle="danger")
        self.cancel_button.pack(side="right", padx=5)

    def create_general_settings(self):
        """Creates the widgets for the general settings tab."""
        # Theme Setting
        theme_labelframe = ttk.LabelFrame(self.general_frame, text="Application Theme", padding=10)
        theme_labelframe.pack(fill="x", pady=10)

        ttk.Label(theme_labelframe, text="Select Theme:", bootstyle="inverse-light").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = tk.StringVar()
        theme_menu = ttk.Combobox(
            theme_labelframe,
            textvariable=self.theme_var,
            values=self.style.theme_names(),
            state="readonly",
            bootstyle="info"
        )
        theme_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        theme_menu.bind("<<ComboboxSelected>>", self.apply_theme_preview)
        theme_labelframe.columnconfigure(1, weight=1)

        # Hotkey Setting
        hotkey_labelframe = ttk.LabelFrame(self.general_frame, text="Global Hotkey", padding=10)
        hotkey_labelframe.pack(fill="x", pady=10)

        ttk.Label(hotkey_labelframe, text="Hotkey Combination:", bootstyle="inverse-light").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hotkey_var = tk.StringVar()
        self.hotkey_entry = ttk.Entry(hotkey_labelframe, textvariable=self.hotkey_var, state="readonly", bootstyle="primary")
        self.hotkey_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.record_hotkey_button = ttk.Button(hotkey_labelframe, text="Record Hotkey", command=self.start_hotkey_recording, bootstyle="info-outline")
        self.record_hotkey_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        hotkey_labelframe.columnconfigure(1, weight=1)

        # Startup Options
        startup_labelframe = ttk.LabelFrame(self.general_frame, text="Startup Options", padding=10)
        startup_labelframe.pack(fill="x", pady=10)

        self.auto_launch_var = tk.BooleanVar()
        auto_launch_check = ttk.Checkbutton(startup_labelframe, text="Launch VocalInk on system startup", variable=self.auto_launch_var, bootstyle="round-toggle")
        auto_launch_check.pack(anchor="w", pady=5)

        self.minimize_to_tray_var = tk.BooleanVar()
        minimize_to_tray_check = ttk.Checkbutton(startup_labelframe, text="Minimize settings window to system tray on close", variable=self.minimize_to_tray_var, bootstyle="round-toggle")
        minimize_to_tray_check.pack(anchor="w", pady=5)

    def create_audio_settings(self):
        """Creates the widgets for the audio settings tab."""
        # Model Size Setting
        model_labelframe = ttk.LabelFrame(self.audio_frame, text="Whisper Model", padding=10)
        model_labelframe.pack(fill="x", pady=10)

        ttk.Label(model_labelframe, text="Model Size:", bootstyle="inverse-light").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.model_var = tk.StringVar()
        model_menu = ttk.Combobox(
            model_labelframe,
            textvariable=self.model_var,
            values=["auto", "tiny", "base", "small", "medium", "large"],
            state="readonly",
            bootstyle="info"
        )
        model_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        model_labelframe.columnconfigure(1, weight=1)

        # Microphone Setting
        mic_labelframe = ttk.LabelFrame(self.audio_frame, text="Microphone Selection", padding=10)
        mic_labelframe.pack(fill="x", pady=10)

        ttk.Label(mic_labelframe, text="Select Microphone:", bootstyle="inverse-light").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.mic_combobox = ttk.Combobox(
            mic_labelframe,
            textvariable=self.mic_var,
            state="readonly",
            bootstyle="info"
        )
        self.mic_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.populate_microphones()
        mic_labelframe.columnconfigure(1, weight=1)

    def load_current_settings(self):
        """Loads the current configuration into the GUI widgets."""
        self.theme_var.set(self.config.theme)
        self.hotkey_var.set(self.config.hotkey)
        self.auto_launch_var.set(self.config.auto_launch)
        self.minimize_to_tray_var.set(self.config.minimize_to_tray)
        self.model_var.set(self.config.model_size)

        if self.config.mic_device is not None:
            recorder = AudioRecorder()
            mics = recorder.list_microphones()
            if self.config.mic_device < len(mics):
                self.mic_var.set(mics[self.config.mic_device])
            else:
                self.mic_var.set("Default") # Fallback if index is out of range
        else:
            self.mic_var.set("Default")

    def populate_microphones(self):
        """Populates the microphone combobox with available devices."""
        recorder = AudioRecorder()
        mics = recorder.list_microphones()
        self.mic_combobox['values'] = ["Default"] + mics
        if not self.mic_var.get(): # Set default if nothing selected
            self.mic_var.set("Default")

    def apply_theme_preview(self, event=None):
        """Applies the selected theme to the settings window for preview."""
        selected_theme = self.theme_var.get()
        self.style.theme_use(selected_theme)

    def start_hotkey_recording(self):
        """Starts listening for hotkey input."""
        self.recording_hotkey = True
        self.captured_hotkey_keys.clear()
        self.hotkey_entry.config(state="normal")
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, "Press your hotkey combination...")
        self.hotkey_entry.config(state="readonly")
        self.record_hotkey_button.config(text="Recording...", state="disabled", bootstyle="warning")

        # Start a global listener for key presses
        self.hotkey_listener = keyboard.Listener(
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release
        )
        self.hotkey_listener.start()

    def _on_hotkey_press(self, key):
        """Callback for hotkey press events during recording."""
        if self.recording_hotkey:
            try:
                # Canonicalize key to handle left/right modifiers
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.captured_hotkey_keys.add(keyboard.Key.ctrl)
                elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                    self.captured_hotkey_keys.add(keyboard.Key.shift)
                elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self.captured_hotkey_keys.add(keyboard.Key.alt)
                elif isinstance(key, keyboard.KeyCode):
                    self.captured_hotkey_keys.add(key.char)
                else:
                    self.captured_hotkey_keys.add(key)
            except AttributeError:
                # Handle special keys without .char attribute
                self.captured_hotkey_keys.add(key)

            self.update_hotkey_display()

    def _on_hotkey_release(self, key):
        """Callback for hotkey release events during recording."""
        if self.recording_hotkey:
            # Stop recording after the first key is released, or after a short delay if multiple keys are pressed
            # For simplicity, we'll stop after any key release for now.
            # A more robust solution would involve a timer or checking if all pressed keys are released.
            self.stop_hotkey_recording()

    def update_hotkey_display(self):
        """Updates the hotkey entry field with the captured keys."""
        display_keys = []
        # Order modifiers first for consistent display
        if keyboard.Key.ctrl in self.captured_hotkey_keys:
            display_keys.append("<ctrl>")
        if keyboard.Key.shift in self.captured_hotkey_keys:
            display_keys.append("<shift>")
        if keyboard.Key.alt in self.captured_hotkey_keys:
            display_keys.append("<alt>")

        for k in self.captured_hotkey_keys:
            if k not in {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.Key.alt}:
                if isinstance(k, keyboard.KeyCode) and k.char:
                    display_keys.append(k.char)
                elif isinstance(k, keyboard.Key):
                    display_keys.append(f"<{str(k).split('.')[-1]}>")

        hotkey_str = "+".join(display_keys)
        self.hotkey_entry.config(state="normal")
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, hotkey_str)
        self.hotkey_entry.config(state="readonly")
        self.hotkey_var.set(hotkey_str) # Update the StringVar

    def stop_hotkey_recording(self):
        """Stops listening for hotkey input."""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
        self.recording_hotkey = False
        self.record_hotkey_button.config(text="Record Hotkey", state="normal", bootstyle="info")

    def save_settings(self):
        """Saves the configuration and closes the window."""
        self.config.theme = self.theme_var.get()
        self.config.hotkey = self.hotkey_var.get()
        self.config.model_size = self.model_var.get()
        self.config.auto_launch = self.auto_launch_var.get()
        self.config.minimize_to_tray = self.minimize_to_tray_var.get()

        mic_selection = self.mic_var.get()
        if mic_selection == "Default":
            self.config.mic_device = None
        else:
            recorder = AudioRecorder()
            mics = recorder.list_microphones()
            try:
                self.config.mic_device = mics.index(mic_selection)
            except ValueError:
                self.config.mic_device = None # Fallback if mic name not found

        save_config(self.config)
        if self.on_save_callback:
            self.on_save_callback()
        self.destroy()

    def on_closing(self):
        """Handles the window closing event."""
        # If recording hotkey, stop it
        if self.recording_hotkey:
            self.stop_hotkey_recording()

        if self.config.minimize_to_tray:
            self.withdraw() # Hide the window instead of destroying it
        else:
            self.destroy()