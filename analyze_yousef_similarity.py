import pandas as pd
import os

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"

# Yousef's Data (Reference)
YOUSEF_CFG = {
    "name": "YOUSEF",
    "path": os.path.join(BASE_PATH, r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv"),
    "anomaly_col": "attack_type"
}

# Other Datasets to Compare
OTHERS_CFG = [
    {"name": "SUZAN", "path": r"Raporlar\SUZAN_BGS\logs\enerji_logs.csv", "anomaly_col": "reason"},
    {"name": "İREM", "path": r"Raporlar\İREM_BSG\network_traffic_features.csv", "anomaly_col": "label"},
    {"name": "MİRAÇ", "path": r"Raporlar\MİRAC_BSG\logs\kayıt_logs.csv", "anomaly_col": "reason"},
    {"name": "EMİRHAN", "path": r"Raporlar\EMİRHAN_BSG\LOG\logs_5000_parsed.csv", "anomaly_col": "message"},
    {"name": "SAMET", "path": r"Raporlar\SAMET_SAHIN\Test ve Loglar\ids_guvenlik_parsed_labeled.csv", "anomaly_col": "detail"},
    {"name": "EMİRHNT", "path": r"Raporlar\EMİRHNT_BSG\logs_expanded.csv", "anomaly_col": None}, # Default: Zaman Kayması
    {"name": "İBRAHİM", "path": r"Raporlar\İBRAHİM_SAHİN\output_labeled.csv", "anomaly_col": "attack_type"},
    {"name": "ATAKAN", "path": r"Raporlar\ATAKAN_BSG\AtakanAkyol-Yuk-Verisi-Manupilasyonu-Anomalisi-99af48c\expanded_logs.csv", "anomaly_col": "attack_type"}
]

REPORT_FILE = os.path.join(BASE_PATH, "similarity_report.txt")

def get_anomaly_types(df, col_name, default=None):
    if not col_name:
        return {default} if default else set()
    try:
        if col_name == 'label':
             # For IREM, label column has values 'normal', 'pivot', etc.
             return set(df[df['label'] != 'normal']['label'].unique())
        
        # Filter for anomalies first if label column exists
        if 'label' in df.columns:
            anomalies = df[df['label'] == 1]
            if anomalies.empty: return set()
            return set(anomalies[col_name].dropna().unique())
        else:
            return set(df[col_name].dropna().unique())
            
    except Exception as e:
        return {f"Error: {e}"}

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    if union == 0: return 0.0
    return intersection / union

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("DETAILED SIMILARITY ANALYSIS: YOUSEF vs OTHERS\n")
    f.write("================================================\n\n")

    # Load Yousef's Data
    try:
        yousef_df = pd.read_csv(YOUSEF_CFG['path'])
        yousef_cols = set(yousef_df.columns)
        yousef_anomalies = get_anomaly_types(yousef_df, YOUSEF_CFG['anomaly_col'])
        f.write(f"REFERENCE: YOUSEF ({len(yousef_df)} rows)\n")
        f.write(f"Columns: {', '.join(yousef_cols)}\n")
        f.write(f"Anomaly Types: {', '.join(str(s) for s in yousef_anomalies)}\n\n")
        f.write("-" * 50 + "\n\n")
        
    except Exception as e:
        f.write(f"CRITICAL ERROR LOADING YOUSEF DATA: {e}\n")
        exit()

    for other in OTHERS_CFG:
        other_path = os.path.join(BASE_PATH, other['path'])
        f.write(f"COMPARING WITH: {other['name']}\n")
        
        if not os.path.exists(other_path):
            f.write("  -> FILE NOT FOUND\n\n")
            continue
            
        try:
            other_df = pd.read_csv(other_path)
            other_cols = set(other_df.columns)
            
            # 1. Structural Similarity (Columns)
            common_cols = yousef_cols.intersection(other_cols)
            col_sim = jaccard_similarity(yousef_cols, other_cols)
            
            f.write(f"  -> Column Similarity: {col_sim:.2f} (Jaccard)\n")
            f.write(f"  -> Common Columns: {', '.join(common_cols) if common_cols else 'None'}\n")
            
            # 2. Anomaly Type Overlap
            other_anomalies = get_anomaly_types(other_df, other['anomaly_col'], default="Unknown")
            # Normalize strings for comparison (lowercase, strip)
            y_norm = {str(x).lower().strip() for x in yousef_anomalies}
            o_norm = {str(x).lower().strip() for x in other_anomalies}
            
            common_anomalies = y_norm.intersection(o_norm)
            
            f.write(f"  -> Anomaly Overlap: {'YES' if common_anomalies else 'NO'}\n")
            if common_anomalies:
                f.write(f"  -> Shared Types: {', '.join(common_anomalies)}\n")
            else:
                f.write(f"  -> Unique to {other['name']}: {', '.join(str(s) for s in other_anomalies)}\n")

            # 3. Row Inclusion Check (Subset check)
            # Check if any row in other_df exists in yousef_df using common columns
            if common_cols:
                # convert common cols to string to avoid type mismatches during merge
                y_subset = yousef_df[list(common_cols)].astype(str)
                o_subset = other_df[list(common_cols)].astype(str)
                
                # Check for intersection
                merge_check = pd.merge(y_subset, o_subset, on=list(common_cols), how='inner')
                match_count = len(merge_check)
                
                f.write(f"  -> Row Matches (Exact Data Match on Common Cols): {match_count} / {len(other_df)}\n")
                if match_count > 0:
                    f.write("  -> CONCLUSION: PROBABLE DATA SUBSET / SHARED SOURCE\n")
            
            f.write("\n")

        except Exception as e:
            f.write(f"  -> ERROR ANALYZING: {e}\n\n")

print(f"Report generated: {REPORT_FILE}")
