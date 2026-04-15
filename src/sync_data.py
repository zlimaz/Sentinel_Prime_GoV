import os
import datetime
import time
from dotenv import load_dotenv
from src.api_client import SentinelAPIClient

load_dotenv()

def sync_parliamentarians(client):
    """Atualiza a base de parlamentares no Supabase."""
    print("Sincronizando parlamentares...")
    deputies = client.get_deputies_list()
    if not deputies: 
        print("Nenhum parlamentar encontrado na API.")
        return

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
        print(f"Sucesso: {len(formatted)} parlamentares sincronizados.")
    except Exception as e:
        print(f"Erro ao salvar parlamentares: {e}")

def sync_all_expenses(client, months_back=2):
    """Sincroniza despesas de forma resiliente."""
    now = datetime.datetime.now()
    try:
        deputies = client.db.table("parlamentares").select("id, nome").execute().data
    except Exception as e: 
        print(f"Erro ao buscar deputados no DB: {e}")
        return

    total = len(deputies)
    print(f"Sincronizando despesas de {total} deputados (últimos {months_back} meses)...")

    for i, dep in enumerate(deputies):
        dep_id, dep_name = dep["id"], dep["nome"]
        all_new = []
        
        for m in range(months_back):
            target = now - datetime.timedelta(days=m * 30)
            expenses = client.get_deputy_expenses(dep_id, target.year, target.month)
            
            for e in expenses:
                # Geração de ID Único Resiliente usando .get() para evitar KeyError
                doc_id = e.get('idDocumento') or e.get('numDocumento') or str(time.time())
                lote = e.get('numLote') or '0'
                ext_id = f"{dep_id}_{doc_id}_{lote}"

                all_new.append({
                    "id_externo": ext_id,
                    "deputado_id": dep_id,
                    "data_emissao": e.get("dataEmissao"),
                    "tipo_despesa": e.get("tipoDespesa"),
                    "valor_liquido": e.get("valorLiquido", 0),
                    "nome_fornecedor": e.get("nomeFornecedor", "Não Informado"),
                    "cnpj_cpf_fornecedor": e.get("cnpjCpfFornecedor"),
                    "url_documento": e.get("urlDocumento"),
                    "ano": target.year,
                    "mes": target.month
                })

        if all_new:
            try:
                client.db.table("despesas").upsert(all_new, on_conflict="id_externo").execute()
                print(f"[{i+1}/{total}] {dep_name}: {len(all_new)} despesas processadas.")
            except Exception as e:
                print(f"Erro ao salvar despesas de {dep_name}: {e}")
        
        # Pausa para respeitar os limites da API da Câmara
        time.sleep(0.3)

def main():
    client = SentinelAPIClient()
    if not client.db: 
        print("Erro: Cliente Supabase não inicializado.")
        return
    sync_parliamentarians(client)
    sync_all_expenses(client)

if __name__ == "__main__":
    main()
