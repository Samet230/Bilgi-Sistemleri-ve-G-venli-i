import json
import random
from datetime import datetime, timedelta

random.seed(42)

N = 5000
OUT_TXT = "logs_5000.txt"
OUT_JSON = "logs_5000.json"

# OCP / K8s bağlamı (sentetik ama analiz edilebilir)
CLUSTERS = ["ocp-lab-01"]
NAMESPACES = ["dev", "test", "payments", "auth", "monitoring"]
PODS = [
    "api-6d7f8c9b7f-2kq9x",
    "web-5c7b9d4cdd-hm8z1",
    "payment-7b86c9c7b8-q2v7m",
    "auth-6c5d7f6cbb-9p3a2",
    "gateway-7f8c9d7b6b-x4n1k",
]
NODES = ["worker-1", "worker-2", "infra-1"]
ROUTES = ["api.example.lab", "web.example.lab", "pay.example.lab", "auth.example.lab"]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
PATHS = [
    "/", "/login", "/api/v1/users", "/api/v1/orders", "/api/v1/payments",
    "/admin", "/.env", "/wp-login.php", "/actuator/health", "/actuator/env"
]
USER_AGENTS = [
    "Mozilla/5.0", "curl/8.5.0", "python-requests/2.31.0",
    "sqlmap/1.7.12", "nikto/2.5.0", "nmap NSE"
]

# Saldırı olayları (olay analizi için stage + why)
ATTACK_EVENTS = [
    {
        "event": "Yan Hareket / Ağ Keşfi",
        "severity": "UYARI",
        "stage": "Reconnaissance",
        "action": "Bloklandı",
        "rule_id": "NET-SCAN-1001",
        "why": [
            "Kısa sürede çoklu hedef/port denemesi tespit edildi.",
            "Ağ segmenti içinde sıra dışı keşif trafiği görüldü."
        ],
    },
    {
        "event": "TLS Downgrade / Fuzzing",
        "severity": "TEHDIT",
        "stage": "Initial Access",
        "action": "Bloklandı",
        "rule_id": "TLS-ANOM-2001",
        "why": [
            "TLS el sıkışmasında anormal sürüm/şifre takımı denemeleri tespit edildi.",
            "Kısa süreli tekrarlayan handshake hataları fuzzing davranışına benziyor."
        ],
    },
    {
        "event": "Firmware Enjeksiyonu (Simülasyon)",
        "severity": "KRITIK",
        "stage": "Execution",
        "action": "Bloklandı",
        "rule_id": "FW-INJECT-9001",
        "why": [
            "Yetkisiz binary/firmware benzeri payload pattern’i tespit edildi.",
            "Beklenmedik imza/format ve tekrar denemeler kritik ihlal göstergesi."
        ],
    },
    {
        "event": "SQL Injection Denemesi",
        "severity": "TEHDIT",
        "stage": "Initial Access",
        "action": "Bloklandı",
        "rule_id": "WAF-SQLI-3003",
        "why": [
            "Parametrelerde SQLi imzaları (OR 1=1, UNION SELECT) tespit edildi.",
            "URL/Body içinde şüpheli anahtar kelime kombinasyonları görüldü."
        ],
    },
    {
        "event": "RBAC Yetki Yükseltme Şüphesi",
        "severity": "KRITIK",
        "stage": "Privilege Escalation",
        "action": "Engellendi",
        "rule_id": "K8S-RBAC-4005",
        "why": [
            "RoleBinding/ClusterRoleBinding değişikliği denemesi görüldü.",
            "Yüksek ayrıcalık istek paterni normal dışı."
        ],
    },
]

NORMAL_EVENTS = [
    {
        "event": "Trafik Akışı Temiz",
        "severity": "NORMAL",
        "stage": "Benign",
        "action": "OK",
        "rule_id": "OK-0000",
        "why": [
            "İstekler beklenen davranış aralığında.",
            "Hata oranı ve gecikmeler normal."
        ],
    },
    {
        "event": "Servis Sağlık Kontrolü",
        "severity": "NORMAL",
        "stage": "Benign",
        "action": "OK",
        "rule_id": "OK-0001",
        "why": [
            "Health-check başarılı.",
            "Pod metrikleri stabil."
        ],
    },
]

def rand_ip(private=True):
    if private:
        return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    return f"{random.randint(2,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def rand_hex_id():
    return hex(random.randint(1, 4095))

def gen_http():
    method = random.choice(HTTP_METHODS)
    path = random.choice(PATHS)
    status = random.choice([200, 200, 201, 204, 301, 400, 401, 403, 404, 429, 500])
    ua = random.choice(USER_AGENTS)
    return method, path, status, ua

def choose_event():
    # saldırı oranı: %18 (analiz için dengeli)
    if random.random() < 0.18:
        return random.choice(ATTACK_EVENTS), True
    return random.choice(NORMAL_EVENTS), False

def build_record(ts):
    ev, is_attack = choose_event()

    cluster = random.choice(CLUSTERS)
    ns = random.choice(NAMESPACES)
    pod = random.choice(PODS)
    node = random.choice(NODES)
    route = random.choice(ROUTES)

    src_ip = rand_ip(private=False if is_attack and random.random() < 0.6 else True)
    dst_ip = rand_ip(private=True)
    src_port = random.randint(1024, 65535)
    dst_port = random.choice([80, 443, 8080, 8443])

    method, path, status, ua = gen_http()

    why_flagged = random.choice(ev["why"])
    confidence = round(random.uniform(0.75, 0.99), 2) if is_attack else round(random.uniform(0.10, 0.45), 2)

    record = {
        "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "label": "SALDIRI" if is_attack else "NORMAL",
        "severity": ev["severity"],
        "stage": ev["stage"],
        "event": ev["event"],
        "action": ev["action"],
        "rule_id": ev["rule_id"],
        "id_hex": rand_hex_id(),

        "ocp": {
            "cluster": cluster,
            "namespace": ns,
            "pod": pod,
            "node": node,
            "route": route
        },
        "network": {
            "src_ip": src_ip,
            "src_port": src_port,
            "dst_ip": dst_ip,
            "dst_port": dst_port
        },
        "http": {
            "method": method,
            "path": path,
            "status": status,
            "user_agent": ua
        },
        "analysis": {
            "why_flagged": why_flagged,
            "confidence": confidence,
            "next_steps": (
                ["Kaynak IP’yi kontrol et/rate-limit doğrula", "Pod loglarını korele et", "Audit zincirini incele"]
                if is_attack else
                ["İzlemeye devam et", "Trend anomali kontrolü"]
            )
        }
    }

    # TXT satırı (tam senin istediğin gibi line-based)
    txt_line = (
        f"[{record['timestamp']}] "
        f"[{record['label']}] "
        f"{record['severity']}: {record['event']} | "
        f"Aksiyon: {record['action']} | "
        f"Stage: {record['stage']} | "
        f"Rule: {record['rule_id']} | "
        f"ID: {record['id_hex']} | "
        f"src={src_ip}:{src_port} -> dst={dst_ip}:{dst_port} | "
        f"http={method} {path} {status} ua=\"{ua}\" | "
        f"ocp=cluster:{cluster} ns:{ns} pod:{pod} node:{node} route:{route} | "
        f"neden=\"{why_flagged}\" conf={confidence}"
    )

    return record, txt_line

def main():
    start = datetime(2025, 12, 20, 23, 0, 0)
    ts = start

    json_records = []

    with open(OUT_TXT, "w", encoding="utf-8") as ftxt:
        for _ in range(N):
            # saldırı anlarında daha sık log (burst efekti)
            ts += timedelta(seconds=random.randint(0, 2) if random.random() < 0.25 else random.randint(1, 6))

            rec, line = build_record(ts)
            ftxt.write(line + "\n")
            json_records.append(rec)

    # TXT bittikten sonra ayrı JSON dosyası yaz
    with open(OUT_JSON, "w", encoding="utf-8") as fjson:
        json.dump(json_records, fjson, ensure_ascii=False, indent=2)

    print(f"✅ Üretildi: {OUT_TXT} (5000 satır) + {OUT_JSON} (5000 kayıt)")

if __name__ == "__main__":
    main()
