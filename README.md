# VocalInk

A free, offline-first desktop dictation assistant that transforms any microphone into a live “type-as-you-speak” engine. Powered by the highly efficient `faster-whisper` library, VocalInk runs as a lightweight system tray application, providing seamless voice-to-text functionality directly into any active text field.

## Features

*   **Real-time Speech-to-Text (STT):** Leverages `faster-whisper` for high-performance, low-latency transcription, enabling a near real-time dictation experience. The application is optimized for speed and accuracy, allowing you to speak naturally and see your words appear almost instantly.

*   **Advanced Global Hotkey Capture:** Activate dictation with a fully customizable global hotkey combination (default: `Ctrl + Shift`). The new settings GUI allows you to record single-key or multi-key hotkeys with ease. Simply press and hold the hotkey to begin recording your voice, and release it to stop recording and trigger the transcription process.

*   **Sleek Recording Overlay:** A modern, always-on-top, pill-shaped overlay, powered by PySide6, appears just above your taskbar when recording. It features a live, red waveform animation that provides subtle visual feedback, fading out smoothly when idle. This non-intrusive design ensures it never steals focus and remains visible even when interacting with other applications.

*   **Clipboard Injection & Auto-Paste:** Once transcription is complete, VocalInk automatically copies the transcribed text to your clipboard and simulates a paste action (`Ctrl+V`). This allows the text to be inserted directly into the currently active text field of any application (e.g., word processors, email clients, web browsers, code editors).

*   **System Tray & Headless Modes:** Runs discreetly in the system tray, consuming minimal system resources. A headless mode is also available for advanced users who prefer command-line operation or integration into custom workflows.

*   **Intelligent Model & Microphone Management:** Automatically detects and utilizes the first available input audio device. Users can easily configure a preferred microphone and select from various Whisper model sizes (e.g., `tiny`, `base`, `small`, `medium`, `large`) or choose an **"Auto"** option for automatic model selection, balancing transcription accuracy and performance according to their system capabilities and needs.

*   **Robust Audio Pipeline:** Features a resilient audio processing pipeline, including a ring-buffer for continuous recording, optional Voice Activity Detection (VAD) for improved silence handling, and automatic stream re-opening to recover from audio input errors.

*   **Persistent Configuration & Modern GUI:** All application settings, including theme, hotkey combination, auto-launch options, and minimize-to-tray behavior, are easily configurable and persist across sessions through a simple `config.json` file and an intuitive, sleek, and professional settings window built with `ttkbootstrap`.

*   **Customizable Tray Icon:** Supports using a custom `logo.png` file in the `assets` folder for the system tray icon.

*   **Cross-Platform Compatibility:** Designed to run seamlessly on major operating systems, including Windows, macOS, and most Linux distributions, requiring Python ≥ 3.10.

*   **Fully Offline Operation:** After the initial download of the chosen Whisper model (which occurs only once), VocalInk operates entirely offline. No audio data or transcribed text ever leaves your local machine, ensuring maximum privacy and security.

## Installation

To get VocalInk up and running on your system, follow these steps:

1.  **Clone the Repository:**
    Open your terminal or command prompt and clone the VocalInk GitHub repository:
    ```bash
    git clone https://github.com/your-username/VocalInk.git
    cd VocalInk
    ```

2.  **Create a Virtual Environment (Recommended):**
    It's highly recommended to create a Python virtual environment to manage dependencies and avoid conflicts with your system's Python packages:
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    *   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    With your virtual environment activated, install all necessary Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Application:**
    Once all dependencies are installed, you can launch VocalInk:
    ```bash
    python src/main.py
    ```
    The application will start and appear as an icon in your system tray.

## Usage

Using VocalInk is straightforward:

1.  **Start Dictation:** Press and hold your configured hotkey (default: `Ctrl + Shift`). The sleek recording overlay will appear, indicating active recording.

2.  **Speak Clearly:** Dictate your text clearly into your microphone. Speak at a natural pace.

3.  **Stop Dictation & Paste:** Release the hotkey. VocalInk will stop recording, process the audio, and automatically paste the transcribed text into the application where your cursor is currently active. The recording overlay will smoothly fade out.

4.  **Access Settings:** Right-click on the VocalInk icon in your system tray to access the context menu. From here, you can:
    *   **Settings:** Open the modern settings window to customize hotkeys, microphone, Whisper model size, UI theme, auto-launch behavior, and more.
    *   **Exit:** Close the VocalInk application.

## Configuration

VocalInk's settings can be adjusted through its graphical settings window, accessible via the system tray icon. These settings are stored in `config.json` in the application's root directory. Key configurable options include:

*   **`model_size`**: Choose your desired Whisper model size (`auto`, `tiny`, `base`, `small`, `medium`, `large`). Larger models offer higher accuracy but require more computational resources and disk space. The `auto` option will select a suitable default.
*   **`mic_device`**: Select your preferred microphone by its index. This ensures VocalInk always uses the correct input device.
*   **`hotkey`**: Customize the global hotkey combination that triggers recording (e.g., `<ctrl>+<alt>+t`). The GUI allows you to record your desired combination.
*   **`theme`**: Change the visual theme of the settings window (uses `ttkbootstrap` themes like `superhero`, `darkly`, `flatly`, etc.).
*   **`auto_launch`**: Enable or disable VocalInk starting automatically with your system.
*   **`minimize_to_tray`**: Control whether the settings window minimizes to the system tray or closes to the taskbar.

## Troubleshooting

*   **Application Not Starting/Crashing:**
    *   Ensure all dependencies are installed (`pip install -r requirements.txt`).
    *   Check your Python version (must be 3.10 or higher).
    *   Review the console output for any error messages. If an error occurs, copy the full traceback and search for solutions or report it.

*   **Transcription Inaccurate or Incomplete:**
    *   **Model Size:** Consider upgrading your `model_size` in the settings (e.g., from `tiny` to `base` or `small`). Larger models are more accurate.
    *   **Microphone Quality:** Ensure your microphone is working correctly and positioned optimally.
    *   **Background Noise:** Minimize background noise in your environment.
    *   **Speaking Pace:** Speak clearly and at a moderate pace.

*   **Text Not Pasting:**
    *   Verify that `pyperclip` is installed and working correctly (you can test it manually in a Python interpreter).
    *   Ensure you have an active text field focused when releasing the hotkey.
    *   Check for any security software or operating system settings that might interfere with simulated keyboard inputs.

*   **Hotkey Not Working:**
    *   Ensure no other application is using the same hotkey combination.
    *   Check the `hotkey` setting in the configuration to ensure it's correctly defined.

## Contributing

We welcome contributions to VocalInk! If you have ideas for new features, bug fixes, or improvements, please feel free to:

*   Fork the repository.
*   Create a new branch for your changes.
*   Submit a pull request with a clear description of your modifications.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
