from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm import generate_sql
from validator import validate_sql
from db import run_query
import json
import psycopg2

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str

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


@app.get("/layers")
def get_layers():
    rows = run_query("SELECT * FROM layer_metadata")
    return rows

