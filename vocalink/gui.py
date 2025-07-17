import customtkinter as ctk
import tkinter as tk
from vocalink.config import AppConfig, save_config
from vocalink.audio import AudioRecorder
from pynput import keyboard
from vocalink.localization import LocalizationManager

class SettingsWindow(ctk.CTkToplevel):
    """Settings window for the application using CustomTkinter."""

    def __init__(self, parent, config: AppConfig, on_save_callback=None, replay_audio_callback=None, localization_manager=None):
        super().__init__(parent)
        self.config = config
        self.on_save_callback = on_save_callback
        self.replay_audio_callback = replay_audio_callback
        self.localization_manager = localization_manager

        self.mic_var = ctk.StringVar() # Use ctk.StringVar
        self.theme_var = ctk.StringVar() # Use ctk.StringVar
        self.hotkey_var = ctk.StringVar() # Use ctk.StringVar
        self.auto_launch_var = ctk.BooleanVar() # Use ctk.BooleanVar
        self.minimize_to_tray_var = ctk.BooleanVar() # Use ctk.BooleanVar
        self.model_var = ctk.StringVar() # Use ctk.StringVar
        self.lang_var = ctk.StringVar() # Use ctk.StringVar
        self.interface_lang_var = ctk.StringVar() # Use ctk.StringVar

        self.title(self.localization_manager.get_string("app_title"))
        self.geometry("800x600") # Increased size for modern layout
        self.resizable(False, False) # Fixed size for now

        # Set default appearance mode and color theme
        ctk.set_appearance_mode("System") # Light or Dark
        ctk.set_default_color_theme("blue") # Themes: blue, dark-blue, green

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.grab_set() # Make the window modal

        self.hotkey_listener = None
        self.recording_hotkey = False
        self.captured_hotkey_keys = set()

        self.create_widgets()
        self.load_current_settings()

    def create_widgets(self):
        """Creates the widgets for the settings window."""
        # Configure grid layout for main window
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # For spacing

        # Sidebar Header
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="VocalInk", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Content Frame (for settings sections)
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Create individual setting frames (not packed yet)
        self.general_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.audio_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.advanced_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self.frames = {
            self.localization_manager.get_string("general_tab"): self.general_frame,
            self.localization_manager.get_string("audio_tab"): self.audio_frame,
            self.localization_manager.get_string("advanced_tab"): self.advanced_frame
        }

        self.create_sidebar_buttons()
        self.create_general_settings()
        self.create_audio_settings()
        self.create_advanced_settings()

        # Buttons Frame at the bottom of the main window
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=1, sticky="se", padx=20, pady=20)
        self.button_frame.grid_columnconfigure(0, weight=1) # For right alignment

        self.save_button = ctk.CTkButton(self.button_frame, text=self.localization_manager.get_string("save_button"), command=self.save_settings, fg_color="#1a73e8", hover_color="#155cb5")
        self.save_button.grid(row=0, column=1, padx=10)

        self.cancel_button = ctk.CTkButton(self.button_frame, text=self.localization_manager.get_string("cancel_button"), command=self.on_closing, fg_color="gray", hover_color="#555555")
        self.cancel_button.grid(row=0, column=2)

        # Display initial frame
        self.show_frame(self.localization_manager.get_string("general_tab"))

    def create_sidebar_buttons(self):
        """Creates the navigation buttons in the sidebar."""
        for i, (text, frame) in enumerate(self.frames.items()):
            button = ctk.CTkButton(self.sidebar_frame, text=text, fg_color="transparent",
                                   command=lambda t=text: self.show_frame(t),
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   hover_color="#3a7ebf",
                                   anchor="w")
            button.grid(row=i+1, column=0, sticky="ew", padx=20, pady=5)

    def show_frame(self, page_name):
        """Shows the selected frame in the content area."""
        frame = self.frames[page_name]
        for f in self.frames.values():
            f.grid_forget() # Hide all frames
        frame.grid(row=0, column=0, sticky="nsew") # Show the selected frame

    def create_general_settings(self):
        """Creates the widgets for the general settings tab."""
        self.general_frame.grid_columnconfigure(1, weight=1)

        # Theme Setting
        theme_label = ctk.CTkLabel(self.general_frame, text=self.localization_manager.get_string("application_theme"), font=ctk.CTkFont(size=16, weight="bold"))
        theme_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.general_frame, text=self.localization_manager.get_string("select_theme")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        theme_menu = ctk.CTkComboBox(
            self.general_frame,
            variable=self.theme_var,
            values=self.get_ctk_themes(),
            state="readonly",
            command=self.apply_theme_preview
        )
        theme_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Interface Language Setting
        lang_label = ctk.CTkLabel(self.general_frame, text=self.localization_manager.get_string("interface_language"), font=ctk.CTkFont(size=16, weight="bold"))
        lang_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.general_frame, text=self.localization_manager.get_string("language")).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.interface_lang_combobox = ctk.CTkComboBox(
            self.general_frame,
            variable=self.interface_lang_var,
            values=self.localization_manager.get_available_languages(),
            state="readonly"
        )
        self.interface_lang_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Hotkey Setting
        hotkey_label = ctk.CTkLabel(self.general_frame, text=self.localization_manager.get_string("global_hotkey"), font=ctk.CTkFont(size=16, weight="bold"))
        hotkey_label.grid(row=4, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.general_frame, text=self.localization_manager.get_string("hotkey_combination")).grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.hotkey_entry = ctk.CTkEntry(self.general_frame, textvariable=self.hotkey_var, state="readonly")
        self.hotkey_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        self.record_hotkey_button = ctk.CTkButton(self.general_frame, text=self.localization_manager.get_string("record_hotkey"), command=self.start_hotkey_recording)
        self.record_hotkey_button.grid(row=5, column=2, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(self.general_frame, text=self.localization_manager.get_string("record_hotkey_tip"),
                     font=ctk.CTkFont(size=10), text_color="gray").grid(row=6, column=0, columnspan=3, padx=10, pady=(0,10), sticky="w")

        # Startup Options
        startup_label = ctk.CTkLabel(self.general_frame, text=self.localization_manager.get_string("startup_options"), font=ctk.CTkFont(size=16, weight="bold"))
        startup_label.grid(row=7, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        self.auto_launch_check = ctk.CTkCheckBox(self.general_frame, text=self.localization_manager.get_string("launch_on_startup"), variable=self.auto_launch_var)
        self.auto_launch_check.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.minimize_to_tray_check = ctk.CTkCheckBox(self.general_frame, text=self.localization_manager.get_string("minimize_to_tray_on_close"), variable=self.minimize_to_tray_var)
        self.minimize_to_tray_check.grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    def create_audio_settings(self):
        """Creates the widgets for the audio settings tab."""
        self.audio_frame.grid_columnconfigure(1, weight=1)

        # Model Size Setting
        model_label = ctk.CTkLabel(self.audio_frame, text=self.localization_manager.get_string("whisper_model"), font=ctk.CTkFont(size=16, weight="bold"))
        model_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.audio_frame, text=self.localization_manager.get_string("model_size")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        model_menu = ctk.CTkComboBox(
            self.audio_frame,
            variable=self.model_var,
            values=["auto", "tiny", "base", "small", "medium", "large"],
            state="readonly"
        )
        model_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.audio_frame, text=self.localization_manager.get_string("model_size_auto_tip"),
                     font=ctk.CTkFont(size=10), text_color="gray").grid(row=2, column=0, columnspan=2, padx=10, pady=(0,10), sticky="w")

        # Microphone Setting
        mic_label = ctk.CTkLabel(self.audio_frame, text=self.localization_manager.get_string("microphone_selection"), font=ctk.CTkFont(size=16, weight="bold"))
        mic_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.audio_frame, text=self.localization_manager.get_string("select_microphone")).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.mic_combobox = ctk.CTkComboBox(
            self.audio_frame,
            variable=self.mic_var,
            state="readonly"
        )
        self.mic_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.populate_microphones()

        # Transcription Language Setting
        lang_label = ctk.CTkLabel(self.audio_frame, text=self.localization_manager.get_string("transcription_language"), font=ctk.CTkFont(size=16, weight="bold"))
        lang_label.grid(row=5, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.audio_frame, text=self.localization_manager.get_string("language")).grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.lang_combobox = ctk.CTkComboBox(
            self.audio_frame,
            variable=self.lang_var,
            values=["en", "es", "fr", "de", "it", "ja", "ko", "zh", "auto"], # Common languages, add more as needed
            state="readonly"
        )
        self.lang_combobox.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.audio_frame, text=self.localization_manager.get_string("language_auto_tip"),
                     font=ctk.CTkFont(size=10), text_color="gray").grid(row=7, column=0, columnspan=2, padx=10, pady=(0,10), sticky="w")

    def create_advanced_settings(self):
        """Creates the widgets for the advanced settings tab."""
        self.advanced_frame.grid_columnconfigure(0, weight=1)
        self.advanced_frame.grid_rowconfigure(1, weight=1) # For text widget expansion

        # Word Replacements Setting
        replacements_label = ctk.CTkLabel(self.advanced_frame, text=self.localization_manager.get_string("word_replacements"), font=ctk.CTkFont(size=16, weight="bold"))
        replacements_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.advanced_frame, text=self.localization_manager.get_string("word_replacements_tip")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.replacements_text = ctk.CTkTextbox(self.advanced_frame, height=150, wrap="word") # Use CTkTextbox
        self.replacements_text.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        ctk.CTkLabel(self.advanced_frame, text=self.localization_manager.get_string("word_replacements_example"),
                     font=ctk.CTkFont(size=10), text_color="gray").grid(row=3, column=0, columnspan=2, padx=10, pady=(0,10), sticky="w")

        # Replay Last Recording Button
        replay_label = ctk.CTkLabel(self.advanced_frame, text=self.localization_manager.get_string("audio_playback"), font=ctk.CTkFont(size=16, weight="bold"))
        replay_label.grid(row=4, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        self.replay_button = ctk.CTkButton(self.advanced_frame, text=self.localization_manager.get_string("replay_last_recording"), command=self.replay_last_audio)
        self.replay_button.grid(row=5, column=0, padx=10, pady=5, sticky="w")

    def load_current_settings(self):
        """Loads the current configuration into the GUI widgets."""
        self.theme_var.set(self.config.theme)
        self.hotkey_var.set(self.config.hotkey)
        self.auto_launch_var.set(self.config.auto_launch)
        self.minimize_to_tray_var.set(self.config.minimize_to_tray)
        self.model_var.set(self.config.model_size)
        self.lang_var.set(self.config.transcription_language)
        self.interface_lang_var.set(self.config.interface_language)

        # Load word replacements
        replacements_str = ""
        for old, new in self.config.word_replacements.items():
            replacements_str += f"{old}={new}\n"
        self.replacements_text.delete("0.0", "end") # Use "0.0" for CTkTextbox
        self.replacements_text.insert("0.0", replacements_str.strip())

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
        self.mic_combobox.configure(values=["Default"] + mics) # Use configure for CTkComboBox
        if not self.mic_var.get(): # Set default if nothing selected
            self.mic_var.set("Default")

    def get_ctk_themes(self):
        """Returns a list of available CustomTkinter themes."""
        return ["blue", "dark-blue", "green"]

    def apply_theme_preview(self, new_theme):
        """Applies the selected theme to the settings window for preview."""
        ctk.set_default_color_theme(new_theme)

    def start_hotkey_recording(self):
        """Starts listening for hotkey input."""
        self.recording_hotkey = True
        self.captured_hotkey_keys.clear()
        self.hotkey_entry.configure(state="normal") # Use configure for CTkEntry
        self.hotkey_entry.delete(0, "end") # Use "end" for CTkEntry
        self.hotkey_entry.insert(0, self.localization_manager.get_string("record_hotkey_tip"))
        self.hotkey_entry.configure(state="readonly")
        self.record_hotkey_button.configure(text=self.localization_manager.get_string("recording_status"), state="disabled") # Use configure for CTkButton

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
        self.hotkey_entry.configure(state="normal")
        self.hotkey_entry.delete(0, "end")
        self.hotkey_entry.insert(0, hotkey_str)
        self.hotkey_entry.configure(state="readonly")
        self.hotkey_var.set(hotkey_str) # Update the StringVar

    def stop_hotkey_recording(self):
        """Stops listening for hotkey input."""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
        self.recording_hotkey = False
        self.record_hotkey_button.configure(text=self.localization_manager.get_string("record_hotkey"), state="normal")

    def save_settings(self):
        """Saves the configuration and closes the window."""
        self.config.theme = self.theme_var.get()
        self.config.hotkey = self.hotkey_var.get()
        self.config.model_size = self.model_var.get()
        self.config.transcription_language = self.lang_var.get()
        self.config.interface_language = self.interface_lang_var.get()

        # Save word replacements
        replacements_dict = {}
        for line in self.replacements_text.get("0.0", "end").strip().split('\n'): # Use "0.0" for CTkTextbox
            if '=' in line:
                old, new = line.split('=', 1)
                replacements_dict[old.strip()] = new.strip()
        self.config.word_replacements = replacements_dict
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

    def replay_last_audio(self):
        """Callback to replay the last recorded audio."""
        if self.replay_audio_callback:
            self.replay_audio_callback()
