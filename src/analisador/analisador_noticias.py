"""Módulo para análise e filtragem de notícias."""
import logging
from datetime import datetime, timedelta, timezone


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def prune_old_posted_articles(posted_articles, days_to_keep=3):
    """
    Remove notícias antigas da lista de artigos já postados.

    Args:
        posted_articles (list): Lista de dicionários, cada um com 'link' e 'posted_at'.
        days_to_keep (int): Número de dias para manter um artigo na lista.

    Returns:
        list: A lista de artigos postados, mas sem os antigos.
    """
    if not posted_articles:
        return []

    pruned_list = []
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

    for article in posted_articles:
        # Usamos o fromisoformat para converter a data de volta para um objeto datetime
        # Assumimos que a data foi salva no formato ISO 8601 com timezone
        posted_date = datetime.fromisoformat(article['posted_at'])
        if posted_date >= cutoff_date:
            pruned_list.append(article)
        else:
            logging.info("Removendo artigo antigo da lista de estado: %s", article['link'])

    return pruned_list


def filter_new_articles(all_fetched_articles, posted_articles):
    """
    Filtra uma lista de notícias, retornando apenas as que ainda não foram postadas.

    Args:
        all_fetched_articles (list): Lista de todas as notícias buscadas nos feeds.
        posted_articles (list): A lista (já limpa de antigos) de artigos postados.

    Returns:
        list: Uma lista de notícias que são novas e prontas para serem postadas.
    """
    if not all_fetched_articles:
        return []

    posted_links = {article['link'] for article in posted_articles}
    new_articles = []

    for article in all_fetched_articles:
        if article['link'] not in posted_links:
            new_articles.append(article)

    logging.info("Filtragem concluída. %d novas notícias encontradas.", len(new_articles))
    # A lista de notícias do feed já vem em ordem cronológica (mais novas primeiro)
    return new_articles
