<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/Database-Supabase-green.svg" alt="Supabase" />
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg?logo=github-actions&logoColor=white" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License" />
</div>

<br />

<div align="center">
  <h1>🏛️ Sentinel Prime GoV</h1>
  <p><b>Bot open-source de transparência governamental. Transformando dados públicos em informação acessível.</b></p>
</div>

---

## Sobre o Projeto

O **Sentinel Prime GoV** é uma ferramenta autônoma de fiscalização cívica. Sua missão é extrair dados de portais de transparência e fontes oficiais, processá-los e publicá-los na rede X (antigo Twitter). O foco principal é manter o cidadão engajado e informado sobre as movimentações do poder público brasileiro (Legislativo, Executivo e Judiciário).

O projeto foi arquitetado com foco em **resiliência**, **escalabilidade** e **boas práticas de engenharia de dados**, utilizando automação em nuvem e persistência em banco de dados para garantir alta disponibilidade.

## Principais Funcionalidades

- **Monitor de Gastos (Cota Parlamentar):** Consome a API de Dados Abertos da Câmara dos Deputados, processa gastos granulares, gera um ranking semanal e publica as despesas detalhadas.
- **Agregador de Notícias Oficiais:** Coleta feeds RSS dinâmicos de agências oficiais (Senado, Câmara, STF, TSE e Agência Brasil) para unificar atualizações políticas.
- **Postagem Segura & Resiliente:** Sistema de *Drip Feed* (postagens espaçadas) e *Jitter* (intervalos dinâmicos), com tratamento avançado de Rate Limit via `SentinelAPIClient` para evitar bloqueios da plataforma.
- **Sincronização Automatizada (Supabase):** Substitui arquivos JSON locais por tabelas relacionais em nuvem (`parlamentares`, `despesas`, `bot_state`), garantindo consistência transacional e isolando a aplicação contra problemas de concorrência.

## Arquitetura e Stack Tecnológica

O sistema opera sem intervenção humana, adotando uma infraestrutura *Serverless* com cron jobs:

* **Linguagem Base:** Python 3.10+
* **Banco de Dados:** Supabase (PostgreSQL / PostgREST)
* **Integrações de API:** Câmara dos Deputados (Dados Abertos), X API v2 (`tweepy`), Feeds RSS (`feedparser` / `beautifulsoup4`)
* **Orquestração e CI/CD:** GitHub Actions

## Fluxo de Funcionamento Automático

1. **Sincronização Diária (`sync_data.py`):** Varre as APIs governamentais e atualiza os registros de deputados e despesas no banco de dados, utilizando chaves de identificação únicas (`id_externo`) para evitar duplicações.
2. **Consolidação (`gerador_de_ranking.py`):** Analisa a base e monta o ranqueamento semanal dos gastos no painel interno.
3. **Distribuição Controlada (`main.py` & `main_noticias.py`):** Baseado em filas lógicas no Supabase (`bot_state`), scripts são disparados via GitHub Actions. Cada ciclo processa apenas **um registro por vez**, constrói uma *thread* informativa e a publica na rede social com total segurança.

## Como Executar Localmente

### 1. Pré-requisitos
- Python 3.10 ou superior
- Git
- Uma conta e projeto configurado no [Supabase](https://supabase.com/)
- Credenciais da API do X (Twitter Developer Portal)

### 2. Instalação
```bash
# Clone o repositório
git clone https://github.com/zlimaz/Sentinel_Prime_GoV.git
cd Sentinel_Prime_GoV

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com as credenciais:
```env
# X (Twitter) API Keys
X_API_KEY="sua_api_key"
X_API_SECRET="seu_api_secret"
X_ACCESS_TOKEN="seu_access_token"
X_ACCESS_TOKEN_SECRET="seu_token_secret"
X_BEARER_TOKEN="seu_bearer_token"

# Supabase
SUPABASE_URL="https://sua-url.supabase.co"
SUPABASE_KEY="sua_chave_anon_ou_service"
```

### 4. Rodando os Scripts
```bash
# 1. Alimentar o banco com os dados oficiais (Executar primeiro)
python -m src.sync_data

# 2. Gerar o ranqueamento lógico
python -m src.gerador_de_ranking

# 3. Disparar a postagem sobre os gastos
python -m src.main

# 4. Disparar o agregador de notícias oficiais
python main_noticias.py
```

## Estrutura do Repositório

```text
.
├── .github/workflows/         # Configuração dos Cron Jobs (GitHub Actions)
├── src/
│   ├── analisador/            # Algoritmos de filtro e controle de estado
│   ├── coletores/             # Web scrapers e ingestão de feeds RSS
│   ├── formatadores/          # Processamento textual para threads estruturadas
│   ├── api_client.py          # Wrapper de resiliência e controle de limites HTTP
│   ├── sync_data.py           # Rotina ETL (Câmara -> Supabase)
│   ├── gerador_de_ranking.py  # Consolidadores de métricas
│   └── main.py                # Entrypoint do Agente de Gastos
├── main_noticias.py           # Entrypoint do Agente de Notícias
├── requirements.txt           # Dependências catalogadas
└── README.md                  # Documentação principal
```

##  Como Contribuir

A transparência pública é um trabalho de todos. Cientistas de dados, engenheiros de software, pesquisadores e entusiastas são bem-vindos!

1. Realize um *Fork* deste repositório.
2. Crie uma branch para a sua feature (`git checkout -b feature/MinhaFeature`).
3. Siga o estilo de código existente e comite suas mudanças (`git commit -m 'feat: implementando novo coletor'`).
4. Faça um *Push* para a branch (`git push origin feature/MinhaFeature`).
5. Abra um *Pull Request* detalhando a melhoria.

> **Regra de Ouro:** Nenhuma credencial deve ser persistida no código. Utilize estritamente variáveis de ambiente.

## Licença

Este projeto encontra-se sob a licença **MIT**. Sinta-se livre para utilizar, modificar e distribuir conforme necessário.

---
<div align="center">
  <i>Transformando transparência governamental em código. 🇧🇷</i>
</div>
