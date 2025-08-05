# Projeto Sentinela 🤖🔍

**Um bot de transparência que monitora e divulga os gastos da Cota Parlamentar de deputados federais brasileiros no X (antigo Twitter).**

---

## 🎯 O que é o Projeto Sentinela?

O Projeto Sentinela é uma ferramenta de fiscalização cívica criada para dar mais visibilidade aos gastos públicos. Ele consome dados diretamente da API de Dados Abertos da Câmara dos Deputados, processa essas informações e as publica de forma clara e acessível em uma thread no X, permitindo que qualquer cidadão acompanhe como a Cota Parlamentar está sendo utilizada.

O objetivo é simples: transformar dados públicos em conhecimento acessível para todos.

## ⚙️ Como Funciona?

O projeto é dividido em três fases principais:

1.  **Fase 1: Coleta e Ranking (Concluída)**
    -   Um script (`src/gerador_de_ranking.py`) consome a API da Câmara para buscar todos os deputados em exercício.
    -   Para cada deputado, ele calcula o total de gastos nos últimos 90 dias.
    -   Ao final, gera o arquivo `ranking_gastos.json`, que ordena os deputados do maior para o menor gastador.

2.  **Fase 2: Automação da Postagem (Concluída)**
    -   O script principal (`src/main.py`) lê o ranking e o estado atual (`estado.json`) para selecionar o próximo deputado da fila.
    -   Ele busca os detalhes das despesas desse deputado.
    -   Gera uma thread informativa com 3 tweets: o primeiro com o valor total, o segundo com os principais tipos de despesa, e o terceiro com o maior gasto único e o link para a fonte oficial.
    -   Posta essa thread no X de forma automática.

3.  **Fase 3: Automação Contínua (Concluída)**
    -   A execução do bot agora é totalmente automatizada e gerenciada pelo GitHub Actions, eliminando a necessidade de intervenção manual ou de manter uma máquina local ligada.
    -   **Workflow de Geração de Ranking (`.github/workflows/generate-ranking.yml`):** Roda quinzenalmente (dias 1 e 15 do mês) para atualizar o `ranking_gastos.json` diretamente no repositório, garantindo que o bot sempre utilize dados recentes.
    -   **Workflow de Postagem (`.github/workflows/bot-schedule.yml`):** Roda duas vezes ao dia (12:00 e 18:00 BRT) para selecionar o próximo deputado do ranking e postar a thread. O estado da aplicação (`estado.json`) é persistido diretamente no repositório a cada execução, assegurando que o bot continue de onde parou.

## 🛠️ Tecnologias Utilizadas

-   **Linguagem:** Python 3
-   **Bibliotecas Principais:** `requests`, `tweepy`, `python-dotenv`
-   **Fonte de Dados:** [API de Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/)
-   **Publicação:** API do X (Twitter)
-   **Automação:** GitHub Actions (para agendamento, execução e persistência de estado na nuvem)
    *   *Nota sobre a escolha da automação:* Inicialmente, ferramentas como `cron` ou o n8n foram consideradas para agendamento local. No entanto, para garantir uma automação robusta, escalável e independente de infraestrutura local, optou-se pelo GitHub Actions. Esta plataforma oferece integração nativa com o repositório, gerenciamento seguro de credenciais (GitHub Secrets) e mecanismos eficientes para persistência de estado, como o versionamento do `estado.json` diretamente no Git.

## 🚀 Como Executar o Projeto (e a Automação)

O Projeto Sentinela agora opera de forma autônoma via GitHub Actions. No entanto, você ainda pode executá-lo manualmente em sua máquina local para desenvolvimento, testes ou depuração.

Siga os passos abaixo para configurar e rodar o projeto em sua máquina local.

**1. Pré-requisitos:**
   - Python 3.8 ou superior
   - Git

**2. Clone o Repositório:**
   ```bash
   git clone https://github.com/zlimaz/Projeto-Sentinela.git
   cd Projeto-Sentinela
   ```
   *Nota:* Após clonar, é recomendável executar `git pull` periodicamente para garantir que seu ambiente local esteja sincronizado com as últimas atualizações do `ranking_gastos.json` e `estado.json` que são gerados pela automação na nuvem.

**3. Crie e Ative o Ambiente Virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

**4. Instale as Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

**5. Configure as Credenciais:**
   - Renomeie o arquivo `.env.example` para `.env` (ou crie um novo).
   - Abra o arquivo `.env` e preencha com suas credenciais da API do X:
     ```
     X_API_KEY=SUA_API_KEY
     X_API_SECRET=SUA_API_SECRET
     X_ACCESS_TOKEN=SEU_ACCESS_TOKEN
     X_ACCESS_TOKEN_SECRET=SEU_ACCESS_TOKEN_SECRET
     ```
   *Nota:* Para a automação na nuvem (GitHub Actions), as credenciais são configuradas como GitHub Secrets no repositório, não no arquivo `.env`.

**6. Execute os Scripts Manualmente:**
   - Para gerar o ranking de gastos (se necessário, para testes locais):
     ```bash
     python3 -m src.gerador_de_ranking
     ```
   - Para postar o próximo deputado do ranking no X:
     ```bash
     python3 -m src.main
     ```

## 🗂️ Estrutura de Arquivos

```
.
├── .venv/               # Ambiente virtual Python
├── src/                 # Código fonte do projeto
│   ├── api_client.py    # Funções para interagir com as APIs (Câmara e X)
│   ├── gerador_de_ranking.py # Script para gerar o ranking de gastos
│   └── main.py          # Script principal que gera e posta a thread
├── .env                 # Arquivo para guardar as credenciais (NÃO versionado)
├── .github/             # Configurações do GitHub (workflows de automação)
│   └── workflows/
│       ├── bot-schedule.yml     # Workflow para postagem diária
│       └── generate-ranking.yml # Workflow para geração quinzenal do ranking
├── .gitignore           # Arquivos e pastas ignorados pelo Git
├── estado.json          # Guarda o estado da aplicação (último deputado processado)
├── ranking_gastos.json  # Lista de deputados ordenada por gastos
├── requirements.txt     # Lista de dependências Python
└── README.md            # Esta documentação
```