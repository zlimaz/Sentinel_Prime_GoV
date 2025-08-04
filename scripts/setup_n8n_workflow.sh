#!/bin/bash

# --- Script para Configurar o Workflow do Projeto Sentinela no n8n ---
#
# Este script cria e ativa um workflow no n8n para executar o bot
# de postagens automaticamente.
#
# PRÉ-REQUISITOS:
#   1. Ter o n8n rodando (ex: via Docker) e acessível em http://localhost:5678.
#   2. Ter uma chave de API do n8n.
#
# COMO USAR:
#   1. Abra este arquivo em um editor de texto.
#   2. Substitua a string "SUA_CHAVE_DE_API_AQUI" pela sua chave de API real.
#   3. Salve o arquivo.
#   4. Abra o terminal, navegue até a pasta 'scripts' e execute:
#      bash setup_n8n_workflow.sh
#

# --- Configuração ---
N8N_URL="http://localhost:5678"
API_KEY="SUA_CHAVE_DE_API_AQUI" 

# --- Definição do Workflow (JSON) ---
WORKFLOW_JSON='{
  "name": "Projeto Sentinela - Bot de Posts",
  "nodes": [
    {
      "parameters": {
        "triggerTimes": {
          "mode": "cron",
          "cronTime": "0 12 * * *",
          "cronTimezone": "America/Sao_Paulo"
        }
      },
      "name": "Agendado para 12:00",
      "type": "n8n-nodes-base.schedule",
      "typeVersion": 1,
      "position": [ 800, 200 ]
    },
    {
      "parameters": {
        "command": "/home/zlimaz/Documentos/Projeto-Sentinela/.venv/bin/python3 -m src.main",
        "executeIn": "/home/zlimaz/Documentos/Projeto-Sentinela/"
      },
      "name": "Executar Bot Sentinela",
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [ 1100, 300 ]
    },
    {
      "parameters": {
        "triggerTimes": {
          "mode": "cron",
          "cronTime": "0 18 * * *",
          "cronTimezone": "America/Sao_Paulo"
        }
      },
      "name": "Agendado para 18:00",
      "type": "n8n-nodes-base.schedule",
      "typeVersion": 1,
      "position": [ 800, 400 ]
    }
  ],
  "connections": {
    "Agendado para 12:00": { "main": [ [ { "node": "Executar Bot Sentinela", "type": "main" } ] ] },
    "Agendado para 18:00": { "main": [ [ { "node": "Executar Bot Sentinela", "type": "main" } ] ] }
  },
  "active": true,
  "settings": {}
}'

# --- Execução do Comando ---
echo "Criando workflow no n8n..."
curl -X POST "${N8N_URL}/api/v1/workflows" \
-H "Content-Type: application/json" \
-H "X-N8N-API-KEY: ${API_KEY}" \
-d "${WORKFLOW_JSON}"

echo -e "\n\nWorkflow criado! Verifique a interface do n8n."
