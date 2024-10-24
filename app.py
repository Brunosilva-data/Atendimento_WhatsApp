import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Operação CSF - WhatsApp", layout="wide")

# URL do arquivo CSV no GitHub
csv_url = "https://raw.githubusercontent.com/Brunosilva-data/Atendimento_WhatsApp/main/Report_WhatsApp_2023_2024.csv"

# Tente carregar o CSV do GitHub
try:
    df = pd.read_csv(csv_url)
except Exception as e:
    st.error(f"Erro ao carregar o arquivo CSV: {e}")

# Criar abas horizontais
tab1, tab2 = st.tabs(["Principal", "Wiki"])

# Conteúdo da aba "Principal"
with tab1:
    st.title("Atendimento CSF - WhatsApp")

    st.markdown("""
    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
        Este dashboard tem como objetivo analisar o desempenho e volume de atendimentos via WhatsApp, expurgando registros de "Atendimento" e "ativo" para focar em categorias e assuntos mais relevantes, proporcionando uma análise mais precisa e objetiva.
    </div>
    """, unsafe_allow_html=True)

    # Ajuste no formato da data para dia/mês/ano
    df['Data de abertura'] = pd.to_datetime(df['Data de abertura'], dayfirst=True)

    # Determinar a data inicial e a data final disponíveis no CSV
    data_inicial = df['Data de abertura'].min()
    data_final = df['Data de abertura'].max()

    # Obter valores únicos da coluna "Papel do criador" para o selectbox
    opcoes_operacao = df['Papel do criador'].unique().tolist()

    # Organizar os elementos horizontalmente com larguras iguais para todas as caixas
    col1, col2, col3 = st.columns(3)

    with col1:
        opcao = st.selectbox("Selecione a operação que deseja analisar:", opcoes_operacao)

    with col2:
        start_date = st.date_input("Selecione a Data Inicial:", value=data_inicial, min_value=data_inicial, max_value=data_final, key='start_date', format='DD/MM/YYYY')

    with col3:
        end_date = st.date_input("Selecione a Data Final:", value=data_final, min_value=data_inicial, max_value=data_final, key='end_date', format='DD/MM/YYYY')

    # Filtrar os dados com base na seleção de datas e operação
    df_filtered = df[(df['Data de abertura'] >= pd.to_datetime(start_date)) & (df['Data de abertura'] <= pd.to_datetime(end_date))]

    df_filtered = df_filtered[df_filtered['Papel do criador'] == opcao]

    # Agrupar os dados por mês e contar volumes de atendimentos
    df_grouped = df_filtered.groupby(pd.Grouper(key='Data de abertura', freq='M')).size()
    df_selected = pd.DataFrame({"Volume de Atendimentos": df_grouped})

    def traduzir_mes(mes):
        meses_portugues = {
            'Jan': 'Jan', 'Feb': 'Fev', 'Mar': 'Mar', 'Apr': 'Abr',
            'May': 'Mai', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Ago',
            'Sep': 'Set', 'Oct': 'Out', 'Nov': 'Nov', 'Dec': 'Dez'
        }
        return meses_portugues.get(mes, mes)

    df_selected.index = df_selected.index.strftime('%b %Y').map(traduzir_mes)

    if not df_selected.empty:
        # Gráfico de área
        fig_area = go.Figure()

        fig_area.add_trace(go.Scatter(
            x=df_selected.index,
            y=df_selected['Volume de Atendimentos'],
            fill='tozeroy',
            mode='none',
            name=f'{opcao}',
            fillcolor='rgba(30, 144, 255, 0.5)'
        ))

        fig_area.update_layout(
            title=f"Volume de Atendimentos - {opcao}",
            xaxis_title="Mês",
            yaxis_title="Volume de Atendimentos",
            plot_bgcolor='rgba(0, 0, 0, 0.1)',
            paper_bgcolor='rgba(0, 0, 0, 0.1)',
            font=dict(color="white"),
            showlegend=True,
            hovermode="x",
            xaxis=dict(
                showgrid=True,
                gridcolor='gray',
                gridwidth=0.5,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='gray',
                gridwidth=0.5,
            ),
        )

        # Exibir o gráfico de área no Streamlit
        st.plotly_chart(fig_area, use_container_width=True)

        # --- Gráfico de linha comparativo para todas as operações selecionadas ---
        fig_line = go.Figure()

        for operacao in opcoes_operacao:
            df_operacao = df[(df['Papel do criador'] == operacao) & 
                             (df['Data de abertura'] >= pd.to_datetime(start_date)) & 
                             (df['Data de abertura'] <= pd.to_datetime(end_date))]

            # Agrupar os dados por mês para cada operação
            df_operacao_grouped = df_operacao.groupby(pd.Grouper(key='Data de abertura', freq='M')).size()

            if not df_operacao_grouped.empty:
                fig_line.add_trace(go.Scatter(
                    x=df_operacao_grouped.index.strftime('%b %Y'),
                    y=df_operacao_grouped,
                    mode='lines',
                    name=operacao,
                ))

        fig_line.update_layout(
            title="Comparação de Volume de Atendimentos - Operações",
            xaxis_title="Mês",
            yaxis_title="Volume de Atendimentos",
            plot_bgcolor='rgba(0, 0, 0, 0.1)',
            paper_bgcolor='rgba(0, 0, 0, 0.1)',
            font=dict(color="white"),
            showlegend=True,
            hovermode="x unified",
            xaxis=dict(
                showgrid=True,
                gridcolor='gray',
                gridwidth=0.5,
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='gray',
                gridwidth=0.5,
            ),
        )

        # Exibir o gráfico de linha comparativo no Streamlit
        st.plotly_chart(fig_line, use_container_width=True)

# Conteúdo da aba "Wiki"
with tab2:
    st.title("Wiki")

    st.markdown("""
    <strong>Os filtros utilizados para extrair a base de dados foram os seguintes:</strong><br>
    <ul>
        <li><strong>Unidade:</strong> Igual a "CSF".</li>
        <li><strong>Papel do criador:</strong> Igual a "Assistente CSF", "Assistente CSF CM", "Assistente CSF Ajuda Quality".</li>
        <li><strong>Origem do caso:</strong> Igual a "WhatsApp".</li>
        <li><strong>Categoria:</strong> Diferente de "Atendimento".</li>
        <li><strong>Assunto:</strong> Não contém "Atendimento".</li>
        <li><strong>Assunto:</strong> Não contém "Ativo".</li>
        <li><strong>Categorização:</strong> Não contém "Ativo".</li>
        <li><strong>Motivo:</strong> Não contém "Ativo".</li>
    </ul>

    <strong>Indicadores:</strong>
    <ul>
        <li><strong>Porcentagem de Variação:</strong> É a variação entre o primeiro e o último período selecionado, indicando a diferença percentual no volume de atendimentos.</li>
        <li><strong>Menor Volume de Atendimentos:</strong> Mostra o menor volume de atendimentos registrado no período selecionado.</li>
        <li><strong>Maior Volume de Atendimentos:</strong> Indica o maior volume de atendimentos registrado no período selecionado.</li>
    </ul>
    """, unsafe_allow_html=True)
# Ocultar o menu de opções padrão (ícones de fork, GitHub, Manage app, etc.)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stDecoration"] {visibility: hidden;}  /* Esconde o botão "Manage app" */
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

