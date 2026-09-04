import os,uuid
from pathlib import Path
from fastapi import FastAPI,BackgroundTasks,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,HttpUrl
from downloader import download_video
from transcriber import transcribe_audio
from analyzer import select_clips
from clipper import make_clip

BASE=Path(os.getenv("WORK_DIR","./data"));BASE.mkdir(parents=True,exist_ok=True)
OUT=BASE/"generated";OUT.mkdir(parents=True,exist_ok=True)
app=FastAPI(title="AI Cuts Worker")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
app.mount("/generated",StaticFiles(directory=str(OUT)),name="generated")
jobs={}

class JobRequest(BaseModel):
    url:HttpUrl
    amount:int=10

def run_job(jid,url,amount):
    jobdir=BASE/jid;jobdir.mkdir(parents=True,exist_ok=True)
    try:
        jobs[jid].update(status="processing",progress=5,message="Baixando vídeo...")
        video=download_video(url,jobdir)
        jobs[jid].update(progress=20,message="Transcrevendo áudio...")
        segments=transcribe_audio(video,jobdir)
        jobs[jid].update(progress=55,message="Analisando melhores momentos...")
        clips=select_clips(segments,amount)
        results=[]
        for i,clip in enumerate(clips,1):
            jobs[jid].update(progress=55+int(40*i/max(len(clips),1)),message=f"Renderizando corte {i}/{len(clips)}...")
            filename=f"{jid}_{i:02d}.mp4";target=OUT/filename
            make_clip(video,clip,target)
            results.append({**clip,"id":f"{jid}-{i}","url":f"/generated/{filename}"})
        jobs[jid].update(status="done",progress=100,message="Cortes prontos!",clips=results)
    except Exception as e:
        jobs[jid].update(status="error",progress=0,message="Falha no processamento.",error=str(e))

@app.post("/jobs")
def create_job(req:JobRequest,bg:BackgroundTasks):
    if not 1<=req.amount<=30:raise HTTPException(400,"amount deve estar entre 1 e 30")
    jid=str(uuid.uuid4())
    jobs[jid]={"id":jid,"status":"queued","progress":0,"message":"Job criado...","clips":[]}
    bg.add_task(run_job,jid,str(req.url),req.amount)
    return jobs[jid]

@app.get("/jobs/{job_id}")
def get_job(job_id):
    if job_id not in jobs:raise HTTPException(404,"Job não encontrado")
    return jobs[job_id]
