import os
import datetime
import time
from dotenv import load_dotenv
from src.api_client import SentinelAPIClient

load_dotenv()

def sync_parliamentarians(client):
    deputies = client.get_deputies_list()
    if not deputies: return

    formatted = [{
        "id": d["id"],
        "nome": d["nome"],
        "sigla_partido": d["siglaPartido"],
        "sigla_uf": d["siglaUf"],
        "id_legislatura": d["idLegislatura"],
        "url_foto": d["urlFoto"],
        "email": d.get("email", ""),
        "updated_at": datetime.datetime.now().isoformat()
    } for d in deputies]
    
    try:
        client.db.table("parlamentares").upsert(formatted).execute()
    except Exception as e:
        print(f"Erro sync parlamentares: {e}")

def sync_all_expenses(client, months_back=2):
    now = datetime.datetime.now()
    try:
        deputies = client.db.table("parlamentares").select("id, nome").execute().data
    except Exception: return

    for i, dep in enumerate(deputies):
        dep_id, dep_name = dep["id"], dep["nome"]
        all_new = []
        
        for m in range(months_back):
            target = now - datetime.timedelta(days=m * 30)
            expenses = client.get_deputy_expenses(dep_id, target.year, target.month)
            
            for e in expenses:
                all_new.append({
                    "id_externo": f"{dep_id}_{e['idDocumento'] or e['numDocumento']}_{e['numLote']}",
                    "deputado_id": dep_id,
                    "data_emissao": e["dataEmissao"],
                    "tipo_despesa": e["tipoDespesa"],
                    "valor_liquido": e["valorLiquido"],
                    "nome_fornecedor": e["nomeFornecedor"],
                    "cnpj_cpf_fornecedor": e["cnpjCpfFornecedor"],
                    "url_documento": e["urlDocumento"],
                    "ano": target.year,
                    "mes": target.month
                })

        if all_new:
            try:
                client.db.table("despesas").upsert(all_new, on_conflict="id_externo").execute()
            except Exception: pass
        time.sleep(0.5)

def main():
    client = SentinelAPIClient()
    if not client.db: return
    sync_parliamentarians(client)
    sync_all_expenses(client)

if __name__ == "__main__":
    main()
