import pandas as pd
import os

# Define the datasets and their configuration
datasets = [
    {
        "name": "YOUSEF",
        "path": r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv",
        "label_col": "label",
        "type_col": "attack_type",
        "filter_query": "label == 1"
    },
    {
        "name": "SUZAN",
        "path": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv",
        "label_col": "label",
        "type_col": "reason",
        "filter_query": "label == 1"
    },
    {
        "name": "İREM",
        "path": r"Raporlar\İREM_BSG\network_traffic_features.csv",
        "label_col": "label",
        "type_col": "label", # label column itself acts as type (e.g. 'pivot', 'can_spoof')
        "filter_query": "label != 'normal'"
    },
    {
        "name": "MİRAÇ",
        "path": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv",
        "label_col": "label",
        "type_col": "reason",
        "filter_query": "label == 1"
    },
    {
        "name": "EMİRHAN",
        "path": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv",
        "label_col": "label",
        "type_col": "message",
        "filter_query": "label == 1"
    },
    {
        "name": "SAMET",
        "path": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv",
        "label_col": "label",
        "type_col": "detail",
        "filter_query": "label == 1"
    },
    {
        "name": "EMİRHNT",
        "path": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv",
        "label_col": "label",
        "type_col": None, # Will default to a fixed name
        "default_type": "Zaman Kayması (Time Drift)",
        "filter_query": "label == 1"
    },
    {
        "name": "İBRAHİM",
        "path": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv",
        "label_col": "label",
        "type_col": "attack_type",
        "filter_query": "label == 1"
    },
    {
        "name": "ATAKAN",
        "path": r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv",
        "label_col": "label",
        "type_col": "attack_type",
        "filter_query": "label == 1"
    }
]

base_path = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
output_file = os.path.join(base_path, "anomaly_summary.txt")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"{'REPORT OWNER':<15} | {'ANOMALY TYPE':<40} | {'COUNT':<5}\n")
    f.write("-" * 70 + "\n")

    for ds in datasets:
        full_path = os.path.join(base_path, ds["path"])
        try:
            if not os.path.exists(full_path):
                f.write(f"{ds['name']:<15} | FILE NOT FOUND ({full_path})\n")
                continue

            df = pd.read_csv(full_path)
            
            # Apply filter for anomalies
            anomalies = df.query(ds["filter_query"])
            
            if anomalies.empty:
                 f.write(f"{ds['name']:<15} | No Anomalies Found | 0\n")
                 continue

            # Count by type
            if ds.get("type_col"):
                counts = anomalies[ds["type_col"]].value_counts()
                for type_name, count in counts.items():
                    f.write(f"{ds['name']:<15} | {str(type_name):<40} | {count}\n")
            else:
                # If no type column, use default type description
                count = len(anomalies)
                type_name = ds.get("default_type", "Unknown Anomaly")
                f.write(f"{ds['name']:<15} | {type_name:<40} | {count}\n")
                
        except Exception as e:
            f.write(f"{ds['name']:<15} | ERROR: {str(e)}\n")

    f.write("-" * 70 + "\n")
print(f"Report written to {output_file}")
