"""Módulo para formatar notícias em threads para redes sociais."""
import logging
import textwrap


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constantes para os limites e textos padrão
MAX_TWEET_LENGTH = 280


def format_news_thread(article):
    """
    Formata uma notícia em uma lista de até 3 tweets para uma thread.

    Args:
        article (dict): Um dicionário contendo 'title', 'link' e 'summary'.

    Returns:
        list: Uma lista de strings, onde cada string é um tweet.
    """
    title = article['title'].strip()
    link = article['link']
    # O resumo de feeds RSS pode conter HTML, uma limpeza básica é útil
    summary = article['summary'].strip()  # Idealmente, usaríamos uma lib para remover HTML

    # --- Tweet 1: Manchete ---
    header = f"📰 Notícia: {title}"
    footer = "\n\n👇 Siga o fio para mais detalhes e a fonte."
    hashtags = "\n\n#Noticias #Politica #Brasil"

    tweet1 = (textwrap.shorten(header,
                               width=(MAX_TWEET_LENGTH - len(footer) - len(hashtags)),
                               placeholder="...") + footer + hashtags)

    # --- Tweet 2: Resumo/Detalhes ---
    # Deixa espaço para um prefixo como "Resumo: "
    prefix_tweet2 = "Resumo: "
    available_space = MAX_TWEET_LENGTH - len(prefix_tweet2)
    tweet2_content = textwrap.shorten(summary,
                                      width=available_space,
                                      placeholder="... (leia mais no link)")
    tweet2 = prefix_tweet2 + tweet2_content

    # --- Tweet 3: Fonte ---
    tweet3 = f"Fonte oficial da notícia:\n{link}"

    thread = [tweet1, tweet2, tweet3]
    logging.info("Thread formatada para a notícia: '%s'", title)
    return thread


if __name__ == '__main__':
    print("--- Testando o formatador de notícias ---")
    sample_article = {
        'title': ("Comissão aprova projeto que altera regras de aposentadoria para "
                  "servidores públicos em nova sessão extraordinária"),
        'link': 'https://www.camara.leg.br/noticias/exemplo-de-link',
        'summary': ('O texto, que segue para análise do Plenário, estabelece um novo '
                    'cálculo para o benefício e regras de transição. A proposta foi ' 
                    'alvo de intenso debate entre os parlamentares, com discussões ' 
                    'que se estenderam por toda a tarde. A oposição criticou a ' 
                    'velocidade da tramitação.')
    }
    formatted_thread = format_news_thread(sample_article)

    print("\n--- Thread Formatada ---\n")
    for i, tweet in enumerate(formatted_thread):
        print(f"\n--- TWEET {i+1}/{len(formatted_thread)} (Tamanho: {len(tweet)}) ---\n{tweet}")
    print("-" * 50)
