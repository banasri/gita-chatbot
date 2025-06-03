# server.py
from fastapi import FastAPI, Query
from query_data import query_rag

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Allow your frontend's origin
origins = [
    "http://127.0.0.1:5500",  # Your frontend server
    "http://localhost:5500",  # Localhost for testing
    "http://localhost:5173",  # Another common local dev server
]

# Allow frontend on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to origins if you want to restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "ChromaDB RAG API is running"}

@app.get("/query")
def run_query(q: str = Query(..., description="The query text")):
    answer = query_rag(q)
    return {"query": q, "response": answer}
from fastapi.responses import JSONResponse