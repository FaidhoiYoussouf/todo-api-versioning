from pydantic import BaseModel
from typing import Optional

# Schéma pour créer une tâche
class TodoCreate(BaseModel):
    titre: str
    description: Optional[str] = None
    termine: Optional[bool] = False

# Schéma pour modifier une tâche
class TodoUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    termine: Optional[bool] = None

# Schéma pour la réponse (inclut l'id)
class TodoResponse(BaseModel):
    id: int
    titre: str
    description: Optional[str] = None
    termine: bool

    class Config:
        from_attributes = True
