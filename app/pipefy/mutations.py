# Estas strings seguem exatamente a documentação oficial do Pipefy
# Pesquisadas em: https://api-docs.pipefy.com/reference/mutations/createCard/
# e https://api-docs.pipefy.com/reference/mutations/updateCardField/

MUTATION_CREATE_CARD = """
mutation {{
  createCard(input: {{
    pipe_id: "PIPE_ID_DO_PROJETO",
    fields_attributes: [
      {{field_id: "nome_do_cliente", field_value: "{nome}"}},
      {{field_id: "email_do_cliente", field_value: "{email}"}},
      {{field_id: "patrimonio", field_value: "{patrimonio}"}}
    ]
  }}) {{
    card {{
      id
      title
    }}
  }}
}}
"""

MUTATION_UPDATE_CARD_FIELD = """
mutation {{
  update_status: updateCardField(input: {{
    card_id: "{card_id}",
    field_id: "status_do_cliente",
    new_value: "{status}"
  }}) {{
    card {{
      id
    }}
  }}
  update_prioridade: updateCardField(input: {{
    card_id: "{card_id}",
    field_id: "prioridade",
    new_value: "{prioridade}"
  }}) {{
    card {{
      id
    }}
  }}
}}
"""