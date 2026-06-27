from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import generate_sql
from validator import validate_sql
from db import run_query
from rag import enrich_place
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class EnrichRequest(BaseModel):
    name: str                      # Arabic or primary name from DB
    name_en: str | None = None     # English name if available
    place_type: str = "place"      # e.g. "university", "mosque", "hospital"
    wikipedia: str | None = None   # OSM wikipedia tag, e.g. "en:Cairo University"
    wikidata: str | None = None    # OSM wikidata tag, e.g. "Q123456"


@app.post("/chat")
def chat(req: ChatRequest):
    sql = generate_sql(req.message)
    valid, reason = validate_sql(sql)
    if not valid:
        raise HTTPException(status_code=400, detail=reason)
    try:
        rows = run_query(sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"sql": sql, "results": rows}


@app.post("/enrich")
async def enrich(req: EnrichRequest):
    """
    RAG endpoint: given a place name (+ optional metadata),
    fetch Wikipedia docs and return a synthesized knowledge card.
    """
    try:
        card = await enrich_place(
            name=req.name,
            name_en=req.name_en,
            place_type=req.place_type,
            wikipedia_tag=req.wikipedia,
            wikidata=req.wikidata,
        )
        return card
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/layers")
def get_layers():
    rows = run_query("SELECT * FROM layer_metadata")
    return rows
