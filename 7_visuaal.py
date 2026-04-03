import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.stats import linregress
from statsmodels.nonparametric.smoothers_lowess import lowess

# -------------------------------------------------------
# SISENDID JA VÄLJUNDID
# -------------------------------------------------------
FAIL_TURI_KOOND = "analüüsi_andmed/turi_ekstreemsused_oktoober.csv"
FAIL_VILSANDI_KOOND = "analüüsi_andmed/vilsandi_ekstreemsused_oktoober.csv"

if not os.path.exists('graafikud'):
    os.makedirs('graafikud')

def loo_graafik(df, pealkiri, failinimi, temp_veerg):
    if df.empty:
        return

    plt.figure(figsize=(15, 8))
    df_plot = df.copy()

    # X-telg: Aasta algusnumber
    df_plot['X_Aasta'] = df_plot['Hüdro_Aasta'].str.split('/').str[0].astype(int)
    
    x = df_plot['X_Aasta']
    y = df_plot['Periood_Nr']

    #  Zoom
    y_min, y_max = y.min(), y.max()
    y_range = y_max - y_min
    plt.ylim(y_min - (y_range * 0.1 + 10), y_max + (y_range * 0.1 + 15))

    # Keskmine joon
    keskmine_y = y.mean()
    plt.axhline(keskmine_y, color='black', linestyle=':', linewidth=1.5, alpha=0.4, 
                label=f'Keskmine: päev {keskmine_y:.1f}')

    # LOWESS trend
    sile_y = lowess(y, x, frac=0.25)
    plt.plot(sile_y[:,0], sile_y[:,1], color='orange', linewidth=2.5, label='Sujuv trend (LOWESS)')

    # Lineaarne trend
    res = linregress(x, y)
    plt.plot(x, res.intercept + res.slope*x, "r--", linewidth=1.5, alpha=0.8,
             label=f'Lineaarne trend (kalle={res.slope:.3f} p/a)')
    
    # Andmepunktid
    plt.plot(x, y, 'o-', color='tab:blue', markersize=5, alpha=0.5, label='Andmed')

    # 5. Punktide sildid
    for i, row in df_plot.iterrows():
        temp_ymardatud = round(float(row[temp_veerg]), 1)
        
        plt.annotate(
            f"{temp_ymardatud}°", 
            (row['X_Aasta'], row['Periood_Nr']), 
            xytext=(0, 8), textcoords='offset points', 
            ha='center', fontsize=8, alpha=0.8,
            bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.5, ec='none')
        )

    # Y-telje sildid
    kuud = [
        (1, '1.okt'), (32, '1.nov'), (62, '1.dets'), (93, '1.jaan'), 
        (124, '1.veeb'), (152, '1.märts'), (183, '1.apr'), (213, '1.mai'), 
        (244, '1.juuni'), (274, '1.juuli'), (305, '1.aug'), (335, '1.sept'), (366, '1.okt')
    ]
    aktsepteeritud_y = plt.gca().get_ylim()
    naitatavad_kuud = [k for k in kuud if aktsepteeritud_y[0] - 20 <= k[0] <= aktsepteeritud_y[1] + 20]
    plt.yticks([k[0] for k in naitatavad_kuud], [k[1] for k in naitatavad_kuud])

    plt.title(pealkiri, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Aasta', fontsize=12)
    plt.ylabel('Perioodi paiknemine', fontsize=12)
    
    # Statistika kast
    stat_info = f"Trend: {res.slope:.3f} p/a\nR²: {res.rvalue**2:.3f}\np: {res.pvalue:.4f}"
    plt.text(0.02, 0.96, stat_info, transform=plt.gca().transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray'))

    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(loc='lower right', frameon=True)
    plt.tight_layout()
    
    plt.savefig(failinimi, dpi=150)
    plt.close()
    print(f" -> Graafik valmis: {failinimi}")

def genereeri_graafikud():
    for fail, jaam in [(FAIL_TURI_KOOND, "Türi"), (FAIL_VILSANDI_KOOND, "Vilsandi")]:
        if os.path.exists(fail):
            df = pd.read_csv(fail, sep=';', encoding='utf-8-sig')
            
            # Soojemad (Suvi)
            df_soojem = df[(df['Tüüp'] == 'Soojem')]
            loo_graafik(df_soojem, f"{jaam}: Soojema nädala ajaline paiknemine", 
                        f"graafikud/graafik_{jaam.lower()}_soojem_zoom.png", f"{jaam}_Keskmine")
            
            # Külmemad (Talv)
            df_kylmem = df[(df['Tüüp'] == 'Külmem')]
            loo_graafik(df_kylmem, f"{jaam}: Külmema nädala ajaline paiknemine", 
                        f"graafikud/graafik_{jaam.lower()}_kylmem_zoom.png", f"{jaam}_Keskmine")

    print("\nGraafikud on nüüd puhtamad ja temperatuurid ümardatud.")

if __name__ == "__main__":
    genereeri_graafikud()