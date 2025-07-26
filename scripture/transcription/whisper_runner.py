# hoisted imports & constants at top
import os, tempfile
from typing import Literal

# heavy HF imports
from pydub import AudioSegment
from transformers import pipeline, WhisperProcessor, WhisperForConditionalGeneration
import torchaudio

# === Constants ===
WHISPER_MODEL = "openai/whisper-small"
CHUNK_SECONDS = 15
STRIDE_SECONDS = 1

# === Pre-load pipeline & models ===
_asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model=WHISPER_MODEL,
    chunk_length_s=CHUNK_SECONDS,
    stride_length_s=STRIDE_SECONDS,
    return_timestamps=False,
    ignore_warning=True
)
_processor = WhisperProcessor.from_pretrained(WHISPER_MODEL)
_model     = WhisperForConditionalGeneration.from_pretrained(WHISPER_MODEL)


def _load_and_prepare(path: str) -> AudioSegment:
    """
    Convert any container (mp4/mp3/wav) to mono 16kHz WAV in memory.
    """
    audio = AudioSegment.from_file(path)
    return audio.set_channels(1).set_frame_rate(16_000)


def transcribe_with_pipeline(path: str) -> str:
    """
    File-based ASR: chunk into WAV segments & feed to HF pipeline.
    """
    audio = _load_and_prepare(path)
    duration = len(audio)
    chunk_ms = CHUNK_SECONDS * 1000
    step_ms  = chunk_ms - (STRIDE_SECONDS * 1000)
    pieces = []
    for start in range(0, duration, step_ms):
        end = min(start + chunk_ms, duration)
        seg = audio[start:end]
        fd, tmp = tempfile.mkstemp(suffix=".wav")
        seg.export(tmp, format="wav")
        try:
            out = _asr_pipeline(tmp)
            pieces.append(out["text"].strip())
        finally:
            os.remove(tmp)
        if end >= duration:
            break
    return " ".join(pieces)


def transcribe_with_generate(path: str) -> str:
    """
    File-based ASR: use model.generate() for shorter audio.
    """
    waveform, sr = torchaudio.load(path)
    inputs = _processor(
        waveform.squeeze().numpy(),
        sampling_rate=sr,
        return_tensors="pt"
    ).input_features
    gen = _model.generate(inputs)
    return _processor.batch_decode(gen, skip_special_tokens=True)[0]


def transcribe(path: str, method: Literal["pipeline", "generate"] = "pipeline") -> str:
    """
    Unified file-based entrypoint.
    """
    if method == "pipeline":
        return transcribe_with_pipeline(path)
    elif method == "generate":
        return transcribe_with_generate(path)
    else:
        raise ValueError("Use 'pipeline' or 'generate'")


def transcribe_live(duration: int = 5, device: str = "cpu") -> str:
    """
    Blocking mic capture for `duration` seconds, then ASR via faster-whisper.
    """
    import sounddevice as sd
    from faster_whisper import WhisperModel

    sr = 16000
    print("🔊 recording mic...")
    audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    model = WhisperModel("small", device=device, compute_type="int8")
    segments, _ = model.transcribe(audio.flatten(), language="en", beam_size=5)
    return " ".join(seg.text.strip() for seg in segments)