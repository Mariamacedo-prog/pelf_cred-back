from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4

class AnexoRequest(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    image: Optional[str] = None
    base64: Optional[str] = None
    descricao: Optional[str] = None
    nome: Optional[str] = None
    tipo: Optional[str] = None

