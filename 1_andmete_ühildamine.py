import pandas as pd

csv_file = 'andmed/uuemad_andmed.csv'
excel_file = 'andmed/ajaloolised_andmed_1941-2003.xlsx'
output_file = 'andmed/koondatud_tabel.xlsx'
UURITAVAD_KELLAAJAD = ["05:00", "11:00", "17:00", "23:00"]

df_excel = pd.read_excel(excel_file, skiprows=2)
df_csv = pd.read_csv(csv_file, sep=';', quotechar='"', decimal=',', encoding='utf-8')

df_csv.columns = ['jaam', 'Aasta', 'Kuu', 'Päev', 'tund', 'vaartus', 'kood', 'nimi_eng']

# Ühtlusame read ja eemaldame võimalikud tühikud
if df_csv['vaartus'].dtype == 'object':
    df_csv['vaartus'] = df_csv['vaartus'].str.replace(',', '.', regex=False)

# Muudame veeru tüübi numbriliseks
df_csv['vaartus'] = pd.to_numeric(df_csv['vaartus'], errors='coerce')

# Teisendame kellaaja ja teeme pivot-tabeli
df_csv['Kell (UTC)'] = df_csv['tund'].astype(str).str.zfill(2) + ':00'
df_csv = df_csv[df_csv['Kell (UTC)'].isin(UURITAVAD_KELLAAJAD)].copy()

df_csv_wide = df_csv.pivot_table(
    index=['Aasta', 'Kuu', 'Päev', 'Kell (UTC)'], 
    columns='jaam', 
    values='vaartus',
    dropna = False
).reset_index()

df_csv_wide.columns.name = None

# Paneme failid kokku
df_final = pd.concat([df_excel, df_csv_wide], ignore_index=True)
df_final = df_final.sort_values(['Aasta', 'Kuu', 'Päev', 'Kell (UTC)'])
df_final.to_excel(output_file, index=False)

print(f"Andmed edukalt koondatud faili: {output_file}")