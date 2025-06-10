
# olx_dashboard.py

"""
Instruções:

1. Instala os pacotes necessários (idealmente num ambiente virtual):
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

# Função para extrair dados de N páginas do OLX
def extrair_anuncios_olx(paginas=3):
    anuncios = []
    for pagina in range(1, paginas + 1):
        url = f"https://www.olx.pt/carros/q-vw-golf-vii/?page={pagina}"
        resposta = requests.get(url)
        sopa = BeautifulSoup(resposta.text, 'html.parser')
        blocos = sopa.find_all('div', class_='css-1sw7q4x')  # Pode precisar de atualização futura

        for bloco in blocos:
            titulo_tag = bloco.find('h6')
            preco_tag = bloco.find('p', class_='css-10b0gli')
            link_tag = bloco.find('a', href=True)

            if titulo_tag and preco_tag and link_tag:
                titulo = titulo_tag.text.strip()
                preco = extrair_preco(preco_tag.text.strip())
                link = "https://www.olx.pt" + link_tag["href"]

                anuncios.append({
                    "Título": titulo,
                    "Preço (€)": preco,
                    "Link": link
                })

    return pd.DataFrame(anuncios)

# Construir a interface do Streamlit
st.set_page_config(page_title="Análise OLX - VW Golf VII", layout="wide")
st.title("🔍 Análise de VW Golf VII no OLX")
st.markdown("Este dashboard identifica possíveis oportunidades de negócio com base nos anúncios mais recentes.")

# Parâmetro: número de páginas a explorar
num_paginas = st.slider("Quantas páginas OLX queres analisar?", 1, 10, 3)

# Botão para atualizar
if st.button("🔄 Atualizar Anúncios"):
    df = extrair_anuncios_olx(paginas=num_paginas)

    if not df.empty:
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
        st.warning("Não foi possível obter dados. Tenta novamente mais tarde.")
else:
    st.info("Clica em 'Atualizar Anúncios' para iniciar a análise.")
