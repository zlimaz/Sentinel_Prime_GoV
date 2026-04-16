import os
import datetime
import random
import time
import requests
import tweepy
from tweepy.errors import TooManyRequests, TweepyException
from supabase import create_client, Client

class SentinelAPIClient:
    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "SentinelPrimeGov/1.0 (Bot; OpenSource; Transparencia Publica)"
        }
        
        # Setup Supabase
        sb_url = os.environ.get("SUPABASE_URL")
        sb_key = os.environ.get("SUPABASE_SERVICE_KEY")
        self.db: Client = create_client(sb_url, sb_key) if sb_url and sb_key else None
        
        # Credenciais OAuth 2.0
        self.client_id = os.environ.get("X_OAUTH2_CLIENT_ID")
        self.client_secret = os.environ.get("X_OAUTH2_CLIENT_SECRET")
        self.redirect_uri = "https://github.com/zlimaz/Sentinel_Prime_GoV"

        # Inicializa cliente (será populado pelo refresh_token)
        self.x_client = self._init_x_client_v2()

    def _init_x_client_v2(self):
        """Inicializa o cliente X usando OAuth 2.0 com Refresh Token do Supabase."""
        try:
            # 1. Busca tokens atuais no Supabase
            res = self.db.table("bot_state").select("value").eq("key", "twitter_tokens").execute()
            if not res.data:
                print("Erro: Tokens OAuth 2.0 não encontrados no Supabase.")
                return None
            
            tokens = res.data[0]["value"]
            
            # 2. Configura o Handler de OAuth 2.0
            oauth2_handler = tweepy.OAuth2UserHandler(
                client_id=self.client_id,
                redirect_uri=self.redirect_uri,
                scope=["tweet.read", "tweet.write", "users.read", "offline.access"],
                client_secret=self.client_secret
            )

            # 3. Faz o Refresh do Token (Garante que temos um access_token válido)
            # O Tweepy renova automaticamente se passarmos o refresh_token
            new_tokens = oauth2_handler.refresh_token(
                "https://api.twitter.com/2/oauth2/token",
                refresh_token=tokens["refresh_token"]
            )

            # 4. Salva os novos tokens no Supabase para a próxima execução
            self.db.table("bot_state").upsert({
                "key": "twitter_tokens", 
                "value": new_tokens
            }).execute()

            # 5. Retorna o cliente autenticado
            return tweepy.Client(bearer_token=new_tokens["access_token"])

        except Exception as e:
            print(f"Erro ao renovar tokens OAuth 2.0: {e}")
            return None

    def is_under_rate_limit_lock(self):
        try:
            res = self.db.table("bot_state").select("value").eq("key", "rate_limit_lock").execute()
            if res.data:
                lock_time = datetime.datetime.fromisoformat(res.data[0]["value"])
                if datetime.datetime.now(datetime.timezone.utc) < lock_time:
                    return True
        except Exception: pass
        return False

    def set_rate_limit_lock(self, hours=2):
        lock_until = (datetime.datetime.now(datetime.timezone.utc) + 
                     datetime.timedelta(hours=hours)).isoformat()
        try:
            self.db.table("bot_state").upsert({"key": "rate_limit_lock", "value": lock_until}).execute()
        except Exception: pass

    def get_deputies_list(self):
        all_deputies = []
        url = "https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome&itens=100"
        while url:
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                all_deputies.extend(data["dados"])
                url = next((link["href"] for link in data["links"] if link["rel"] == "next"), None)
            except Exception: break
        return all_deputies

    def get_deputy_expenses(self, deputy_id, year=None, month=None):
        url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{deputy_id}/despesas"
        params = {"ano": year or datetime.datetime.now().year, "mes": month or datetime.datetime.now().month, "itens": 100}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            return response.json().get("dados", []) if response.status_code == 200 else []
        except Exception: return []

    def post_tweet_thread(self, tweets):
        if not self.x_client:
            print("Erro: X Client não inicializado. Verifique os tokens OAuth 2.0 no Supabase.")
            return None
            
        if self.is_under_rate_limit_lock():
            print("Execução abortada: Bot em quarentena de Rate Limit.")
            return None

        last_id = None
        for i, text in enumerate(tweets):
            try:
                if i > 0:
                    time.sleep(random.uniform(10, 30))

                # Para OAuth 2.0, o Tweepy usa bearer_token internamente no Client
                response = self.x_client.create_tweet(text=text, in_reply_to_tweet_id=last_id)
                last_id = response.data['id']
                print(f"Postado com sucesso (OAuth 2.0)! ID: {last_id}")
            
            except TooManyRequests:
                print("Erro: Rate Limit atingido no X.")
                self.set_rate_limit_lock(2)
                return "rate_limit"
            except TweepyException as e:
                if "duplicate content" in str(e).lower():
                    print("Erro: Conteúdo duplicado no X.")
                    return "duplicate"
                print(f"Erro ao postar no X (OAuth 2.0): {e}")
                return None
        return last_id
