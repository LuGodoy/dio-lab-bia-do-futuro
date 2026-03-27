#============== VERSÃO 3 (FINAL) ==============
import os
import json
import re
import pandas as pd
import requests
import streamlit as st

# ============ CONFIGURAÇÃO ============
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"   
PASTA_TXT = "data/txt_otimizado" 

# ============ CARREGAR DADOS OTIMIZADOS ============
@st.cache_data
def carregar_dados():
    with open(f"{PASTA_TXT}/perfil_investidor.txt", 'r', encoding='utf-8') as f:
        perfil = json.load(f)

    with open(f"{PASTA_TXT}/produtos_financeiros.txt", 'r', encoding='utf-8') as f:
        produtos = json.load(f)

    with open(f"{PASTA_TXT}/transacoes.txt", 'r', encoding='utf-8') as f:
        transacoes = pd.DataFrame(json.load(f))

    historico = pd.read_csv(
        f"{PASTA_TXT}/historico_atendimento.txt", 
        sep='|', 
        names=['data', 'canal', 'tema', 'status'],
        header=None
    )
    return perfil, produtos, transacoes, historico

perfil, produtos, transacoes, historico = carregar_dados()

# ============ NORMALIZAR MOEDA & FORMATO ============
def normalizar_resposta(texto):
    # 1. Limpa espaços unicode invisíveis
    texto = re.sub(r'[\u00A0\u2000-\u200D\u202F\uFEFF]', ' ', texto)

    # 2. Garante o formato "R$ 1.234,56" e aplica negrito automático nos valores
    # Esta regex detecta números no formato brasileiro com ou sem R$ na frente
    texto = re.sub(r'(?:R\$\s*|R\s*|(?<=\s))(\d{1,3}(?:\.\d{3})*,\d{2})', r'**R$ \1**', texto)

    # 3. Garante que não haja espaços excessivos após o R$
    texto = re.sub(r'R\$\s+', 'R$ ', texto)
    
    return texto.strip()

# ============ MONTAR CONTEXTO ============
contexto_transacoes = transacoes.to_csv(index=False, sep='|', header=False)

contexto = f"""
CLIENTE: {perfil.get('nome')}, {perfil.get('idade')} anos, perfil {perfil.get('perfil_investidor')}
OBJETIVO: {perfil.get('objetivo_principal')}
PATRIMÔNIO: R$ {perfil.get('patrimonio_total')} | RESERVA: R$ {perfil.get('reserva_emergencia_atual')}

TRANSAÇÕES (Data|Desc|Cat|Val|Tipo):
{contexto_transacoes}

PRODUTOS DISPONÍVEIS (Compacto):
{json.dumps(produtos, ensure_ascii=False)}
"""

# ============ SYSTEM PROMPT (ESTRUTURADO) ============
SYSTEM_PROMPT = """Você é a Fia, uma assistente financeira amigável e didática.

REGRAS DE FORMATAÇÃO (OBRIGATÓRIO):
1. Use Markdown: Use '###' para títulos e '*' para listas de tópicos.
2. Destaque: Use **negrito** para categorias e valores financeiros.
3. Estrutura de Resposta:
   - Comece com uma frase direta em negrito sobre o que foi identificado.
   - Use uma lista para detalhar itens ou subcategorias.
   - Termine com um '💡 Insight' curto.

REGRAS DE CONTEÚDO:
- NUNCA recomende investimentos específicos.
- Use "valor_formatado" dos dados quando disponível.
- Se a pergunta não for sobre finanças, decline educadamente.
- Responda de forma sucinta.
"""

# ============ FUNÇÃO DE PERGUNTA ============
def perguntar(msg):
    try:
        # Pega apenas as últimas 4 mensagens para o contexto da IA
        memoria_recente = st.session_state.historico_chat[-4:]
        historico_formatado = "\n".join([f"{m['role']}: {m['content']}" for m in memoria_recente])

        prompt = f"""
        {SYSTEM_PROMPT}

        CONTEXTO DO CLIENTE:
        {contexto}

        HISTÓRICO DA CONVERSA:
        {historico_formatado}

        Pergunta: {msg}
        """

        r = requests.post(OLLAMA_URL, 
                        json={"model": MODELO, "prompt": prompt, "stream": False}
        )
        r.raise_for_status()
        return r.json().get("response", "Erro ao gerar resposta")
    
    except Exception as e:
        return f"Erro ao conectar o modelo: {e}"

# ============ PROCESSAMENTO PARA O DASHBOARD ============

# 1. Garantir tipos e limpeza
transacoes['valor'] = pd.to_numeric(transacoes['valor'], errors='coerce')
transacoes['categoria'] = transacoes['categoria'].str.strip().str.lower()
transacoes['tipo'] = transacoes['tipo'].str.strip().str.lower()
transacoes['data'] = pd.to_datetime(transacoes['data'], errors='coerce')

# 2. Criar colunas temporais
transacoes['mes'] = transacoes['data'].dt.to_period('M').astype(str)
data_inicio = transacoes['data'].min()
data_fim = transacoes['data'].max()

def formatar_data_br(dt):
    return dt.strftime('%d/%m/%Y') if pd.notnull(dt) else ''

periodo = f"{formatar_data_br(data_inicio)} a {formatar_data_br(data_fim)}"

# 3. Filtrar Saídas e Agrupar
df_gastos = transacoes[transacoes['tipo'] == 'saida']
resumo_categorias = df_gastos.groupby('categoria')['valor'].sum().sort_values(ascending=False)
gastos_mensais = df_gastos.groupby('mes')['valor'].sum().sort_index()
ultimos_3 = gastos_mensais.tail(3)

# 4. Função de Formatação Monetária
def formatar_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
# ============ AJUSTE DE LARGURA DA SIDEBAR ============
st.markdown(
    """
    <style>
        /* Ajusta a largura da sidebar (ex: 400px) */
        [data-testid="stSidebar"] {
            width: 400px;
            max-width: 1200px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =================== PAINEL VISUAL (SIDEBAR) ==========================

st.sidebar.header("📊 Dashboard Financeiro")
st.sidebar.caption(f"Período: {periodo}")

# 🔹 1. MÉTRICAS PRINCIPAIS COM DELTA
total_gasto_periodo = resumo_categorias.sum()

# Cálculo do Delta (Último mês vs Mês anterior)
if len(ultimos_3) >= 2:
    ultimo_mes_valor = ultimos_3.iloc[-1]
    mes_anterior_valor = ultimos_3.iloc[-2]
    # Se o gasto subiu, o delta é positivo. 
    delta_percentual = ((ultimo_mes_valor / mes_anterior_valor) - 1) * 100
else:
    ultimo_mes_valor = ultimos_3.iloc[-1] if not ultimos_3.empty else 0
    delta_percentual = 0

st.sidebar.metric(
    label="Total no Período", 
    value=formatar_real(total_gasto_periodo)
)

st.sidebar.metric(
    label="Último Mês Registrado", 
    value=formatar_real(ultimo_mes_valor),
    delta=f"{delta_percentual:.1f}% vs mês anterior",
    delta_color="inverse" # Vermelho se aumentar gasto, Verde se diminuir
)

st.sidebar.divider()

# 🔹 2. GRÁFICO DE EVOLUÇÃO (TENDÊNCIA)
st.sidebar.subheader("Tendência Mensal")
st.sidebar.area_chart(gastos_mensais)

# 🔹 3. COMPOSIÇÃO POR CATEGORIA
st.sidebar.subheader("Gastos por Categoria")
st.sidebar.bar_chart(resumo_categorias)

st.sidebar.divider()

# ============ INTERFACE PRINCIPAL ============
st.title("✨💲✨ Fia, Assistente Financeira")

if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

# Exibe o histórico
for msg in st.session_state.historico_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do Usuário
if pergunta := st.chat_input("Sua dúvida sobre finanças..."):
    # Adiciona e exibe pergunta do usuário
    st.session_state.historico_chat.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.spinner("Fia está analisando..."):
        resposta_bruta = perguntar(pergunta)
        resposta_final = normalizar_resposta(resposta_bruta)

    # Adiciona e exibe resposta da Fia
    st.session_state.historico_chat.append({"role": "assistant", "content": resposta_final})
    with st.chat_message("assistant"):
        st.markdown(resposta_final)

# Limita o histórico para não sobrecarregar o st.session_state em sessões longas
if len(st.session_state.historico_chat) > 10:
    st.session_state.historico_chat = st.session_state.historico_chat[-10:]