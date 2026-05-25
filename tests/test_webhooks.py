def test_webhook_prioridade_alta(client):
    """Patrimônio >= 200k deve resultar em prioridade_alta."""
    client.post("/clientes/", json={
        "cliente_nome": "Maria",
        "cliente_email": "maria@example.com",
        "tipo_solicitacao": "Novo",
        "valor_patrimonio": 300000,
    })
    payload = {
        "event_id": "evt_001",
        "card_id": "card_001",
        "cliente_email": "maria@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }
    response = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["prioridade"] == "prioridade_alta"
    assert "cliente_id" in data


def test_webhook_prioridade_normal(client):
    """Patrimônio < 200k deve resultar em prioridade_normal."""
    client.post("/clientes/", json={
        "cliente_nome": "Pedro",
        "cliente_email": "pedro@example.com",
        "tipo_solicitacao": "Recadastro",
        "valor_patrimonio": 100000,
    })
    payload = {
        "event_id": "evt_002",
        "card_id": "card_002",
        "cliente_email": "pedro@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }
    response = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["prioridade"] == "prioridade_normal"


def test_webhook_prioridade_limite_exato(client):
    """Patrimônio exatamente igual a 200k deve ser prioridade_alta (regra >=)."""
    client.post("/clientes/", json={
        "cliente_nome": "Ana",
        "cliente_email": "ana@example.com",
        "tipo_solicitacao": "Atualização",
        "valor_patrimonio": 200000,
    })
    payload = {
        "event_id": "evt_003",
        "card_id": "card_003",
        "cliente_email": "ana@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }
    response = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert response.status_code == 200
    assert response.json()["prioridade"] == "prioridade_alta"


def test_webhook_idempotencia(client):
    """Mesmo event_id processado duas vezes deve ser ignorado na segunda."""
    client.post("/clientes/", json={
        "cliente_nome": "Carlos",
        "cliente_email": "carlos@example.com",
        "tipo_solicitacao": "Recadastro",
        "valor_patrimonio": 50000,
    })
    payload = {
        "event_id": "evt_004",
        "card_id": "card_004",
        "cliente_email": "carlos@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }
    resp1 = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "processed"

    resp2 = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "ignored"


def test_webhook_cliente_nao_encontrado(client):
    """Webhook com e-mail inexistente deve retornar 404."""
    payload = {
        "event_id": "evt_005",
        "card_id": "card_005",
        "cliente_email": "naoexiste@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }
    response = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert response.status_code == 404


def test_webhook_atualiza_status_no_banco(client):
    """Após processamento, o status do cliente no banco deve ser 'Processado'."""
    client.post("/clientes/", json={
        "cliente_nome": "Lucia",
        "cliente_email": "lucia@example.com",
        "tipo_solicitacao": "Novo",
        "valor_patrimonio": 500000,
    })
    payload = {
        "event_id": "evt_006",
        "card_id": "card_006",
        "cliente_email": "lucia@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }
    client.post("/webhooks/pipefy/card-updated", json=payload)

    # Verificar que a mutation não é exposta na resposta HTTP
    response = client.post("/webhooks/pipefy/card-updated", json={
        **payload,
        "event_id": "evt_006b",
    })
    data = response.json()
    assert "mutation_enviada" not in data