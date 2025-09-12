"""Coletor de notícias da Câmara dos Deputados."""
import logging
import feedparser


# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CAMARA_NEWS_RSS_URL = "https://www.camara.leg.br/noticias/rss/ultimas-noticias"


def fetch_camara_news():
    """
    Busca as últimas notícias do feed RSS da Agência Câmara.

    Retorna:
        list: Uma lista de dicionários, onde cada dicionário representa uma notícia
              com as chaves 'title', 'link' e 'summary'.
              Retorna uma lista vazia em caso de erro.
    """
    logging.info(f"Buscando notícias do feed: {CAMARA_NEWS_RSS_URL}")
    try:
        feed = feedparser.parse(CAMARA_NEWS_RSS_URL)

        if feed.bozo:
            logging.error("O feed RSS da Câmara está malformado. Causa: %s",
                          feed.bozo_exception)
            return []

        news_list = []
        for entry in feed.entries:
            news_item = {
                'title': entry.title,
                'link': entry.link,
                'summary': entry.summary
            }
            news_list.append(news_item)

        logging.info("%d notícias encontradas no feed da Câmara.", len(news_list))
        return news_list

    except Exception as e:  # pylint: disable=broad-except
        logging.error("Falha ao buscar ou analisar o feed de notícias da Câmara: %s", e)
        return []


if __name__ == '__main__':
    print("--- Testando o coletor de notícias da Câmara ---")
    latest_news = fetch_camara_news()
    if latest_news:
        print(f"\nEncontradas {len(latest_news)} notícias.")
        print("\n--- Exemplo da primeira notícia encontrada ---")
        print(f"Título: {latest_news[0]['title']}")
        print(f"Link: {latest_news[0]['link']}")
        print(f"Resumo: {latest_news[0]['summary']}")
        print("-" * 50)
    else:
        print("Nenhuma notícia foi encontrada ou ocorreu um erro.")
