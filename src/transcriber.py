
from faster_whisper import WhisperModel

class Transcriber:
    """Transcribes audio using the faster-whisper library."""

    def __init__(self, configured_model_size="auto", language="en"):
        self.configured_model_size = configured_model_size # Store the configured size
        self.language = language
        if configured_model_size == "auto":
            self.model_size = "base" # Default to 'base' for auto
        else:
            self.model_size = configured_model_size
        print(f"Initializing Whisper model '{self.model_size}'. This may involve a one-time download and will take a moment...", flush=True)
        # Let WhisperModel handle caching in the default system location.
        # This ensures the model is only downloaded once.
        self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        print("Model loaded successfully.", flush=True)

    def transcribe(self, audio_frames, word_replacements=None):
        """Transcribes the audio file at the given path, applies word replacements, and formats sentences."""
        if word_replacements is None:
            word_replacements = {}

        # Convert audio frames (bytes) to a format faster-whisper can use
        # This might involve writing to a temporary in-memory buffer or a named pipe
        # For simplicity, let's assume audio_frames is a list of bytes objects
        # and we'll join them and pass to transcribe. For real-time, a more advanced
        # approach with a generator or a queue would be needed.
        import numpy as np
        import io
        import soundfile as sf

        # Assuming audio_frames are raw bytes from PyAudio, 16-bit PCM
        audio_data = b"".join(audio_frames)
        audio_np = np.frombuffer(audio_data, dtype=np.int16).flatten().astype(np.float32) / 32768.0

        # faster-whisper's transcribe method can accept a numpy array directly
        if self.language == "auto":
            segments, _ = self.model.transcribe(audio_np, 
                                                vad_filter=True, 
                                                vad_parameters=dict(min_silence_duration_ms=500))
        else:
            segments, _ = self.model.transcribe(audio_np, language=self.language, 
                                                vad_filter=True, 
                                                vad_parameters=dict(min_silence_duration_ms=500))
        
        transcribed_text = []
        for segment in segments:
            text = segment.text
            # Apply word replacements
            for old, new in word_replacements.items():
                text = text.replace(old, new)
            transcribed_text.append(text.strip())

        # Join segments and attempt basic sentence formatting (capitalization, punctuation)
        # faster-whisper often handles basic punctuation, but this adds a layer of formatting.
        formatted_text = ". ".join(s.capitalize() for s in transcribed_text if s)
        if formatted_text and not formatted_text.endswith(('.', '?', '!')):
            formatted_text += "."

        return formatted_text
