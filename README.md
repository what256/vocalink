🎤 VocalInk

VocalInk is a blazing-fast, privacy-friendly desktop voice-to-text app that transcribes your speech into text in real time and pastes it directly where you’re typing. It works with customizable hotkeys, a minimal tray icon, and runs silently in the background.

🚀 Why VocalInk?

Not everyone can afford expensive commercial tools like Aqua Voice or Otter — VocalInk was built to give everyone free access to real-time speech-to-text transcription with the same power, speed, and convenience, but open-source and offline-first. No subscriptions, no cloud processing, and your data stays on your machine.

⸻

🛠️ Requirements

Before installing, make sure you have:
	•	Python 3.9+
	•	(Optional) Node.js — only required for future overlay features (you’ll be prompted if needed)
	•	Windows 10 or newer (full installer available)
	•	Microphone access enabled

⸻

📦 Installation

Option 1 (easy):
Download the .exe installer from the Releases page and install like any normal app.

Option 2 (advanced):
Install from source:

pip install vocalink


⸻

⚙️ Usage

To start VocalInk:

vocalink

Then press the configured hotkey (default: Ctrl+Shift+V) to begin and stop recording. Your voice will be transcribed instantly and pasted into the currently active window or input field.

⸻

📝 Configuration

After first launch, you’ll find the configuration file here:

~/.config/vocalink/config.json

You can manually adjust your:
	•	Microphone
	•	Hotkey
	•	Auto-launch behavior
	•	Overlay settings (coming soon)

⸻

💡 Features
	•	🔥 Blazing-fast offline transcription (powered by Whisper or faster engines)
	•	⌨️ Global hotkey trigger
	•	📋 Auto-paste into any app (Chrome, Notepad, Discord, etc.)
	•	🖥️ Tray icon + GUI settings
	•	🎯 First-run setup wizard
	•	🔒 No internet required — local only!
	•	🆓 100% free and open-source

⸻

📢 Feedback & Support

If you find a bug, want to suggest features, or just want to say hi — open an issue or reach out on GitHub.