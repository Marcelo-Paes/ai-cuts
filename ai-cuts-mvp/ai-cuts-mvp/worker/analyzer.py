import json,os

def fallback(segments,amount):
    if not segments:return []
    out=[];i=0
    while i<len(segments) and len(out)<amount:
        start=segments[i]["start"];end=start;texts=[];j=i
        while j<len(segments) and end-start<45:
            end=segments[j]["end"];texts.append(segments[j]["text"]);j+=1
        out.append({"start":round(start,2),"end":round(end,2),"title":"Momento interessante","hook":texts[0] if texts else "Confira este trecho.","reason":"Fallback do MVP; configure OPENAI_API_KEY para análise semântica.","viral_score":max(50,90-len(out)*2)})
        i=max(j,i+1)
    return out

def select_clips(segments,amount):
    key=os.getenv("OPENAI_API_KEY")
    if not key:return fallback(segments,amount)
    from openai import OpenAI
    client=OpenAI(api_key=key)
    transcript="\n".join(f"[{s['start']:.2f}-{s['end']:.2f}] {s['text']}" for s in segments)
    prompt=f'''Você é um editor profissional de vídeos curtos. Selecione até {amount} trechos independentes da transcrição com alto potencial para Shorts/Reels/TikTok. Avalie hook, curiosidade, emoção, surpresa, conflito, história, payoff, utilidade, opinião e potencial de retenção/compartilhamento. Não invente falas. Use timestamps reais. Retorne SOMENTE JSON no formato:
{{"clips":[{{"start":0,"end":10,"title":"título curto","hook":"hook baseado no trecho","reason":"motivo","viral_score":0}}]}}
Transcrição:
{transcript}'''
    r=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-5-mini"),input=prompt)
    data=json.loads(r.output_text)
    raw=data.get("clips",[])
    raw.sort(key=lambda x:float(x.get("viral_score",0)),reverse=True)
    chosen=[]
    for c in raw:
        start,end=float(c["start"]),float(c["end"])
        if end<=start or end-start<8 or end-start>120:continue
        if any(not(end<=x["start"] or start>=x["end"]) for x in chosen):continue
        c["start"],c["end"]=start,end;c["viral_score"]=max(0,min(100,int(c.get("viral_score",0))))
        chosen.append(c)
        if len(chosen)>=amount:break
    return chosen
