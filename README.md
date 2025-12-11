# analise-consumo-de-energia

Projeto para importar dados de consumo de energia (arquivo Excel público) para um banco SQLite
e oferecer ferramentas de exploração e visualização via Jupyter Notebook e um dashboard Streamlit.

## Conteúdo do repositório
- `Dados_abertos_Consumo_Mensal.xlsx` - arquivo Excel fonte (não versionado aqui se for grande).
- `scripts/import_to_sqlite.py` - script que importa todas as sheets do Excel para `consumo_mensal.db` (SQLite).
- `scripts/inspect_excel.py` e `scripts/inspect_excel_fast.py` - scripts úteis para inspecionar sheets e amostras.
- `consumo_mensal.db` - arquivo de banco SQLite gerado pelo importador (gerado localmente após executar o importador).
- `notebooks/analise_sqlite.ipynb` - notebook Jupyter com consultas e análise rápida das tabelas do SQLite.
- `app.py` - aplicativo Streamlit que cria um dashboard interativo (usa `seaborn` para visualizações).

## Pré-requisitos
- Python 3.10+ (o projeto foi testado com 3.10)
- Windows (instruções abaixo usam PowerShell e o venv criado pelo projeto)

O repositório contém um ambiente virtual sugerido em `.venv` (quando criado localmente). As instruções abaixo usam o Python desse venv quando disponível.

## Instalação (PowerShell)
Abra um terminal PowerShell na raiz do projeto e execute:

```powershell
# (opcional) criar venv se ainda não existir
python -m venv .venv

# usar o python do venv para instalar dependências
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install pandas openpyxl matplotlib seaborn streamlit jupyterlab ipykernel
```

Observação: se você preferir não usar o venv local, substitua `.venv\Scripts\python.exe` por `python` conforme sua configuração.

## Importar o Excel para SQLite
1. Coloque `Dados_abertos_Consumo_Mensal.xlsx` na raiz do repositório (ou atualize o caminho em `scripts/import_to_sqlite.py`).
2. Execute o importador:

```powershell
.venv\Scripts\python.exe scripts\import_to_sqlite.py
```

O script criará (ou sobrescreverá) `consumo_mensal.db` na raiz do projeto. Se o arquivo for muito grande, o script pode demorar — há variantes de inspeção (`inspect_excel_fast.py`) para análise rápida.

## Notebook de análise
Para abrir o notebook e inspecionar os dados:

```powershell
.venv\Scripts\python.exe -m jupyter lab
```

Abra `notebooks/analise_sqlite.ipynb` no JupyterLab. Garanta que o kernel selecionado seja o Python do venv (use `analise-consumo-venv` se você registrou um kernel).

## Dashboard Streamlit
Para executar o dashboard interativo (`app.py`):

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

O app permite selecionar tabelas do banco `consumo_mensal.db`, inspecionar esquema/amostras, agregar consumo por mês e região, visualizar top setores industriais e ver consumo por UF.

## Dicas e próximos passos
- Se o importador foi interrompido parcialmente, reexecute `scripts/import_to_sqlite.py` para completar a importação. Para arquivos muito grandes, considere ler e inserir por blocos.
- Posso adicionar um `requirements.txt` e um comando `Makefile`/`ps1` para facilitar a configuração automática — diga se quer que eu adicione.
- Posso também estender o `app.py` com filtros por período, exportação CSV e modelos pré-definidos de consultas.

## Licença
Ver arquivo `LICENSE` (se houver) para informações sobre licenciamento.

---
Desenvolvido para análise de consumo de energia — scripts e app foram adicionados para facilitar a ingestão e visualização dos dados.
# analise-consumo-de-energia