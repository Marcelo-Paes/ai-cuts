'use client';

import {useEffect,useState} from 'react';

type Clip={id:string;title:string;hook:string;reason:string;viral_score:number;start:number;end:number;url:string};
type Job={id:string;status:string;progress:number;message:string;clips:Clip[];error?:string};

const WORKER=process.env.NEXT_PUBLIC_WORKER_URL||'http://localhost:8000';

export default function Home(){
  const [url,setUrl]=useState('');
  const [amount,setAmount]=useState(10);
  const [job,setJob]=useState<Job|null>(null);
  const [loading,setLoading]=useState(false);

  async function createJob(){
    setLoading(true);setJob(null);
    try{
      const r=await fetch(`${WORKER}/jobs`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({url,amount})
      });
      const data=await r.json();
      if(!r.ok)throw new Error(data.detail||'Erro ao criar job');
      setJob(data);
    }catch(e){
      setJob({id:'',status:'error',progress:0,message:e instanceof Error?e.message:'Erro',clips:[]});
    }finally{setLoading(false)}
  }

  useEffect(()=>{
    if(!job?.id||['done','error'].includes(job.status))return;
    const timer=setInterval(async()=>{
      const r=await fetch(`${WORKER}/jobs/${job.id}`,{cache:'no-store'});
      if(r.ok)setJob(await r.json());
    },2000);
    return()=>clearInterval(timer);
  },[job?.id,job?.status]);

  return <main>
    <section className="hero">
      <div className="badge">AI VIDEO CLIPPER</div>
      <h1>Vídeos longos em <span>cortes prontos.</span></h1>
      <p>Cole uma URL de um vídeo que você tem direito de processar. A IA encontra os melhores momentos e gera cortes verticais.</p>
      <div className="form">
        <input value={url} onChange={e=>setUrl(e.target.value)} placeholder="Cole a URL..." />
        <select value={amount} onChange={e=>setAmount(Number(e.target.value))}>
          <option value={5}>5 cortes</option>
          <option value={10}>10 cortes</option>
          <option value={30}>30 cortes</option>
        </select>
        <button onClick={createJob} disabled={loading||!url}>{loading?'Enviando...':'Gerar cortes'}</button>
      </div>
      {job&&<div className="job">
        <div className="jobtop"><strong>{job.message}</strong><span>{job.progress}%</span></div>
        <div className="bar"><div style={{width:`${job.progress}%`}}/></div>
        {job.error&&<p className="error">{job.error}</p>}
      </div>}
    </section>

    {job?.status==='done'&&<section className="results">
      <h2>{job.clips.length} cortes gerados</h2>
      <div className="grid">
        {job.clips.map(c=><article className="card" key={c.id}>
          <div className="videoWrap">
            <video controls src={`${WORKER}${c.url}`}/>
            <span className="score">🔥 {c.viral_score}/100</span>
          </div>
          <div className="content">
            <h3>{c.title}</h3>
            <p className="hook">“{c.hook}”</p>
            <p className="muted">{c.reason}</p>
            <a className="download" href={`${WORKER}${c.url}`} download>Baixar MP4</a>
          </div>
        </article>)}
      </div>
    </section>}
  </main>;
}
