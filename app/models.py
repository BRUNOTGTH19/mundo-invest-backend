from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    tipo_solicitacao = Column(String, nullable=False)
    valor_patrimonio = Column(Float, nullable=False)
    status = Column(String, default="Aguardando Análise")
    prioridade = Column(String, nullable=True)  # será preenchida no webhook
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

class EventoWebhook(Base):
    __tablename__ = "eventos_webhook"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, nullable=False)
    card_id = Column(String, nullable=False)
    cliente_email = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    processado_em = Column(DateTime(timezone=True), server_default=func.now())