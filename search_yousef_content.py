import pandas as pd
import os

# --- Configuration ---
BASE_PATH = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i"
YOUSEF_PATH = os.path.join(BASE_PATH, r"Raporlar\YOUSEF_BSG\Toplanan_Veriler\dataset_final.csv")

# Keywords associated with other users' datasets
# Format: "User": ["keyword1", "keyword2"]
KEYWORDS = {
    "SUZAN": ["price", "energy", "enerji", "fiyat"],
    "MİRAÇ": ["plaka", "plate", "isim", "name", "register", "kayıt"],
    "İREM": ["can", "bus", "network", "trafik", "spoof", "pivot"],
    "EMİRHAN": ["kubernetes", "ocp", "pod", "rbac", "sql", "injection"],
    "SAMET": ["ids", "ips", "firmware", "enjeksiyon", "yan hareket", "lateral"],
    "İBRAHİM": ["zaman", "time", "drift", "saat"],
    "ATAKAN": ["yük", "load", "manipulasyon", "manipulation", "11.2"], # 11.2kW was the attack value
    "EMİRHNT": ["tarife", "tüketim", "billing", "faturalandırma"]
}

OUTPUT_FILE = os.path.join(BASE_PATH, "yousef_content_search_report.txt")

def search_content():
    try:
        print(f"Loading '{YOUSEF_PATH}'...")
        df = pd.read_csv(YOUSEF_PATH)
        
        # Convert entire dataframe to a single string for valid string searching (inefficient but effective for small datsets) 
        # or search column by column. Let's do column by column for better reporting.
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"DEEP CONTENT SEARCH REPORT: YOUSEF DATASET ({len(df)} rows)\n")
            f.write("========================================================\n\n")
            
            # 1. Attack Type Analysis
            f.write("1. ATTACK_TYPE / EVENT_TYPE COLUMN ANALYSIS\n")
            f.write("-------------------------------------------\n")
            if 'attack_type' in df.columns:
                unique_attacks = df['attack_type'].unique()
                f.write(f"Unique Attack Types found: \n{unique_attacks}\n\n")
                
                # Check which users 'match' these attack types
                for user, keywords in KEYWORDS.items():
                    matches = []
                    for attack in unique_attacks:
                        attack_str = str(attack).lower()
                        for kw in keywords:
                            if kw.lower() in attack_str:
                                matches.append(attack)
                                break # Found one keyword for this attack, move to next attack
                    
                    if matches:
                        f.write(f"  -> {user}: POTENTIAL MATCH found in 'attack_type': {set(matches)}\n")
            else:
                f.write("  -> 'attack_type' column NOT FOUND.\n")
            f.write("\n")

            # 2. Full Text Search in All Columns (for hidden matches)
            f.write("2. FULL KEYWORD SEARCH (ALL COLUMNS)\n")
            f.write("------------------------------------\n")
            
            # Convert all relevant columns to string
            str_df = df.astype(str).apply(lambda x: x.str.lower())
            
            for user, keywords in KEYWORDS.items():
                match_count = 0
                found_samples = set()
                
                for kw in keywords:
                    kw_lower = kw.lower()
                    # Check if keyword exists in any cell of the dataframe
                    # mask is True where keyword is found
                    mask = str_df.apply(lambda col: col.str.contains(kw_lower, na=False))
                    # If any True in row, that row is a match
                    rows_with_kw = mask.any(axis=1)
                    count = rows_with_kw.sum()
                    
                    if count > 0:
                        match_count += count
                        # Get a sample value that matched
                        # This is a bit tricky to get efficiently in pandas without iteration, 
                        # let's just say "found"
                        found_samples.add(kw)
                
                if match_count > 0:
                    f.write(f"  -> {user}: FOUND {match_count} rows containing keywords {list(found_samples)}\n")
                else:
                    f.write(f"  -> {user}: No matches found.\n")
                    
            f.write("\n")
            
            # 3. Numeric specific checks (e.g. Atakan's 11.2 kW)
            f.write("3. NUMERIC/SPECIFIC VALUE CHECKS\n")
            f.write("--------------------------------\n")
            # Convert to string and search for "11.2" specifically
            if str_df.apply(lambda col: col.str.contains("11.2", na=False)).any(axis=None):
                 f.write("  -> Found '11.2' (Atakan's specific attack value) in dataset.\n")
            else:
                 f.write("  -> '11.2' not found.\n")

        print(f"Report generated: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_content()
