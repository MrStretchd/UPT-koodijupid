import pandas as pd
import os

SISEND_FAIL = "analüüsi_andmed/aastate_nadala_keskmised_oktoober.csv"
VÄLJUNDID = {
    'Türi': "analüüsi_andmed/turi_ekstreemsused_oktoober.csv",
    'Vilsandi': "analüüsi_andmed/vilsandi_ekstreemsused_oktoober.csv"
}

def eralda_lihtsalt():
    if not os.path.exists(SISEND_FAIL):
        print(f"Puudub sisendfail: {SISEND_FAIL}")
        return

    print(f"Loen andmeid: {SISEND_FAIL}...")
    df = pd.read_csv(SISEND_FAIL, sep=';', encoding='utf-8-sig')

    for jaam, valjund_fail in VÄLJUNDID.items():
        veerg = f"{jaam}_Keskmine"
        
        idx_max = df.groupby('Hüdro_Aasta')[veerg].idxmax()
        df_max = df.loc[idx_max].copy()
        df_max['Tüüp'] = 'Soojem'
       
        idx_min = df.groupby('Hüdro_Aasta')[veerg].idxmin()
        df_min = df.loc[idx_min].copy()
        df_min['Tüüp'] = 'Külmem'

        koond = pd.concat([df_max, df_min]).sort_values('Hüdro_Aasta')

        loplik = koond[['Hüdro_Aasta', 'Tüüp', 'Periood_Nr', 'Kuupäevad', veerg]]
        
        loplik.to_csv(valjund_fail, index=False, sep=';', encoding='utf-8-sig')
        print(f" -> Valmis: {jaam} ({len(loplik)} rida)")

if __name__ == "__main__":
    eralda_lihtsalt()