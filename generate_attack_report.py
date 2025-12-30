"""
Attack Type Analysis Report Generator (FULL DATA)
Analyzes all 10 ML training datasets with EXACT paths from train_ensemble_suite.py.
NO ROW LIMITS - reads complete files.
"""
import os
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from collections import Counter

# Add parent dir to path for imports
sys.path.insert(0, r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i")
from detect_attack_ensemble import EnsembleDetector, classify_attack

BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

# EXACT paths from train_ensemble_suite.py (ML Training Data)
TRAINING_DATASETS = [
    {"name": "YOUSEF", "path": r"Raporlar\YOUSEF_BSG\Logs\dataset.csv"},
    {"name": "SAMET", "path": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv"},
    {"name": "EMİRHAN", "path": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv"},
    {"name": "ATAKAN", "path": r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv"},
    {"name": "İBRAHİM", "path": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv"},
    {"name": "SUZAN", "path": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv"},
    {"name": "İREM", "path": r"Raporlar\İREM_BSG\network_traffic_features.csv"},
    {"name": "MİRAÇ", "path": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv"},
    {"name": "EMİRHNT", "path": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv"},
    {"name": "ALİ", "path": r"Raporlar\ALİ_GİRİŞ_BSG\ali_logs_parsed.csv"},
]

def analyze_dataset(ds):
    """Analyze a single dataset and return attack type counts."""
    full_path = os.path.join(BASE_PATH, ds["path"])
    
    if not os.path.exists(full_path):
        return None, f"File not found: {full_path}"
    
    # Try to load detector
    try:
        detector = EnsembleDetector(ds["name"])
    except Exception as e:
        return None, f"Detector error: {e}"
    
    # Read FULL csv (no nrows limit)
    try:
        df = pd.read_csv(full_path, encoding='utf-8-sig', on_bad_lines='skip')
    except Exception as e:
        return None, f"CSV read error: {e}"
    
    logs_list = df.to_dict(orient='records')
    
    if not logs_list:
        return None, "No logs in file"
    
    total_logs = len(logs_list)
    total_attacks = 0
    attack_types = Counter()
    
    # Run batch detection
    try:
        results = detector.detect_batch(logs_list)
        
        for result in results:
            if result['attack_detected']:
                total_attacks += 1
                attack_type = result['final_decision']
                if attack_type.startswith("ŞÜPHELİ: "):
                    attack_type = attack_type.replace("ŞÜPHELİ: ", "") + " (Supheli)"
                attack_types[attack_type] += 1
                
    except Exception as e:
        return None, f"Detection error: {e}"
    
    return {
        "total_logs": total_logs,
        "total_attacks": total_attacks,
        "attack_types": dict(attack_types)
    }, None

# Main Analysis - Write to Markdown File
OUTPUT_FILE = r"C:\Users\smt1s\.gemini\antigravity\brain\bed426e9-452f-4f5b-ab4d-d79f28bd4009\attack_type_report_full.md"

lines = []
lines.append("# Saldiri Tipi Analiz Raporu (TAM VERİ)")
lines.append("")
lines.append("ML egitiminde kullanilan **gercek veri setleri** uzerinden analiz.")
lines.append("")
lines.append(f"Analiz edilen senaryo sayisi: **{len(TRAINING_DATASETS)}**")
lines.append("")

all_results = {}
grand_total_logs = 0
grand_total_attacks = 0
all_attack_types = Counter()

for ds in TRAINING_DATASETS:
    print(f"Analyzing {ds['name']}...")
    
    lines.append(f"## {ds['name']}")
    lines.append(f"Dosya: `{ds['path']}`")
    lines.append("")
    
    result, error = analyze_dataset(ds)
    
    if error:
        lines.append(f"**Hata:** {error}")
        lines.append("")
        all_results[ds['name']] = {"error": error}
        continue
    
    all_results[ds['name']] = result
    grand_total_logs += result["total_logs"]
    grand_total_attacks += result["total_attacks"]
    all_attack_types.update(result["attack_types"])
    
    attack_rate = (result["total_attacks"] / result["total_logs"] * 100) if result["total_logs"] > 0 else 0
    
    lines.append(f"- **Toplam Log:** {result['total_logs']}")
    lines.append(f"- **Tespit Edilen Saldiri:** {result['total_attacks']} (%{attack_rate:.1f})")
    
    if result["attack_types"]:
        lines.append("")
        lines.append("| Saldiri Tipi | Adet | Oran |")
        lines.append("|--------------|------|------|")
        for attack_type, count in sorted(result["attack_types"].items(), key=lambda x: -x[1]):
            pct = (count / result["total_attacks"] * 100) if result["total_attacks"] > 0 else 0
            safe_type = attack_type.replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c").replace("Ş", "S").replace("İ", "I").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O").replace("Ç", "C")
            lines.append(f"| {safe_type} | {count} | %{pct:.1f} |")
    else:
        lines.append("- Saldiri tespit edilmedi. ✅")
    
    lines.append("")
    lines.append("---")
    lines.append("")

# Summary
lines.append("# Genel Ozet")
lines.append("")
lines.append(f"- **Toplam Analiz Edilen Log:** {grand_total_logs:,}")
lines.append(f"- **Toplam Tespit Edilen Saldiri:** {grand_total_attacks:,}")
if grand_total_logs > 0:
    lines.append(f"- **Genel Saldiri Orani:** %{(grand_total_attacks/grand_total_logs*100):.1f}")
lines.append("")

lines.append("## Tum Saldiri Tipleri (Birlesitirilmis)")
lines.append("")
lines.append("| Saldiri Tipi | Adet | Oran |")
lines.append("|--------------|------|------|")
for attack_type, count in sorted(all_attack_types.items(), key=lambda x: -x[1]):
    pct = (count / grand_total_attacks * 100) if grand_total_attacks > 0 else 0
    safe_type = attack_type.replace("ş", "s").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c").replace("Ş", "S").replace("İ", "I").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O").replace("Ç", "C")
    lines.append(f"| {safe_type} | {count:,} | %{pct:.1f} |")

# Write to file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"\nReport written to: {OUTPUT_FILE}")
print(f"Total logs analyzed: {grand_total_logs:,}")
print(f"Total attacks detected: {grand_total_attacks:,}")
