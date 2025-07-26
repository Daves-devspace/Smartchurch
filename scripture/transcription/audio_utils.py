import tempfile
from pydub import AudioSegment

def preprocess_audio(input_path: str, sample_rate: int = 16000) -> str:
    """
    Load ANY audio/video file (mp4, mp3, wav, etc.), convert to mono‑16k WAV,
    and return the path to a temp WAV file.
    """
    # pydub will use ffmpeg under the hood to demux.
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(sample_rate)

    # Write out to a safe temp WAV
    fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
    audio.export(tmp_wav, format="wav")
    return tmp_wav


