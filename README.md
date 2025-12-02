# Projeto Sentinela 

**Um bot de transparência que monitora gastos parlamentares e agrega notícias dos Três Poderes do Brasil, publicando tudo no X (antigo Twitter).**

---

##  O que é o Projeto Sentinela?

O Projeto Sentinela é uma ferramenta de fiscalização cívica com duas funções principais:

1.  **Monitor de Gastos:** Divulga os gastos da Cota Parlamentar de deputados federais, transformando dados públicos da Câmara dos Deputados em um ranking claro e acessível.
2.  **Agregador de Notícias:** Centraliza e publica as últimas notícias de fontes oficiais do Legislativo, Executivo e Judiciário, mantendo o cidadão informado sobre as atividades dos Três Poderes.

O objetivo é simples: transformar dados e notícias públicas em conhecimento acessível para todos.

##  Como Funciona?

O projeto opera em duas frentes principais, ambas automatizadas com GitHub Actions.

### 1. Monitor de Gastos de Deputados

Este módulo foca na Cota Parlamentar da Câmara dos Deputados.

-   **Coleta e Ranking:** Um workflow do GitHub Actions (`.github/workflows/generate-ranking.yml`) é executado quinzenalmente. Ele roda o script `src/gerador_de_ranking.py` que busca todos os deputados, calcula seus gastos nos últimos 90 dias e gera um ranking (`ranking_gastos.json`).
-   **Postagem Automática:** Outro workflow (`.github/workflows/bot-schedule.yml`) roda duas vezes ao dia. Ele executa o script `src/main.py`, que lê o ranking, seleciona o próximo deputado da fila, detalha suas despesas e posta uma thread informativa no X. O estado da fila é controlado pelo arquivo `estado.json`.

### 2. Agregador de Notícias

Este módulo coleta notícias de fontes oficiais dos Três Poderes.

-   **Fontes Coletadas:**
    -   **Legislativo:** Agência Senado e Agência Câmara.
    -   **Judiciário:** Supremo Tribunal Federal (STF) e Tribunal Superior Eleitoral (TSE).
    -   **Executivo:** Agência Brasil.
-   **Coleta e Postagem:** Um workflow dedicado (`.github/workflows/noticias-bot.yml`) roda em intervalos regulares. Ele executa o script `main_noticias.py`, que:
    1.  Chama os coletores na pasta `src/coletores/` para buscar as últimas notícias de todas as fontes via feeds RSS.
    2.  Filtra as notícias para não repetir posts, usando o `estado.json` como referência.
    3.  Seleciona a notícia mais recente, a formata em uma thread com título, resumo e link, e a publica no X.

##  Tecnologias Utilizadas

-   **Linguagem:** Python 3
-   **Bibliotecas Principais:** `requests`, `tweepy`, `python-dotenv`, `feedparser`
-   **Fontes de Dados:**
    -   [API de Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/)
    -   Feeds RSS do Senado, Câmara, STF, TSE e Agência Brasil.
-   **Publicação:** API do X (Twitter)
-   **Automação:** GitHub Actions

##  Como Executar o Projeto Localmente

Embora o bot opere de forma autônoma, você pode executá-lo em sua máquina para testes e desenvolvimento.

**1. Pré-requisitos:**
   - Python 3.8 ou superior
   - Git

**2. Clone o Repositório:**
   ```bash
   git clone https://github.com/zlimaz/Projeto-Sentinela.git
   cd Projeto-Sentinela
   ```

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
   - Crie um arquivo `.env` (pode copiar do `.env.example`) e preencha com suas credenciais da API do X.

**6. Execute os Scripts Manualmente:**

   - **Para o Monitor de Gastos:**
     ```bash
     # Gerar o ranking de gastos (opcional, para testes)
     python3 -m src.gerador_de_ranking

     # Postar o próximo deputado do ranking
     python3 -m src.main
     ```

   - **Para o Agregador de Notícias:**
     ```bash
     # Coletar e postar a última notícia
     python3 main_noticias.py
     ```

##  Estrutura de Arquivos

```
.
├── .github/
│   └── workflows/
│       ├── bot-schedule.yml       # Workflow para postar gastos
│       ├── generate-ranking.yml   # Workflow para gerar ranking de gastos
│       └── noticias-bot.yml       # Workflow para postar notícias
├── src/
│   ├── analisador/
│   │   └── analisador_noticias.py # Filtra e gerencia notícias postadas
│   ├── api_client.py            # Cliente para a API do X (Twitter)
│   ├── coletores/               # Scripts que coletam notícias das fontes
│   │   ├── coleta_agenciabrasil.py
│   │   ├── coleta_camara.py
│   │   ├── coleta_senado.py
│   │   ├── coleta_stf.py
│   │   └── coleta_tse.py
│   ├── formatadores/
│   │   └── formatador_noticias.py # Formata notícias para o X
│   ├── gerador_de_ranking.py    # Script do monitor de gastos
│   └── main.py                  # Script principal do monitor de gastos
├── main_noticias.py             # Script principal do agregador de notícias
├── estado.json                  # Guarda o estado da aplicação (últimos posts)
├── ranking_gastos.json          # Ranking de deputados por gastos
├── requirements.txt             # Dependências Python
└── README.md                    # Esta documentação
```
