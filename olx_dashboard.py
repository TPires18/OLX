
# olx_dashboard.py

"""
Instruções:

1. Instala os pacotes necessários:
   pip install requests beautifulsoup4 pandas streamlit

2. Corre o dashboard com:
   streamlit run olx_dashboard.py
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import re

# Função para extrair o valor numérico do preço
def extrair_preco(texto):
    preco = re.findall(r'\d+', texto.replace('.', ''))
    return int(''.join(preco)) if preco else None

# Função robusta de scraping com fallback
def extrair_anuncios_olx(paginas=3):
    anuncios = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        for pagina in range(1, paginas + 1):
            url = f"https://www.olx.pt/carros/q-vw-golf-vii/?page={pagina}"
            resposta = requests.get(url, headers=headers, timeout=10)
            sopa = BeautifulSoup(resposta.text, 'html.parser')
            links = sopa.select('a[data-testid="listing-ad-title"]')

            for link_tag in links:
                titulo = link_tag.get_text(strip=True)
                link = "https://www.olx.pt" + link_tag.get("href", "")
                preco_tag = link_tag.find_parent().find_next("p")
                preco = extrair_preco(preco_tag.text) if preco_tag else None

                anuncios.append({
                    "Título": titulo,
                    "Preço (€)": preco,
                    "Link": link
                })
    except Exception as e:
        st.error(f"Erro ao aceder aos dados do OLX: {e}")
        return pd.DataFrame()

    return pd.DataFrame(anuncios)

# Dados simulados como fallback
def dados_simulados():
    return pd.DataFrame([
        {"Título": "VW Golf VII 1.6 TDI", "Preço (€)": 11200, "Link": "#"},
        {"Título": "VW Golf VII 2.0 GTD", "Preço (€)": 12990, "Link": "#"},
        {"Título": "VW Golf VII 1.6 TDI Comfortline", "Preço (€)": 9990, "Link": "#"},
        {"Título": "VW Golf VII 1.0 TSI", "Preço (€)": 8750, "Link": "#"},
    ])

# Interface do Streamlit
st.set_page_config(page_title="Análise OLX - VW Golf VII", layout="wide")
st.title("🔍 Análise de VW Golf VII no OLX")
st.markdown("Este painel identifica possíveis oportunidades de negócio com base nos anúncios mais recentes.")

num_paginas = st.slider("Quantas páginas OLX queres analisar?", 1, 10, 3)

if st.button("🔄 Atualizar Anúncios"):
    df = extrair_anuncios_olx(paginas=num_paginas)

    if df.empty:
        st.warning("⚠️ Não foi possível obter dados reais. A mostrar dados simulados.")
        df = dados_simulados()

    preco_medio = df["Preço (€)"].mean()
    preco_min = df["Preço (€)"].min()
    preco_max = df["Preço (€)"].max()

    st.subheader("📊 Estatísticas de Preço")
    st.metric("Preço Médio", f"{preco_medio:,.0f} €")
    st.metric("Mais Barato", f"{preco_min:,.0f} €")
    st.metric("Mais Caro", f"{preco_max:,.0f} €")

    st.subheader("📋 Anúncios")
    st.dataframe(df)

    st.subheader("💡 Oportunidades abaixo da média")
    oportunidades = df[df["Preço (€)"] < preco_medio * 0.9]
    st.dataframe(oportunidades if not oportunidades.empty else pd.DataFrame([{"Mensagem": "Sem oportunidades abaixo da média."}]))
else:
    st.info("Clica em 'Atualizar Anúncios' para iniciar a análise.")
