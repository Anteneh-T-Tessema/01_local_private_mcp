from fastapi import FastAPI, Request, Query
from typing import Optional
from pydantic import BaseModel
from db.sqlite_db import SQLiteDB

app = FastAPI()

class UpdateDataRequest(BaseModel):
    id: int
    content: str

@app.put("/update_data")
def update_data(req: UpdateDataRequest):
    db = SQLiteDB()
    conn = db.conn
    with conn:
        cur = conn.execute("UPDATE data SET content = ? WHERE id = ?", (req.content, req.id))
    return {"status": "success", "rows_affected": cur.rowcount}

@app.delete("/delete_data/{data_id}")
def delete_data(data_id: int):
    db = SQLiteDB()
    conn = db.conn
    with conn:
        cur = conn.execute("DELETE FROM data WHERE id = ?", (data_id,))
    return {"status": "success", "rows_affected": cur.rowcount}

@app.get("/search_data")
def search_data(q: str = Query(..., description="Search term")):
    db = SQLiteDB()
    conn = db.conn
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM data WHERE content LIKE ? ORDER BY id ASC", (f"%{q}%",))
    rows = cur.fetchall()
    return {"data": [{"id": row[0], "content": row[1]} for row in rows]}

@app.get("/list_data")
def list_data():
    db = SQLiteDB()
    conn = db.conn
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM data ORDER BY id ASC")
    rows = cur.fetchall()
    return {"data": [{"id": row[0], "content": row[1]} for row in rows]}

@app.get("/tools")
def get_tools():
    return {"tools": ["add_data", "read_data"]}

class AddDataRequest(BaseModel):
    content: str

@app.post("/add_data")
def add_data(req: AddDataRequest):
    db = SQLiteDB()
    db.add_data(req.content)
    return {"status": "success"}

@app.get("/read_data/{data_id}")
def read_data(data_id: int):
    db = SQLiteDB()
    result = db.read_data(data_id)
    if result:
        return {"content": result[0]}
    return {"error": "Not found"}
from fastapi import FastAPI, Request, Query
from typing import Optional
class UpdateDataRequest(BaseModel):
    id: int
    content: str

@app.put("/update_data")
def update_data(req: UpdateDataRequest):
    db = SQLiteDB()
    conn = db.conn
    with conn:
        cur = conn.execute("UPDATE data SET content = ? WHERE id = ?", (req.content, req.id))
    return {"status": "success", "rows_affected": cur.rowcount}

@app.delete("/delete_data/{data_id}")
def delete_data(data_id: int):
    db = SQLiteDB()
    conn = db.conn
    with conn:
        cur = conn.execute("DELETE FROM data WHERE id = ?", (data_id,))
    return {"status": "success", "rows_affected": cur.rowcount}

@app.get("/search_data")
def search_data(q: str = Query(..., description="Search term")):
    db = SQLiteDB()
    conn = db.conn
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM data WHERE content LIKE ? ORDER BY id ASC", (f"%{q}%",))
    rows = cur.fetchall()
    return {"data": [{"id": row[0], "content": row[1]} for row in rows]}

# MCP Server skeleton using FastAPI
from fastapi import FastAPI, Request
from pydantic import BaseModel

from db.sqlite_db import SQLiteDB

app = FastAPI()

@app.get("/list_data")
def list_data():
    db = SQLiteDB()
    conn = db.conn
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM data ORDER BY id ASC")
    rows = cur.fetchall()
    return {"data": [{"id": row[0], "content": row[1]} for row in rows]}

@app.get("/tools")
def get_tools():
    return {"tools": ["add_data", "read_data"]}


class AddDataRequest(BaseModel):
    content: str


@app.post("/add_data")
def add_data(req: AddDataRequest):
    db = SQLiteDB()
    db.add_data(req.content)
    return {"status": "success"}


@app.get("/read_data/{data_id}")
def read_data(data_id: int):
    db = SQLiteDB()
    result = db.read_data(data_id)
    if result:
        return {"content": result[0]}
    return {"error": "Not found"}
