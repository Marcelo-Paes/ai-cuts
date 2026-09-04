# AI Cuts MVP

Projeto inicial de um SaaS de cortes com frontend Next.js e worker Python.

Frontend: pode ser hospedado na Vercel.
Worker: deve rodar em servidor separado porque FFmpeg, Whisper e renderização são processos pesados.

Use somente vídeos que você tenha autorização para processar e respeite os termos do serviço de origem.

## Rodar
Frontend:
    cd frontend
    npm install
    cp .env.example .env.local
    npm run dev

Worker:
    cd worker
    python -m venv .venv
    pip install -r requirements.txt
    cp .env.example .env
    uvicorn main:app --reload --port 8000

É necessário FFmpeg instalado. Com OPENAI_API_KEY, a seleção dos cortes usa IA.
Sem chave, o worker usa um fallback simples.

Este MVP usa memória e disco local. Para produção, use PostgreSQL, storage S3/R2/Supabase e uma fila persistente.
