"""FastAPI server for the Pulse RAG agent.

Endpoints:
  GET  /health         -> liveness + corpus size
  GET  /               -> minimal chat UI (single page)
  POST /ask            -> blocking JSON answer {answer, sources}
  POST /ask/stream     -> Server-Sent Events: sources, reasoning, answer, done

Run locally:   uvicorn agent.server:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# Load pulse/.env before anything reads LLM_API_KEY.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from . import core
from .rag import get_retriever

app = FastAPI(title="Pulse RAG Agent", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskBody(BaseModel):
    message: str
    k: int = 6


@app.on_event("startup")
def _warm() -> None:
    get_retriever()  # build the BM25 index at boot, not on first request


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "chunks": len(get_retriever()),
                         "model": os.environ.get("PULSE_LLM_MODEL", "deepseek/deepseek-v4-flash")})


@app.post("/ask")
def ask(body: AskBody) -> JSONResponse:
    ans = core.ask(body.message[:1000], k=body.k)
    return JSONResponse({
        "answer": ans.text,
        "sources": [{"n": i, "citation": s.chunk.citation, "source": s.chunk.source,
                     "score": round(s.score, 3)} for i, s in enumerate(ans.sources, 1)],
    })


@app.post("/ask/stream")
def ask_stream(body: AskBody) -> StreamingResponse:
    def gen():
        try:
            for kind, text in core.ask_stream(body.message[:1000], k=body.k):
                payload = text if kind == "sources" else json.dumps({"text": text})
                yield f"event: {kind}\ndata: {payload}\n\n"
        except Exception as e:  # surface, don't hang the stream
            yield f"event: error\ndata: {json.dumps({'text': str(e)})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache, no-transform",
                                      "X-Accel-Buffering": "no"})


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _UI


_UI = """<!doctype html><html lang=en><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Pulse RAG Agent</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto;background:#0a0b0e;color:#e7e9ee}
.wrap{max-width:760px;margin:0 auto;padding:28px 18px 96px}
h1{font-size:20px;margin:0 0 2px;letter-spacing:-.01em}
.sub{color:#8b93a7;font-size:13px;margin:0 0 22px}
.msg{padding:14px 16px;border-radius:12px;margin:10px 0;white-space:pre-wrap}
.me{background:#16202e;border:1px solid #1f2c3d}
.bot{background:#0f1116;border:1px solid #1b1e26}
.think{color:#6b7280;font-size:12.5px;font-style:italic;border-left:2px solid #2a2f3a;padding:4px 0 4px 10px;margin:6px 0;white-space:pre-wrap}
.src{font-size:12px;color:#7c89a3;margin-top:8px}
.src b{color:#9fb0cc;font-weight:600}
form{position:fixed;bottom:0;left:0;right:0;background:linear-gradient(180deg,transparent,#0a0b0e 30%);padding:18px}
.bar{max-width:760px;margin:0 auto;display:flex;gap:8px}
input{flex:1;padding:13px 15px;border-radius:11px;border:1px solid #232838;background:#0f1116;color:#e7e9ee;font-size:15px}
button{padding:0 18px;border-radius:11px;border:0;background:#34d399;color:#04130c;font-weight:700;cursor:pointer}
button:disabled{opacity:.5;cursor:default}
.dot{color:#34d399}
</style>
<div class=wrap>
<h1><span class=dot>●</span> Pulse RAG Agent</h1>
<p class=sub>Retrieval-augmented Q&A over the Pulse skill — grounded, cited. DeepSeek V4 Flash.</p>
<div id=log></div>
</div>
<form id=f><div class=bar>
<input id=q autocomplete=off placeholder="How does Pulse catch crashes? What's the fee disclosure?">
<button id=s>Ask</button>
</div></form>
<script>
const log=document.getElementById('log'),q=document.getElementById('q'),f=document.getElementById('f'),s=document.getElementById('s');
function el(c,t){const d=document.createElement('div');d.className=c;if(t)d.textContent=t;log.appendChild(d);return d}
f.onsubmit=async e=>{
 e.preventDefault();const m=q.value.trim();if(!m)return;q.value='';s.disabled=true;
 el('msg me',m);
 const bot=el('msg bot');let think=null,ans='',srcLine=null;
 try{
  const r=await fetch('/ask/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
  const rd=r.body.getReader(),dec=new TextDecoder();let buf='';
  for(;;){const{value,done}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});
   let i;while((i=buf.indexOf('\\n\\n'))>=0){const ev=buf.slice(0,i);buf=buf.slice(i+2);
    const mt=ev.match(/^event: (.*)$/m),md=ev.match(/^data: (.*)$/m);if(!mt||!md)continue;
    const kind=mt[1];let data;try{data=JSON.parse(md[1])}catch{data=md[1]}
    if(kind==='sources'){const arr=JSON.parse(md[1]);if(arr.length){srcLine=el('src');srcLine.innerHTML='<b>Sources:</b> '+arr.map(x=>'['+x.n+'] '+x.citation).join(' · ');bot.appendChild(srcLine)}}
    else if(kind==='reasoning'){if(!think)think=el('think');think.textContent+=data.text}
    else if(kind==='answer'){ans+=data.text;bot.textContent=ans;if(srcLine)bot.appendChild(srcLine)}
    else if(kind==='error'){bot.textContent='⚠ '+data.text}
   }}
 }catch(err){bot.textContent='⚠ '+err.message}
 s.disabled=false;q.focus();window.scrollTo(0,document.body.scrollHeight);
};
</script>
</html>"""
