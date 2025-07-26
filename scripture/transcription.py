from transformers import pipeline
from pydub import AudioSegment
from pydub.utils import make_chunks
import os

# Initialize pipeline only once
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",  # or medium/small
    chunk_length_s=30,
    stride_length_s=5,
    return_timestamps=True
)

def preprocess_audio(audio_path, output_format="wav", sample_rate=16000):
    """Convert and prepare audio for transcription."""
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(sample_rate)
        processed_path = "temp_processed_audio.wav"
        audio.export(processed_path, format=output_format)
        return processed_path
    except Exception as e:
        raise RuntimeError(f"Audio preprocessing failed: {e}")

def transcribe(audio_path):
    """Transcribe audio with error handling and preprocessing."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"{audio_path} not found.")

    processed_path = preprocess_audio(audio_path)

    try:
        result = asr_pipeline(processed_path)
        return result.get("text", ""), result.get("chunks", [])
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}")
    finally:
        if os.path.exists(processed_path):
            os.remove(processed_path)

# # Example usage:
# if __name__ == "__main__":
#     text, timestamps = transcribe("scripture/test_files/preaching-clip.wav")
#     print("Transcript:", text)
#     print("Timestamps:", timestamps)
