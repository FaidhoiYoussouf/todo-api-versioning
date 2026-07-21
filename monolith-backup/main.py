import os
import sys
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import List

import models
import schemas
from database import engine, get_db

# 12 Factor - Facteur III : configuration par variables d'environnement
load_dotenv()
PORT = int(os.getenv("PORT", 8080))

# Création des tables au démarrage
models.Base.metadata.create_all(bind=engine)

# Initialisation de l'application
app = FastAPI(
    title="Todo API",
    description="API REST de gestion de tâches — ISI SUPTECH M1 IL",
    version="1.0.0"
)

# 12 Factor - Facteur XI : logs vers stdout
def log(message: str):
    print(message, flush=True)

# ── CRUD ──────────────────────────────────────────

# GET /api/v1/todos — Lister toutes les tâches
@app.get("/api/v1/todos", response_model=List[schemas.TodoResponse], status_code=200)
def lister_todos(db: Session = Depends(get_db)):
    log("GET /api/v1/todos")
    return db.query(models.Todo).all()

# POST /api/v1/todos — Créer une tâche
@app.post("/api/v1/todos", response_model=schemas.TodoResponse, status_code=201)
def creer_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    log(f"POST /api/v1/todos - titre: {todo.titre}")
    nouveau = models.Todo(**todo.model_dump())
    db.add(nouveau)
    db.commit()
    db.refresh(nouveau)
    return nouveau

# GET /api/v1/todos/{id} — Récupérer une tâche
@app.get("/api/v1/todos/{todo_id}", response_model=schemas.TodoResponse, status_code=200)
def obtenir_todo(todo_id: int, db: Session = Depends(get_db)):
    log(f"GET /api/v1/todos/{todo_id}")
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    return todo

# PATCH /api/v1/todos/{id} — Modifier une tâche
@app.patch("/api/v1/todos/{todo_id}", response_model=schemas.TodoResponse, status_code=200)
def modifier_todo(todo_id: int, maj: schemas.TodoUpdate, db: Session = Depends(get_db)):
    log(f"PATCH /api/v1/todos/{todo_id}")
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    for champ, valeur in maj.model_dump(exclude_unset=True).items():
        setattr(todo, champ, valeur)
    db.commit()
    db.refresh(todo)
    return todo

# DELETE /api/v1/todos/{id} — Supprimer une tâche
@app.delete("/api/v1/todos/{todo_id}", status_code=204)
def supprimer_todo(todo_id: int, db: Session = Depends(get_db)):
    log(f"DELETE /api/v1/todos/{todo_id}")
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    db.delete(todo)
    db.commit()
    return None

# ── Démarrage ─────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)


@app.get("/health")
def health():
    return {"status": "OK"}
