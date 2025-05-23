import whisper

# Load Whisper model once globally
model = whisper.load_model("base")  # use "small" or "medium" if you want better accuracy

def transcribe(audio_path):
    """
    Transcribes a given audio file to text using Whisper.
    Params:
        audio_path (str): Path to the audio file (WAV, MP3, etc.)
    Returns:
        str: Transcribed text
    """
    try:
        result = model.transcribe(audio_path)
        return result.get("text", "").strip()
    except Exception as e:
        print(f"[Whisper Error] Failed to transcribe {audio_path}: {e}")
        return ""
