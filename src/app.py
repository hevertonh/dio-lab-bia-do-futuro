
import json
import streamlit as st
import pandas as pd
import requests

# =============== CONFIGURAÇÃO ==================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"

# ================ CARREGAR DADOS ===================
perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))

# ================ MONTAR CONTEXTO ==================
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']},
OBJETIVO: {perfil['objetivo_principal']}
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

## System Prompt

SYSTEM_PROMPT = """Você é o Heve, um educador financeiro.

OBJETIVO: 
Seu objetivo é ensinar conceitos de finanças de forma simples.

REGRAS:
- Sempre baseie suas respostas nos dados fornecidos
- Nunca invente informações financeiras
- Se não souber algo, admita e ofereça alternativas
- Sempre pergunte se o cliente entendeu
"""
# ============= CHAMAR OLLAMA ==============
def perguntar(msg):
    prompt = f"{SYSTEM_PROMPT}\n\nCONTEXTO DO CLIENTE:\n{contexto}\n\nPergunta: {msg}"
    
    try:
        r = requests.post(OLLAMA_URL, json={"model": MODELO, "prompt": prompt, "stream": False})
        dados_da_resposta = r.json()
        
        # Se houver erro no Ollama, ele vira um KeyError aqui se não checarmos
        if 'response' in dados_da_resposta:
            return dados_da_resposta['response']
        else:
            # Caso o Ollama mande um erro (ex: modelo não encontrado)
            erro_ollama = dados_da_resposta.get('error', 'Erro desconhecido')
            return f"Erro no Ollama: {erro_ollama}"
            
    except Exception as e:
        return f"Não consegui conectar ao Ollama. Verifique se ele está aberto! Erro: {e}"

# ================= INTERFACE =================
st.title("Sou Heve, o Educador Financeiro")

# Aqui você volta para a borda esquerda para indicar que a função acabou
if pergunta := st.chat_input("Sua dúvida sobre finanças..."):
    # O código dentro do IF também precisa de recuo!
    st.chat_message("user").write(pergunta)
    with st.spinner("..."):
        st.chat_message("assistant").write(perguntar(pergunta))
        
        


 