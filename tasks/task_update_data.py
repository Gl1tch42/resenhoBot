import json
import time
from tasks.obter_jogos_brasileirao import obter_jogos_brasileirao # Sua função que já funciona

def atualizar_arquivo():
    print("🔄 Atualizando dados do Brasileirão...")
    try:
        jogos = obter_jogos_brasileirao()
        if jogos:
            with open('data\dados_jogos.json', 'w', encoding='utf-8') as f:
                json.dump(jogos, f, ensure_ascii=False, indent=4)
            print("✅ Arquivo atualizado com sucesso!")
        else:
            print("⚠️ Falha ao obter jogos, tentando novamente no próximo ciclo.")
    except Exception as e:
        print(f"❌ Erro na task: {e}")
