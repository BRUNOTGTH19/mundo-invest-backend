import logging

from app.repositories.cliente_repo import ClienteRepository
from app.repositories.evento_repo import EventoRepository
from app.schemas import WebhookPayload
from app.pipefy.mutations import MUTATION_UPDATE_CARD_FIELD

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, cliente_repo: ClienteRepository, evento_repo: EventoRepository):
        self.cliente_repo = cliente_repo
        self.evento_repo = evento_repo

    def processar(self, payload: WebhookPayload) -> dict:
        # Idempotência: ignora eventos já processados
        if self.evento_repo.existe(payload.event_id):
            return {"status": "ignored", "message": "Evento já processado"}

        # Buscar cliente pelo e-mail
        cliente = self.cliente_repo.buscar_por_email(payload.cliente_email)
        if not cliente:
            return {"status": "error", "message": "Cliente não encontrado"}

        # Regra de negócio: prioridade por patrimônio
        prioridade = (
            "prioridade_alta" if cliente.valor_patrimonio >= 200_000
            else "prioridade_normal"
        )

        # Atualizar banco local
        self.cliente_repo.atualizar_status_prioridade(cliente, "Processado", prioridade)

        # Registrar evento para garantir idempotência futura
        self.evento_repo.registrar(
            event_id=payload.event_id,
            card_id=payload.card_id,
            cliente_email=payload.cliente_email,
            timestamp=payload.timestamp,
        )

        # Montar mutation que seria enviada ao Pipefy (simulação)
        # Em produção: POST https://api.pipefy.com/graphql com Authorization: Bearer <token>
        mutation = MUTATION_UPDATE_CARD_FIELD.format(
            card_id=payload.card_id,
            status="Processado",
            prioridade=prioridade,
        )
        # A mutation é apenas logada internamente — não exposta na resposta HTTP
        logger.info("[Pipefy][simulação] mutation para card %s:\n%s", payload.card_id, mutation)

        return {
            "status": "processed",
            "cliente_id": cliente.id,
            "prioridade": prioridade,
        }