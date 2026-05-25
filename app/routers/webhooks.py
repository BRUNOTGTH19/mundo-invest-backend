from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import WebhookPayload
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.evento_repo import EventoRepository
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks/pipefy", tags=["Webhooks"])

@router.post("/card-updated")
def card_updated(payload: WebhookPayload, db: Session = Depends(get_db)):
    cliente_repo = ClienteRepository(db)
    evento_repo = EventoRepository(db)
    service = WebhookService(cliente_repo, evento_repo)
    resultado = service.processar(payload)
    if resultado["status"] == "error":
        raise HTTPException(status_code=404, detail=resultado["message"])
    return resultado