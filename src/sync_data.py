import os
import datetime
import time
from dotenv import load_dotenv
from src.api_client import SentinelAPIClient

load_dotenv()

def clean_expense(e, dep_id, year, month):
    """Camada de Limpeza (Silver): Normaliza e valida os dados da despesa."""
    # 1. Geração de ID Único determinístico
    doc_id = e.get('idDocumento') or e.get('numDocumento') or str(hash(str(e)))
    lote = e.get('numLote') or '0'
    ext_id = f"{dep_id}_{doc_id}_{lote}"

    # 2. Normalização e Limpeza
    return {
        "id_externo": ext_id,
        "deputado_id": dep_id,
        "data_emissao": e.get("dataEmissao"),
        "tipo_despesa": (e.get("tipoDespesa") or "OUTROS").strip().title(),
        "valor_liquido": float(e.get("valorLiquido") or 0),
        "nome_fornecedor": (e.get("nomeFornecedor") or "NÃO INFORMADO").strip().title(),
        "cnpj_cpf_fornecedor": e.get("cnpjCpfFornecedor"),
        "url_documento": e.get("urlDocumento"),
        "ano": year,
        "mes": month
    }

def sync_parliamentarians(client):
    """Sincroniza parlamentares (Bronze -> Silver)."""
    print("Sincronizando parlamentares...")
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
        print(f"Sucesso: {len(formatted)} parlamentares sincronizados.")
    except Exception as e:
        print(f"Erro parlamentares: {e}")

def sync_all_expenses(client, months_back=2):
    """Sincroniza despesas com deduplicação local."""
    now = datetime.datetime.now()
    try:
        deputies = client.db.table("parlamentares").select("id, nome").execute().data
    except Exception: return

    total = len(deputies)
    print(f"Iniciando sincronização Silver de {total} deputados...")

    for i, dep in enumerate(deputies):
        dep_id, dep_name = dep["id"], dep["nome"]
        expenses_batch = {} # Deduplicação por chave única no lote
        
        for m in range(months_back):
            target = now - datetime.timedelta(days=m * 30)
            raw_expenses = client.get_deputy_expenses(dep_id, target.year, target.month)
            
            for e in raw_expenses:
                cleaned = clean_expense(e, dep_id, target.year, target.month)
                # O dicionário garante que se o id_externo repetir no lote, ele é sobrescrito
                expenses_batch[cleaned["id_externo"]] = cleaned

        if expenses_batch:
            try:
                data = list(expenses_batch.values())
                client.db.table("despesas").upsert(data, on_conflict="id_externo").execute()
                print(f"[{i+1}/{total}] {dep_name}: {len(data)} registros processados.")
            except Exception as e:
                print(f"Erro {dep_name}: {e}")
        
        time.sleep(0.3)

def main():
    client = SentinelAPIClient()
    if not client.db: return
    sync_parliamentarians(client)
    sync_all_expenses(client)

if __name__ == "__main__":
    main()
