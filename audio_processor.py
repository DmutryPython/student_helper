from transformers import pipeline
import librosa
import config


class AudioProcessor:
    def __init__(self):
        self.transcriber = pipeline(
            "automatic-speech-recognition",
            model=config.WHISPER_MODEL
        )

    def transcribe_audio(self, audio_path: str) -> str:
        """Транскрибация аудио в текст"""
        audio, sr = librosa.load(audio_path, sr=16000)
        result = self.transcriber({"raw": audio, "sampling_rate": sr})
        return result["text"]

