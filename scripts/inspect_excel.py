import pandas as pd
from pathlib import Path

FILE = Path(r"e:\GitHub-projects\analise-consumo-de-energia\Dados_abertos_Consumo_Mensal.xlsx")

if not FILE.exists():
    print(f"Excel file not found at {FILE}")
    raise SystemExit(1)

print(f"Reading: {FILE}")
xls = pd.read_excel(FILE, sheet_name=None)
print("Found sheets:", list(xls.keys()))

for name, df in xls.items():
    print("\n" + "-" * 60)
    print(f"Sheet: {name}")
    print(f"Shape: {df.shape}")
    print("Dtypes:\n", df.dtypes)
    print("First rows:\n", df.head(5).to_string(index=False))
