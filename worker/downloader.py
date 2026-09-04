from pathlib import Path
import subprocess

def download_video(url:str,workdir:Path)->Path:
    output=workdir/"source.%(ext)s"
    cmd=["yt-dlp","--no-playlist","-f","bv*[height<=1080]+ba/b[height<=1080]","--merge-output-format","mp4","-o",str(output),url]
    subprocess.run(cmd,check=True)
    mp4=workdir/"source.mp4"
    if mp4.exists():return mp4
    candidates=list(workdir.glob("source.*"))
    if not candidates:raise RuntimeError("Vídeo não foi baixado.")
    return candidates[0]
