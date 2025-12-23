import pandas as pd
import os

BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

DATASETS = {
    "YOUSEF": r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv",
    "SAMET": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv",
    "EMİRHAN": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv",
    "ATAKAN": r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv",
    "İBRAHİM": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv",
    "SUZAN": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv",
    "İREM": r"Raporlar\İREM_BSG\network_traffic_features.csv",
    "MİRAÇ": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv",
    "EMİRHNT": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv",
}

print("=" * 60)
print("YOUSEF LOG YAPISI - BOŞ OLMAYAN KOLONLAR")
print("=" * 60)

yousef_path = os.path.join(BASE_PATH, DATASETS["YOUSEF"])
df_yousef = pd.read_csv(yousef_path, nrows=100)

# Kolonları ve doluluk oranlarını göster
yousef_cols = {}
for col in df_yousef.columns:
    non_null_count = df_yousef[col].dropna().replace("", float('nan')).dropna().count()
    fill_rate = non_null_count / len(df_yousef) * 100
    yousef_cols[col] = fill_rate
    print(f"  {col}: %{fill_rate:.0f} dolu")

# Dolu olan kolonları belirle
active_yousef_cols = [col for col, rate in yousef_cols.items() if rate > 10]
print(f"\nAktif Kolonlar: {active_yousef_cols}")

print("\n" + "=" * 60)
print("DİĞER VERİ SETLERİYLE KARŞILAŞTIRMA")
print("=" * 60)

for name, path in DATASETS.items():
    if name == "YOUSEF":
        continue
    
    full_path = os.path.join(BASE_PATH, path)
    if not os.path.exists(full_path):
        print(f"\n{name}: Dosya bulunamadı")
        continue
        
    df = pd.read_csv(full_path, nrows=100)
    
    # Ortak kolon bul
    common_cols = set(active_yousef_cols) & set(df.columns)
    
    print(f"\n🔍 {name}")
    print(f"   Kolonlar: {list(df.columns)}")
    print(f"   Yousef ile Ortak: {common_cols if common_cols else 'YOK'}")
    
    # Eğer ocpp_message veya status varsa değerleri karşılaştır
    if 'ocpp_message' in df.columns:
        print(f"   ocpp_message değerleri: {df['ocpp_message'].unique()[:5]}")
    if 'status' in df.columns:
        print(f"   status değerleri: {df['status'].unique()[:5]}")

print("\n" + "=" * 60)
print("SONUÇ VE ÖNERİ")
print("=" * 60)
