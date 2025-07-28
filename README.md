# Projeto Sentinela

Este projeto tem como objetivo monitorar e divulgar os gastos de parlamentares brasileiros (deputados federais) de forma automatizada, publicando os resultados em redes sociais como o X (antigo Twitter).

## Visão Geral

A ideia é consumir dados diretamente da API de Dados Abertos da Câmara dos Deputados para obter informações sobre a Cota para o Exercício da Atividade Parlamentar. Com esses dados, o sistema irá:

1.  Processar os gastos de um parlamentar específico.
2.  Agregar os valores por um período determinado (ex: últimos 90 dias).
3.  Formatar um resumo claro e informativo.
4.  Publicar o resumo em um perfil dedicado no X.

## Tecnologias

-   **Linguagem:** Python
-   **Automação:** n8n (planejado)
-   **Fonte de Dados:** API de Dados Abertos da Câmara dos Deputados.
-   **Publicação:** API do X (Twitter).
