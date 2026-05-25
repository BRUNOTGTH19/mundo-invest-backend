def test_webhook_prioridade_alta(client):
    # Primeiro cria cliente
    client.post("/clientes/", json={
        "cliente_nome": "Maria",
        "cliente_email": "maria@example.com",
        "tipo_solicitacao": "Novo",
        "valor_patrimonio": 300000
    })
    # Webhook simulado
    payload = {
        "event_id": "evt_001",
        "card_id": "card_001",
        "cliente_email": "maria@example.com",
        "timestamp": "2026-05-18T12:00:00Z"
    }
    response = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prioridade"] == "prioridade_alta"
    assert "mutation_enviada" in data

def test_webhook_idempotencia(client):
    # Cria cliente
    client.post("/clientes/", json={
        "cliente_nome": "Pedro",
        "cliente_email": "pedro@example.com",
        "tipo_solicitacao": "Recadastro",
        "valor_patrimonio": 100000
    })
    payload = {
        "event_id": "evt_002",
        "card_id": "card_002",
        "cliente_email": "pedro@example.com",
        "timestamp": "2026-05-18T12:00:00Z"
    }
    # Primeira chamada
    resp1 = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert resp1.status_code == 200
    # Segunda chamada com mesmo event_id
    resp2 = client.post("/webhooks/pipefy/card-updated", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "ignored"