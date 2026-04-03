import pandas as pd
import numpy as np

# -----------------------------------------------------------
# SEADISTUSED
# -----------------------------------------------------------
SISEND_FAIL = "andmed/korrektsed_andmed.xlsx"
VALJUND_FAIL = "analüüsi_andmed/paeva_keskmised_4kella.xlsx"

VEERG_KELL = 'Kell (UTC)'
LINNAD = ['Türi', 'Vilsandi']

STANDARD_KELLAD = ["05:00", "11:00", "17:00", "23:00"]

def arvuta_keskmised():
    print(f"Loen andmeid failist: {SISEND_FAIL}...")
    df = pd.read_excel(SISEND_FAIL, header=0)
    df.columns = df.columns.str.strip()
    if df[VEERG_KELL].dtype == object:
        df[VEERG_KELL] = df[VEERG_KELL].str.strip()

    # Sajandi keskel kellajad vaatlustel muutusid, nii et siin on tabel, mis paneb vastamisi vanad ja uued kellaajad
    kella_reeglid = {
        "05:00": ("05:00", 1), "06:00": ("05:00", 2),
        "11:00": ("11:00", 1), "12:00": ("11:00", 2),
        "17:00": ("17:00", 1), "18:00": ("17:00", 2),
        "23:00": ("23:00", 1), "00:00": ("23:00", 2)
    }

    df = df[df[VEERG_KELL].isin(kella_reeglid.keys())].copy()

    df['Standard_Kell'] = df[VEERG_KELL].map(lambda x: kella_reeglid[x][0])
    df['Prioriteet'] = df[VEERG_KELL].map(lambda x: kella_reeglid[x][1])

    print("Eemaldan dublikaadid (eelistades õigeid kellaaegu)...")
    
    df = df.sort_values(by=['Aasta', 'Kuu', 'Päev', 'Standard_Kell', 'Prioriteet'])

    df_clean = df.drop_duplicates(subset=['Aasta', 'Kuu', 'Päev', 'Standard_Kell'], keep='first').copy()

    grupeeritud = df_clean.groupby(['Aasta', 'Kuu', 'Päev'])[LINNAD].agg(['mean', 'count'])

    tulemus = pd.DataFrame()
    tulemus['Aasta'] = grupeeritud.index.get_level_values(0)
    tulemus['Kuu'] = grupeeritud.index.get_level_values(1)
    tulemus['Päev'] = grupeeritud.index.get_level_values(2)

    for linn in LINNAD:
        keskmine = grupeeritud[linn]['mean']
        kogus = grupeeritud[linn]['count']

        tulemus[linn] = np.where(kogus == 4, keskmine, np.nan)
        
        praak = ((kogus < 4) & (kogus > 0)).sum()
        if praak > 0:
            print(f"⚠️  {linn}: {praak} päeva on puudulike andmetega.")

    tulemus.to_excel(VALJUND_FAIL, index=False)
    print(f"\n✅ Valmis! Tulemus: {VALJUND_FAIL}")

if __name__ == "__main__":
    arvuta_keskmised()