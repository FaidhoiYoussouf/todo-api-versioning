from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func

from database import Base

class ConsultationStatistique(Base):
    __tablename__ = "consultations_statistiques"

    id = Column(Integer, primary_key=True, index=True)
    total_taches = Column(Integer, nullable=False)
    taches_terminees = Column(Integer, nullable=False)
    taches_non_terminees = Column(Integer, nullable=False)
    date_consultation = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
