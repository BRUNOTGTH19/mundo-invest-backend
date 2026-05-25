from app.repositories.cliente_repo import ClienteRepository
from app.repositories.evento_repo import EventoRepository
from app.schemas import WebhookPayload
from app.pipefy.mutations import MUTATION_UPDATE_CARD_FIELD

class WebhookService:
    def __init__(self, cliente_repo: ClienteRepository, evento_repo: EventoRepository):
        self.cliente_repo = cliente_repo
        self.evento_repo = evento_repo

    def processar(self, payload: WebhookPayload) -> dict:
        # Idempotência
        if self.evento_repo.existe(payload.event_id):
            return {"status": "ignored", "message": "Evento já processado"}

        # Buscar cliente
        cliente = self.cliente_repo.buscar_por_email(payload.cliente_email)
        if not cliente:
            return {"status": "error", "message": "Cliente não encontrado"}

        # Regra de prioridade
        prioridade = "prioridade_alta" if cliente.valor_patrimonio >= 200_000 else "prioridade_normal"

        # Atualizar banco local
        self.cliente_repo.atualizar_status_prioridade(cliente, "Processado", prioridade)

        # Registrar evento (idempotência)
        self.evento_repo.registrar(
            event_id=payload.event_id,
            card_id=payload.card_id,
            cliente_email=payload.cliente_email,
            timestamp=payload.timestamp
        )

        # Simular envio da mutation ao Pipefy
        mutation = MUTATION_UPDATE_CARD_FIELD.format(
            card_id=payload.card_id,
            status="Processado",
            prioridade=prioridade
        )

        return {
            "status": "processed",
            "cliente_id": cliente.id,
            "prioridade": prioridade,
            "mutation_enviada": mutation
        }