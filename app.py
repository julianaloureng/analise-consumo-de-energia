from pathlib import Path
import sqlite3

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Caminho para o banco SQLite (criado pelo script de importação)
DB_PATH = Path(r"e:\GitHub-projects\analise-consumo-de-energia\consumo_mensal.db")

st.set_page_config(layout="wide", page_title="Dashboard Consumo de Energia")

@st.cache_data
def get_tables(db_path: str):
    if not Path(db_path).exists():
        return []
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", conn)
    return df['name'].tolist()

@st.cache_data
def get_table_schema(db_path: str, table: str):
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(f"PRAGMA table_info('{table}')", conn)

@st.cache_data
def load_table(db_path: str, table: str, limit: int | None = None):
    with sqlite3.connect(db_path) as conn:
        q = f"SELECT * FROM '{table}'"
        if limit is not None:
            q += f" LIMIT {limit}"
        df = pd.read_sql_query(q, conn)
    # try common datetime conversions
    for col in ['Data', 'DataExcel', 'DataVersao']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

@st.cache_data
def aggregate_consumption_by_month_region(df: pd.DataFrame):
    tmp = df.copy()
    if 'DataExcel' in tmp.columns and tmp['DataExcel'].notna().any():
        tmp['mes'] = tmp['DataExcel'].dt.to_period('M').dt.to_timestamp()
    elif 'Data' in tmp.columns:
        tmp['mes'] = pd.to_datetime(tmp['Data'].astype(str), errors='coerce').dt.to_period('M').dt.to_timestamp()
    else:
        tmp['mes'] = pd.NaT

    if 'Consumo' in tmp.columns and 'Regiao' in tmp.columns:
        agg = tmp.groupby(['mes', 'Regiao'], dropna=True)['Consumo'].sum().reset_index()
        return agg
    else:
        return pd.DataFrame()

def lineplot_pivot(agg_df: pd.DataFrame, title: str = None):
    pivot = agg_df.pivot(index='mes', columns='Regiao', values='Consumo')
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=pivot, dashes=False, ax=ax)
    ax.set_title(title or 'Consumo por Região')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Consumo')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def bar_top_sectors(df: pd.DataFrame, top_n: int = 10):
    if 'SetorIndustrial' in df.columns and 'Consumo' in df.columns:
        agg = df.groupby('SetorIndustrial')['Consumo'].sum().sort_values(ascending=False).head(top_n)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=agg.values, y=agg.index, ax=ax)
        ax.set_xlabel('Consumo')
        ax.set_ylabel('Setor Industrial')
        ax.set_title(f'Top {top_n} Setores por Consumo')
        plt.tight_layout()
        return fig
    return None


def main():
    st.title('Dashboard — Consumo Mensal de Energia')

    if not DB_PATH.exists():
        st.error(f"Banco não encontrado em: {DB_PATH}\nExecute o script de importação primeiro.")
        return

    tables = get_tables(str(DB_PATH))
    st.sidebar.header('Configurações')
    st.sidebar.markdown('Banco: `' + str(DB_PATH) + '`')

    table_choice = st.sidebar.selectbox('Tabela', options=tables)
    st.sidebar.markdown('---')

    if not table_choice:
        st.info('Nenhuma tabela disponível no DB.')
        return

    st.subheader(f'Tabela: {table_choice}')
    if st.sidebar.button('Mostrar esquema'):
        schema = get_table_schema(str(DB_PATH), table_choice)
        st.write(schema)

    sample_limit = st.sidebar.number_input('Linhas de amostra', min_value=5, max_value=1000, value=5)
    df_sample = load_table(str(DB_PATH), table_choice, limit=sample_limit)
    st.write('Amostra da tabela (primeiras linhas):')
    st.dataframe(df_sample)

    # If main consumption table, show time series by region
    if table_choice.upper() in ('CONSUMO_E_NUMCONS_SAM', 'CONSUMO_E_NUMCONS_SAM_UF') or 'Consumo' in df_sample.columns:
        st.markdown('### Série temporal / agregações')
        # load full table lazily (caution: can be large)
        want_full = st.sidebar.checkbox('Carregar tabela completa para análises (pode ser lento)', value=False)
        if want_full:
            df_full = load_table(str(DB_PATH), table_choice)
        else:
            # try to load a reasonable subset for quick analysis
            df_full = load_table(str(DB_PATH), table_choice, limit=10000)

        st.write(f'Dados usados para análise: {len(df_full)} linhas')

        agg = aggregate_consumption_by_month_region(df_full)
        if not agg.empty:
            # allow region filter
            regions = agg['Regiao'].dropna().unique().tolist()
            sel_regions = st.multiselect('Regiões', options=regions, default=regions[:4])
            if sel_regions:
                agg_f = agg[agg['Regiao'].isin(sel_regions)]
                fig = lineplot_pivot(agg_f, title='Consumo por Região (mensal)')
                st.pyplot(fig)
        else:
            st.info('Não foi possível agregar consumo por mês/região — verifique colunas `DataExcel`/`Data`, `Consumo`, `Regiao`.')

        # Top setores (se presentes)
        fig2 = bar_top_sectors(df_full, top_n=10)
        if fig2 is not None:
            st.markdown('### Top setores industriais por consumo')
            st.pyplot(fig2)

    # Quick exploratory: consumo por UF if available
    if 'UF' in df_sample.columns and 'Consumo' in df_sample.columns:
        st.markdown('### Consumo por UF (soma)')
        df_uf = df_sample.groupby('UF', dropna=True)['Consumo'].sum().reset_index().sort_values('Consumo', ascending=False)
        st.dataframe(df_uf)
        fig3, ax3 = plt.subplots(figsize=(10,5))
        sns.barplot(data=df_uf, x='Consumo', y='UF', ax=ax3)
        ax3.set_title('Consumo por UF (amostra)')
        st.pyplot(fig3)

    st.sidebar.write('')
    st.sidebar.markdown('Feito com :heart: — Streamlit + Seaborn')


if __name__ == '__main__':
    main()
