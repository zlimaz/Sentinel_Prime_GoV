import tweepy
import os
from dotenv import load_dotenv

# Carrega chaves do seu arquivo .env local
load_dotenv()

client_id = os.environ.get("X_OAUTH2_CLIENT_ID")
client_secret = os.environ.get("X_OAUTH2_CLIENT_SECRET")

# A URL deve ser EXATAMENTE a mesma que você colocou no "Callback URI" do portal do X
redirect_uri = "https://github.com/zlimaz/Sentinel_Prime_GoV" 

def main():
    if not client_id or not client_secret:
        print("ERRO: Configure X_OAUTH2_CLIENT_ID e X_OAUTH2_CLIENT_SECRET no seu arquivo .env antes de rodar.")
        return

    # 1. Inicializa o manipulador do OAuth 2.0
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=["tweet.read", "tweet.write", "users.read", "offline.access"],
        client_secret=client_secret
    )

    print("\n--- ETAPA 1: AUTORIZAÇÃO MANUAL ---")
    print("1. Clique no link abaixo e autorize o bot:")
    print("\n" + oauth2_user_handler.get_authorization_url() + "\n")

    # 2. Você cola a URL de resposta
    authorization_response = input("2. Após autorizar, copie a URL INTEIRA da barra de endereços e cole aqui: ").strip()

    try:
        # 3. Troca a URL de resposta pelos tokens reais
        token = oauth2_user_handler.fetch_token(authorization_response)
        print("\n✅ TOKENS OBTIDOS COM SUCESSO!")
        print("-" * 50)
        print(f"REFRESH_TOKEN PARA O SUPABASE:\n{token['refresh_token']}")
        print("-" * 50)
        print("\nCOMO SALVAR NO SUPABASE:")
        print("1. Vá em Table Editor -> bot_state")
        print("2. Insira ou Edite a key 'twitter_tokens'")
        print(f"3. No campo 'value', cole EXATAMENTE isso (em formato JSON):")
        print('{"refresh_token": "' + token['refresh_token'] + '"}')

    except Exception as e:
        print(f"\n❌ FALHA AO OBTER TOKENS: {e}")

if __name__ == "__main__":
    main()
