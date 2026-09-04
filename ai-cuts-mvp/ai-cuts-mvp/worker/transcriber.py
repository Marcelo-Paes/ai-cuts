from pathlib import Path
import subprocess
_model=None

def transcribe_audio(video:Path,workdir:Path):
    global _model
    audio=workdir/"audio.wav"
    subprocess.run(["ffmpeg","-y","-i",str(video),"-vn","-ac","1","-ar","16000",str(audio)],check=True,capture_output=True)
    from faster_whisper import WhisperModel
    if _model is None:_model=WhisperModel("small",device="cpu",compute_type="int8")
    segments,_=_model.transcribe(str(audio),vad_filter=True)
    return [{"start":float(s.start),"end":float(s.end),"text":s.text.strip()} for s in segments]
