import pandas as pd
import os

SISEND_FAIL = "analüüsi_andmed/paeva_keskmised_4kella.xlsx"
VALJUND_FAIL = "analüüsi_andmed/aastate_nadala_keskmised_oktoober.csv"

def arvuta_kiirelt():
    if not os.path.exists('analüüsi_andmed'):
        os.makedirs('analüüsi_andmed')

    df = pd.read_excel(SISEND_FAIL)
    df.columns = df.columns.str.strip()

    df['Date'] = pd.to_datetime(df[['Aasta', 'Kuu', 'Päev']].rename(columns={'Aasta':'year', 'Kuu':'month', 'Päev':'day'}), errors='coerce')
    df = df.sort_values('Date').reset_index(drop=True)
    df = df[~((df['Kuu'] == 2) & (df['Päev'] == 29))].copy()

    # Tee vahepealne aasta 2025/2025
    df['H_Algus_Aasta'] = df.apply(lambda x: x['Aasta'] if x['Kuu'] >= 10 else x['Aasta'] - 1, axis=1)
    df['Hüdro_Aasta'] = df['H_Algus_Aasta'].astype(str) + "/" + (df['H_Algus_Aasta'] + 1).astype(str)

    koik_h_aastad = set(df['Hüdro_Aasta'].unique())

    # Perioodide leidmine
    grupeeritud = df.groupby('Hüdro_Aasta')
    df['Türi_Keskmine'] = grupeeritud['Türi'].transform(lambda x: x.rolling(window=7).mean().shift(-6))
    df['Vilsandi_Keskmine'] = grupeeritud['Vilsandi'].transform(lambda x: x.rolling(window=7).mean().shift(-6))

    valmis_df = df.dropna(subset=['Türi_Keskmine', 'Vilsandi_Keskmine']).copy()
    valmis_df['Periood_Nr'] = valmis_df.groupby('Hüdro_Aasta').cumcount() + 1
    
    valmis_df = valmis_df[valmis_df['Periood_Nr'] <= 359]

    perioodide_arv = valmis_df.groupby('Hüdro_Aasta')['Periood_Nr'].transform('max')
    loplid_andmed = valmis_df[perioodide_arv == 359].copy()

    loplid_h_aastad = set(loplid_andmed['Hüdro_Aasta'].unique())
    eemaldatud_aastad = sorted(list(koik_h_aastad - loplid_h_aastad))

    loplid_andmed['Kuupäevad'] = (
        loplid_andmed['Date'].dt.strftime('%d.%m') + "-" + 
        (loplid_andmed['Date'] + pd.Timedelta(days=6)).dt.strftime('%d.%m')
    )

    loplid_andmed = loplid_andmed[['Hüdro_Aasta', 'Periood_Nr', 'Kuupäevad', 'Türi_Keskmine', 'Vilsandi_Keskmine']]
    loplid_andmed.to_csv(VALJUND_FAIL, index=False, sep=';', encoding='utf-8-sig')

    print("-" * 30)
    print(f"ANALÜÜSI RAPORT")
    print("-" * 30)
    print(f"Säilitati: {len(loplid_h_aastad)} hüdroaastat.")
    print(f"Eemaldati: {len(eemaldatud_aastad)} hüdroaastat.")
    
    if eemaldatud_aastad:
        print("\nEemaldatud aastad (andmeid vähe või puudu):")
        print(", ".join(eemaldatud_aastad))
    
    print("-" * 30)
    print(f"Fail salvestatud: {VALJUND_FAIL}")

if __name__ == "__main__":
    arvuta_kiirelt()