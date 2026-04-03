import pandas as pd

faili_nimi = "andmed/koondatud_tabel.xlsx" 

df = pd.read_excel(faili_nimi, header=0)
df.columns = df.columns.str.strip()

df['puudub'] = df[['Türi', 'Vilsandi']].isna().any(axis=1)

# Filtreerime välja ainult need read, kus midagi puudub
puudujaaagid = df[df['puudub']]

# 3. Loendame, mitu päeva igas aastas puudu on
statistika = puudujaaagid.groupby('Aasta').size()

print("Aasta  | Puuduvad lüngad")
print("-------|----------------")
print(statistika)