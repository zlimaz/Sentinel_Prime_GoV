#!/bin/bash

# --- Script para Configurar o Workflow do Projeto Sentinela no n8n ---
#
# Este script cria e ATIVA um workflow no n8n para executar o bot
# de postagens automaticamente.
#
# COMO USAR:
#   1. Abra este arquivo e substitua "SUA_CHAVE_DE_API_AQUI" pela sua chave.
#   2. Salve o arquivo.
#   3. Execute no terminal: ./scripts/setup_n8n_workflow.sh
#

# --- Configuração ---
N8N_URL="http://localhost:5678"
API_KEY= 

# --- Definição do Workflow (JSON) ---
WORKFLOW_JSON='{
  "name": "Projeto Sentinela - Bot de Posts",
  "nodes": [
    {
      "parameters": {
        "cronTime": "0 12 * * *",
        "timezone": "America/Sao_Paulo"
      },
      "name": "Agendado para 12:00",
      "type": "n8n-nodes-base.cron",
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
        "cronTime": "0 18 * * *",
        "timezone": "America/Sao_Paulo"
      },
      "name": "Agendado para 18:00",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [ 800, 400 ]
    }
  ],
  "connections": {
    "Agendado para 12:00": { "main": [ [ { "node": "Executar Bot Sentinela", "type": "main" } ] ] },
    "Agendado para 18:00": { "main": [ [ { "node": "Executar Bot Sentinela", "type": "main" } ] ] }
  },
  "settings": {}
}'

# --- Passo 1: Criar o Workflow ---
echo "Criando workflow no n8n..."

RESPONSE=$(curl -s -X POST "${N8N_URL}/api/v1/workflows" \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: ${API_KEY}" \
  -d "${WORKFLOW_JSON}")

WORKFLOW_ID=$(echo ${RESPONSE} | jq -r '.id')

if [ -z "${WORKFLOW_ID}" ] || [ "${WORKFLOW_ID}" == "null" ]; then
  echo "Erro: Não foi possível criar o workflow ou extrair seu ID."
  echo "Resposta do n8n: ${RESPONSE}"
  exit 1
fi

echo "Workflow criado com sucesso! ID: ${WORKFLOW_ID}"

# --- Passo 2: Ativar o Workflow ---
echo "Ativando o workflow..."

ACTIVATION_RESPONSE=$(curl -s -X POST "${N8N_URL}/api/v1/workflows/${WORKFLOW_ID}/activate" \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: ${API_KEY}")

ACTIVATION_SUCCESS=$(echo ${ACTIVATION_RESPONSE} | jq -r '.active')

if [ "${ACTIVATION_SUCCESS}" == "true" ]; then
  echo -e "\nWorkflow ativado com sucesso!"
  echo "O Projeto Sentinela agora está automatizado."
else
  echo "Erro: Falha ao ativar o workflow."
  echo "Resposta do n8n: ${ACTIVATION_RESPONSE}"
  exit 1
fi