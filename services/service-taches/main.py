import os
from typing import List

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

load_dotenv()

PORT = int(os.getenv("PORT", "8001"))

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Service Tâches",
    description="Microservice de gestion des tâches",
    version="1.0.0"
)

def log(message: str):
    print(f"[SERVICE-TACHES] {message}", flush=True)

@app.get("/")
def accueil():
    return {
        "service": "service-taches",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health")
def health():
    log("GET /health")
    return {
        "service": "service-taches",
        "status": "OK"
    }

@app.get(
    "/api/v1/taches",
    response_model=List[schemas.TodoResponse]
)
def lister_taches(db: Session = Depends(get_db)):
    log("GET /api/v1/taches")
    return db.query(models.Todo).all()

@app.post(
    "/api/v1/taches",
    response_model=schemas.TodoResponse,
    status_code=201
)
def creer_tache(
    tache: schemas.TodoCreate,
    db: Session = Depends(get_db)
):
    log(f"POST /api/v1/taches - titre={tache.titre}")

    nouvelle_tache = models.Todo(**tache.model_dump())

    db.add(nouvelle_tache)
    db.commit()
    db.refresh(nouvelle_tache)

    return nouvelle_tache

@app.get(
    "/api/v1/taches/{tache_id}",
    response_model=schemas.TodoResponse
)
def obtenir_tache(
    tache_id: int,
    db: Session = Depends(get_db)
):
    log(f"GET /api/v1/taches/{tache_id}")

    tache = (
        db.query(models.Todo)
        .filter(models.Todo.id == tache_id)
        .first()
    )

    if not tache:
        raise HTTPException(
            status_code=404,
            detail="Tâche introuvable"
        )

    return tache

@app.patch(
    "/api/v1/taches/{tache_id}",
    response_model=schemas.TodoResponse
)
def modifier_tache(
    tache_id: int,
    modification: schemas.TodoUpdate,
    db: Session = Depends(get_db)
):
    log(f"PATCH /api/v1/taches/{tache_id}")

    tache = (
        db.query(models.Todo)
        .filter(models.Todo.id == tache_id)
        .first()
    )

    if not tache:
        raise HTTPException(
            status_code=404,
            detail="Tâche introuvable"
        )

    donnees = modification.model_dump(exclude_unset=True)

    for champ, valeur in donnees.items():
        setattr(tache, champ, valeur)

    db.commit()
    db.refresh(tache)

    return tache

@app.delete(
    "/api/v1/taches/{tache_id}",
    status_code=204
)
def supprimer_tache(
    tache_id: int,
    db: Session = Depends(get_db)
):
    log(f"DELETE /api/v1/taches/{tache_id}")

    tache = (
        db.query(models.Todo)
        .filter(models.Todo.id == tache_id)
        .first()
    )

    if not tache:
        raise HTTPException(
            status_code=404,
            detail="Tâche introuvable"
        )

    db.delete(tache)
    db.commit()

    return None

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True
    )
