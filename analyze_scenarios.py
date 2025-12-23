import pandas as pd
import os

# Configuration: Map each user to their file, descriptive scenario name, and filtering logic
datasets = [
    {
        "owner": "YOUSEF",
        "file_path": r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv",
        "scenario": "OCPP & Network Attack Vectors (Karma Senaryo)",
    },
    {
        "owner": "SUZAN",
        "file_path": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv",
        "scenario": "Energy Consumption & Price Manipulation",
    },
    {
        "owner": "İREM",
        "file_path": r"Raporlar\İREM_BSG\network_traffic_features.csv",
        "scenario": "Network Traffic & CAN Bus Anomalies",
    },
    {
        "owner": "MİRAÇ",
        "file_path": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv",
        "scenario": "Charging Station Registration & Auth Anomalies",
    },
    {
        "owner": "EMİRHAN",
        "file_path": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv",
        "scenario": "Kubernetes/OCP Security Incidents",
    },
    {
        "owner": "SAMET",
        "file_path": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv",
        "scenario": "IDS/IPS Security Logs (Kritik Altyapı)",
    },
    {
        "owner": "EMİRHNT",
        "file_path": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv",
        "scenario": "Time Shift & Billing Anomaly (Zaman Kayması)",
    },
    {
        "owner": "İBRAHİM",
        "file_path": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv",
        "scenario": "System Time Manipulation (Zaman Anomalisi)",
    },
    {
        "owner": "ATAKAN",
        "file_path": r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv",
        "scenario": "Load Data Manipulation (Yük Verisi)",
    }
]

base_path = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
output_file = os.path.join(base_path, "scenario_summary.txt")

with open(output_file, 'w', encoding='utf-8') as f:
    # Header
    header = f"| {'RAPOR SAHİBİ':<15} | {'SENARYO ADI':<50} | {'TOPLAM LOG SATIRI':<18} |"
    f.write(header + "\n")
    f.write(f"|{'-'*17}|{'-'*52}|{'-'*20}|\n")

    total_all_logs = 0

    for ds in datasets:
        full_path = os.path.join(base_path, ds["file_path"])
        
        try:
            if os.path.exists(full_path):
                # Read CSV to get precise line count
                df = pd.read_csv(full_path)
                count = len(df)
            else:
                count = "DOSYA YOK"
        except Exception as e:
            count = f"ERROR: {e}"

        if isinstance(count, int):
            total_all_logs += count
            count_str = f"{count:,}".replace(",", ".") # Format with dots for thousands
        else:
            count_str = str(count)

        row = f"| {ds['owner']:<15} | {ds['scenario']:<50} | {count_str:<18} |"
        f.write(row + "\n")

    f.write(f"\n**TOPLAM İŞLENEN VERİ:** {total_all_logs:,} satır".replace(",", "."))

print(f"Summary generated at: {output_file}")
