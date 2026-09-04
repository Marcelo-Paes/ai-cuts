from pathlib import Path
import subprocess

def make_clip(video:Path,clip:dict,target:Path):
    start=float(clip["start"]);duration=float(clip["end"])-start
    vf="crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920"
    subprocess.run(["ffmpeg","-y","-ss",str(start),"-i",str(video),"-t",str(duration),"-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-movflags","+faststart",str(target)],check=True,capture_output=True)
