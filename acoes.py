import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt



acoes = ['AZUL4.SA','B3SA3.SA','BBDC3.SA','DIRR3.SA','ELET3.SA','GGBR4.SA','KLBN4.SA','PETR4.SA','RENT3.SA','VALE3.SA','WEGE3.SA','MELI34.SA',
            'HGRE11.SA','HSML11.SA','KFOF11.SA','KNSC11.SA','MXRF11.SA','RBRR11.SA','RZTR11.SA','VILG11.SA','XPSF11.SA']

# data de inicio, vou contar somente 2024
data_inicio = '2024-01-01'

#data final sempre será hoje

data_final = datetime.today().strftime('%Y-%m-%d')

# funcao para coletar e processar os dados
@st.cache_data
def coletar_dados(acoes, data_inicio, data_final):
    carteira = []
    for acao in acoes:
        # Criar um objeto Ticker para a ação
        ticker = yf.Ticker(acao)
        
        # Obter informações sobre a ação
        info = ticker.info
        nome_empresa = info.get('longName', 'Informação Não Disponível')

        # Baixar dados históricos da ação
        dados = yf.download(acao, start=data_inicio, end=data_final)
        if dados.empty:
            continue

        dados.reset_index(inplace=True)
        dados['Diferenca %'] = ((dados['Close'] - dados['Open']) / dados['Open']) * 100
        dados['Diferenca R$'] = dados['Close'] - dados['Open']
        dados.rename(columns={'Date': 'Dia', 'Open': 'Preco Abertura', 'Close': 'Preco Fechamento'}, inplace=True)
        
        # Adicionar as colunas 'Ação' e 'Nome Empresa'
        dados['Ação'] = acao
        dados['Nome Empresa'] = nome_empresa

        dados = dados[['Ação', 'Nome Empresa', 'Dia', 'Preco Abertura', 'Preco Fechamento', 'Diferenca %', 'Diferenca R$']]
        carteira.append(dados)

    # Concatenar todos os dataframes da carteira
    titulos = pd.concat(carteira, ignore_index=True)
    return titulos

# A variável 'patrimonio' está correta aqui
patrimonio = coletar_dados(acoes, data_inicio, data_final)

patrimonio['Dia'] = patrimonio['Dia'].dt.date


with st.sidebar:
    st.subheader('Seleção de ações')
    fAcoes = st.selectbox(
        'Selecione um ticker: ',
        options=patrimonio['Ação'].unique()
    )

    patrimonio_filtrado = patrimonio.loc[(
        patrimonio['Ação'] == fAcoes)
    ]

    st.subheader('Ação por nome:')
    fNomes = st.selectbox(
        'Escolha uma ação: ',
        options=patrimonio_filtrado['Nome Empresa'].unique()
    )

st.header('Dados históricos de ações 2024')
st.markdown('**Ação selecionada** ' + fNomes)



#st.line_chart( patrimonio_filtrado, x='Dia', y='Preco Fechamento')



base = alt.Chart(patrimonio_filtrado).encode(x='Dia')

bar = base.mark_bar().encode(y='Preco Fechamento')

line = base.mark_line(color='red').encode(y='Diferenca %')

chart = (bar + line).properties(width=600).interactive()

st.altair_chart(chart)

patrimonio_filtrado   

