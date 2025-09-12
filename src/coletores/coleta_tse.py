
"""
Coletor de notícias do Tribunal Superior Eleitoral (TSE)."""
import logging
import feedparser
import requests


# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TSE_NEWS_RSS_URL = "https://www.tse.jus.br/comunicacao/noticias/rss"

# Cabeçalho para simular um navegador
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
}


def fetch_tse_news():
    """
    Busca as últimas notícias do feed RSS do TSE.

    Retorna:
        list: Uma lista de dicionários, onde cada dicionário representa uma notícia
              com as chaves 'title', 'link' e 'summary'.
              Retorna uma lista vazia em caso de erro.
    """
    logging.info(f"Buscando notícias do feed: {TSE_NEWS_RSS_URL}")
    try:
        response = requests.get(TSE_NEWS_RSS_URL, headers=HEADERS,
                                timeout=15, verify=False)
        response.raise_for_status()

        feed = feedparser.parse(response.content)

        if feed.bozo:
            logging.error("O feed RSS do TSE está malformado. Causa: %s",
                          feed.bozo_exception)
            return []

        news_list = []
        for entry in feed.entries:
            news_item = {
                'title': entry.title,
                'link': entry.link,
                'summary': getattr(entry, 'summary', '')
            }
            news_list.append(news_item)

        logging.info("%d notícias encontradas no feed do TSE.", len(news_list))
        return news_list

    except requests.RequestException as e:
        logging.error("Falha ao fazer a requisição para o feed do TSE: %s", e)
        return []
    except Exception as e:  # pylint: disable=broad-except
        logging.error("Falha ao analisar o feed de notícias do TSE: %s", e)
        return []


if __name__ == '__main__':
    print("--- Testando o coletor de notícias do TSE ---")
    latest_news = fetch_tse_news()
    if latest_news:
        print(f"\nEncontradas {len(latest_news)} notícias.")
        print("\n--- Exemplo da primeira notícia encontrada ---")
        print(f"Título: {latest_news[0]['title']}")
        print(f"Link: {latest_news[0]['link']}")
        print(f"Resumo: {latest_news[0]['summary']}")
        print("-" * 50)
    else:
        print("Nenhuma notícia foi encontrada ou ocorreu um erro.")
