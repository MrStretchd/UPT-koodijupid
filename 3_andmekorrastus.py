import pandas as pd
import numpy as np

# SEADISTUSED
SISEND_FAIL = "andmed/koondatud_tabel.xlsx"
VALJUND_FAIL = "andmed/korrektsed_andmed.xlsx"
HALVAD_AASTAD = [1941, 1942, 1943, 1944, 1946, 1947, 1990, 1991, 2015, 2024]
LINNAD = ['Türi', 'Vilsandi']

def puhasta_kliimaandmed():
    print(f"Loen andmeid: {SISEND_FAIL}...")
    df = pd.read_excel(SISEND_FAIL, header=0)
    df.columns = df.columns.str.strip()

    # TÜHJENDA HALVAD AASTAD (aga ära veel kustuta ridu)
    # See on vajalik, et me ei interpoleeriks valedest andmetest, 
    mask_halvad = df['Aasta'].isin(HALVAD_AASTAD)
    df.loc[mask_halvad, LINNAD] = np.nan
    print(f"Määratud tühjaks aastad: {HALVAD_AASTAD}")

    # ÜHTLUSTA KELLAAEG (HH:MM formaati)
    df['Kell (UTC)'] = df['Kell (UTC)'].astype(str).str.strip()
    df['Kell (UTC)'] = df['Kell (UTC)'].apply(lambda x: ':'.join(x.split(':')[:2]) if ':' in x else x)
    df['Kell (UTC)'] = df['Kell (UTC)'].apply(lambda x: x.zfill(5) if len(x) == 4 else x)
    
    # LÜNKADE TÄITMINE (Interpolatsioon + otsad)
    for linn in LINNAD:
        df[linn] = df[linn].interpolate(method='linear', limit=7)
        df[linn] = df[linn].ffill(limit=7) # Venitab aasta lõppu
        df[linn] = df[linn].bfill(limit=7) # Venitab aasta algust

    # KUSTUTA HALVAD AASTAD JA LIIGPÄEVAD
    df_clean = df[~df['Aasta'].isin(HALVAD_AASTAD)].copy()

    df_final = df_clean[~((df_clean['Kuu'] == 2) & (df_clean['Päev'] == 29))].copy()

    puuduvaid_kokku = df_final[LINNAD].isna().sum().sum()
    if puuduvaid_kokku == 0:
        print("\n✅ KONTROLL EDUKAS: Andmestik on puhas ja aastad on 365-päevased!")
        df_final.to_excel(VALJUND_FAIL, index=False)
        print(f"Fail salvestatud: {VALJUND_FAIL}")
    else:
        print(f"\n❌ VIGA: Andmestikus on ikka auke kokku: {puuduvaid_kokku}")
        # Näita esimesi vigaseid ridu
        print(df_final[df_final[LINNAD].isna().any(axis=1)].head())

if __name__ == "__main__":
    puhasta_kliimaandmed()