"""
Attack Pattern Analyzer
Scans all CSV files in Raporlar to extract unique attack signatures and keywords.
"""
import os
import pandas as pd
from collections import defaultdict

BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\Raporlar"

def analyze_dataset(folder_path, folder_name):
    """Analyze CSVs in a folder to find attack-related columns and values."""
    results = {
        "folder": folder_name,
        "files_analyzed": 0,
        "attack_columns": [],
        "sample_attack_values": [],
        "text_columns": [],
        "columns": []
    }
    
    for file in os.listdir(folder_path):
        if not file.endswith('.csv'):
            continue
        
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path, nrows=100, encoding='utf-8-sig', on_bad_lines='skip')
            results["files_analyzed"] += 1
            results["columns"] = list(df.columns)[:10]  # First 10 columns
            
            # Look for attack indicator columns
            for col in df.columns:
                col_lower = col.lower()
                if any(kw in col_lower for kw in ['label', 'attack', 'anomaly', 'threat', 'is_', 'saldiri', 'durum', 'status', 'level', 'severity']):
                    results["attack_columns"].append(col)
                    # Get unique values
                    unique_vals = df[col].dropna().unique()[:10]
                    results["sample_attack_values"].extend([f"{col}={v}" for v in unique_vals])
                    
            # Look for text columns that might contain attack descriptions
            for col in df.columns:
                if df[col].dtype == 'object':
                    sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else ""
                    if isinstance(sample, str) and len(sample) > 10:
                        results["text_columns"].append(col)
                        
        except Exception as e:
            print(f"  Error reading {file}: {e}")
            
    return results

# Main Analysis
print("="*60)
print("ATTACK PATTERN ANALYSIS REPORT")
print("="*60)

all_results = []

for folder in sorted(os.listdir(BASE_PATH)):
    folder_path = os.path.join(BASE_PATH, folder)
    if not os.path.isdir(folder_path):
        continue
        
    print(f"\n>>> {folder}")
    result = analyze_dataset(folder_path, folder)
    all_results.append(result)
    
    if result["files_analyzed"] > 0:
        print(f"  Files: {result['files_analyzed']}")
        print(f"  Columns: {result['columns']}")
        print(f"  Attack Columns: {result['attack_columns']}")
        print(f"  Text Columns: {result['text_columns']}")
        if result['sample_attack_values']:
            print(f"  Sample Values: {result['sample_attack_values'][:5]}")
    else:
        print("  No CSV files found.")
        
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
