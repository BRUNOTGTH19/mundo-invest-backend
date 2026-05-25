from sqlalchemy.orm import Session
from app.models import EventoWebhook

class EventoRepository:
    def __init__(self, db: Session):
        self.db = db

    def existe(self, event_id: str) -> bool:
        return self.db.query(EventoWebhook).filter(EventoWebhook.event_id == event_id).first() is not None

    def registrar(self, event_id: str, card_id: str, cliente_email: str, timestamp: str):
        evento = EventoWebhook(
            event_id=event_id,
            card_id=card_id,
            cliente_email=cliente_email,
            timestamp=timestamp
        )
        self.db.add(evento)
        self.db.commit()