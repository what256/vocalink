
from faster_whisper import WhisperModel

class Transcriber:
    """Transcribes audio using the faster-whisper library."""

    def __init__(self, model_size="tiny"):
        self.model_size = model_size
        print(f"Initializing Whisper model '{self.model_size}'. This may involve a one-time download and will take a moment...", flush=True)
        # Let WhisperModel handle caching in the default system location.
        # This ensures the model is only downloaded once.
        self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        print("Model loaded successfully.", flush=True)

    def transcribe(self, audio_path):
        """Transcribes the audio file at the given path."""
        segments, _ = self.model.transcribe(audio_path)
        return " ".join([segment.text for segment in segments])
