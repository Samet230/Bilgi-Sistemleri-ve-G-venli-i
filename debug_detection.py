
import pandas as pd
import numpy as np
from detect_attack_ensemble import EnsembleDetector, SAFE_PATTERNS

# Load test data
test_file = r"c:\Users\smt1s\OneDrive\Belgeler\GitHub\Bilgi-Sistemleri-ve-G-venli-i\test_data\test_EMİRHAN.csv"
print(f"Loading {test_file}...")
df = pd.read_csv(test_file)
logs = df.to_dict(orient='records')

print(f"Loaded {len(logs)} logs.")

# Initialize detector
detector = EnsembleDetector("EMİRHAN")
print("Detector initialized. Running detection...")

# Run detection manually to inspect internals if needed, 
# but detect_batch returns the final results we want to check.
results = detector.detect_batch(logs)

print("\n=== DETECTION RESULTS (Log #2 Only) ===")
# Check only the 2nd log (index 1) which is "User login success"
for i, res in enumerate(results[1:2]):
    i = i + 1 # Adjust index to match original
    raw_msg = logs[i].get('message', 'N/A')
    print(f"\n[Log #{i+1}] {raw_msg}")
    print(f"  Decision: {res['final_decision']}")
    print(f"  Confidence: {res['confidence_score']:.4f}")
    print(f"  Votes: {res['council_votes']}")
    print(f"  Winning Model: {res['winning_model']}")
    
    # Re-check whitelist logic to verify
    text_for_classification = " ".join(str(v) for v in logs[i].values()).lower()
    is_whitelisted = any(safe_pattern in text_for_classification for safe_pattern in SAFE_PATTERNS)
    has_attack_key = any(k in text_for_classification for k in ["flood", "attack", "fail", "error", "denied", "unauthorized"])
    print(f"  DEBUG -> Whitelisted: {is_whitelisted}, HasAttackKey: {has_attack_key}")

print("\nDone.")
