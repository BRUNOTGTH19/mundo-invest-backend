from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClienteCreate(BaseModel):
    cliente_nome: str
    cliente_email: EmailStr
    tipo_solicitacao: str
    valor_patrimonio: float

class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: str
    tipo_solicitacao: str
    valor_patrimonio: float
    status: str
    prioridade: Optional[str] = None
    criado_em: datetime

    model_config = {"from_attributes": True}

class WebhookPayload(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: str  # ISO format