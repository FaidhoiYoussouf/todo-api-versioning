import logging
import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import ConsultationStatistique

load_dotenv()

PORT = int(os.getenv("PORT", "8002"))
SERVICE_TACHES_URL = os.getenv(
    "SERVICE_TACHES_URL",
    "http://127.0.0.1:8001"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Service Statistiques",
    version="1.0.0"
)


@app.get("/")
def accueil():
    return {
        "service": "service-statistiques",
        "message": "Microservice de statistiques opérationnel"
    }


@app.get("/health")
def health():
    return {
        "service": "service-statistiques",
        "status": "OK"
    }


@app.get("/api/v1/statistiques")
def obtenir_statistiques(db: Session = Depends(get_db)):
    try:
        response = requests.get(
            f"{SERVICE_TACHES_URL}/api/v1/taches",
            timeout=3
        )

        response.raise_for_status()
        taches = response.json()

        total_taches = len(taches)

        taches_terminees = sum(
            1 for tache in taches
            if tache.get("termine") is True
        )

        taches_non_terminees = total_taches - taches_terminees

        consultation = ConsultationStatistique(
            total_taches=total_taches,
            taches_terminees=taches_terminees,
            taches_non_terminees=taches_non_terminees
        )

        db.add(consultation)
        db.commit()
        db.refresh(consultation)

        logger.info(
            "Statistiques calculées : total=%s, terminées=%s, non terminées=%s",
            total_taches,
            taches_terminees,
            taches_non_terminees
        )

        return {
            "service": "service-statistiques",
            "source": "service-taches",
            "total_taches": total_taches,
            "taches_terminees": taches_terminees,
            "taches_non_terminees": taches_non_terminees
        }

    except requests.Timeout:
        logger.error("Délai dépassé lors de l'appel au service-taches")

        return {
            "service": "service-statistiques",
            "status": "dégradé",
            "message": "Le service-taches ne répond pas dans le délai prévu",
            "total_taches": 0,
            "taches_terminees": 0,
            "taches_non_terminees": 0
        }

    except requests.RequestException as erreur:
        logger.error(
            "Erreur de communication avec service-taches : %s",
            erreur
        )

        raise HTTPException(
            status_code=503,
            detail="Le service-taches est indisponible"
        )


@app.get("/api/v1/historique")
def obtenir_historique(db: Session = Depends(get_db)):
    consultations = (
        db.query(ConsultationStatistique)
        .order_by(ConsultationStatistique.id.desc())
        .all()
    )

    return [
        {
            "id": consultation.id,
            "total_taches": consultation.total_taches,
            "taches_terminees": consultation.taches_terminees,
            "taches_non_terminees": consultation.taches_non_terminees,
            "date_consultation": consultation.date_consultation
        }
        for consultation in consultations
    ]


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )
