import json
import os
import sys
import time
import logging
from datetime import datetime


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_log_dir(log_file_path: str) -> None:
    log_dir = os.path.dirname(os.path.abspath(log_file_path))
    os.makedirs(log_dir, exist_ok=True)


def setup_logger(log_file_path: str) -> logging.Logger:
    logger = logging.getLogger("pricing_anomaly_test")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if script reruns in same interpreter
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # File handler
    fh = logging.FileHandler(log_file_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def is_price_anomalous(price: float, min_ok: float, max_ok: float) -> bool:
    # Anomaly examples:
    # - Negative price
    # - Extremely high price
    # - Outside normal configured bounds
    return (price < 0) or (price < min_ok) or (price > max_ok)


def main() -> int:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")

    try:
        cfg = load_config(config_path)
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    log_file = os.path.join(base_dir, cfg.get("log_file", "../logs/pricing_anomaly.log"))
    ensure_log_dir(log_file)
    logger = setup_logger(log_file)

    cp_id = cfg.get("charge_point_id", "CP-ANOM-01")
    currency = cfg.get("currency", "EUR")
    baseline = float(cfg.get("baseline_price", 0.20))
    anomaly_prices = cfg.get("anomaly_prices", [baseline, 0.85, 0.18, 0.95, -0.30, 5.50])
    sleep_s = float(cfg.get("sleep_seconds", 1))
    min_ok = float(cfg.get("min_normal_price", 0.05))
    max_ok = float(cfg.get("max_normal_price", 1.50))

    test_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    logger.info(f"[TEST_START] test_id={test_id} charge_point={cp_id} currency={currency}")
    logger.info(f"[BASELINE] baseline_price={baseline:.4f} {currency}/kWh")
    logger.info(f"[LIMITS] min_normal={min_ok:.4f} max_normal={max_ok:.4f} ({currency}/kWh)")

    # Baseline phase (simulate normal operation)
    logger.info("[PHASE] baseline_normal_operation")
    for i in range(3):
        logger.info(f"[NORMAL] tick={i+1} price={baseline:.4f} {currency}/kWh")
        time.sleep(max(0.1, sleep_s))

    # Anomaly injection phase
    logger.info("[PHASE] anomaly_injection_frequent_irregular_pricing")
    anomaly_count = 0
    for idx, price in enumerate(anomaly_prices, start=1):
        price_f = float(price)
        if is_price_anomalous(price_f, min_ok, max_ok):
            anomaly_count += 1
            logger.warning(f"[ANOMALY] step={idx} price={price_f:.4f} {currency}/kWh (out_of_bounds)")
        else:
            logger.info(f"[PRICE_UPDATE] step={idx} price={price_f:.4f} {currency}/kWh")
        time.sleep(max(0.1, sleep_s))

    # Summary
    logger.info("[PHASE] summary")
    logger.info(f"[SUMMARY] total_steps={len(anomaly_prices)} anomalies_detected={anomaly_count}")
    logger.info(f"[TEST_END] test_id={test_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
