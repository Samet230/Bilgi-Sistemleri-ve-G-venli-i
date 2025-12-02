# tls_downgrade_sim.py
import asyncio
import logging
import json
import hashlib
import os
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -----------------------
# إعدادات لوج وملف
# -----------------------
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"tls_sim_{timestamp_str}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TLS-Sim")

# -----------------------
# Security Monitor
# -----------------------
class SecurityMonitor:
    def __init__(self):
        self.events = []
        self.attacks = []
        self.total_attacks = 0
        self.blocked = 0

    def record_event(self, kind, details):
        entry = {
            "time": datetime.now(timezone.utc).isoformat(),
            "event": kind,
            "details": details
        }
        self.events.append(entry)
        logger.info(f"[EVENT] {kind} | {details}")

    def log_attack(self, attack_type, reason, blocked=True, meta=None):
        self.total_attacks += 1
        if blocked:
            self.blocked += 1
        entry = {
            "type": attack_type,
            "reason": reason,
            "blocked": blocked,
            "time": datetime.now(timezone.utc).isoformat(),
        }
        if meta:
            entry["meta"] = meta
        self.attacks.append(entry)
        logger.warning(f"[ATTACK] {attack_type} | blocked={blocked} | reason={reason} | meta={meta}")

    def save_report(self):
        report_path = log_dir / f"tls_report_{timestamp_str}.json"
        data = {
            "events": self.events,
            "attacks": self.attacks,
            "total_attacks": self.total_attacks,
            "blocked": self.blocked
        }
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved security report: {report_path}")

# -----------------------
# Simulated Entities
# -----------------------
class ChargingStation:
    def __init__(self, station_id, cert_fp, expected_tls="TLS1.3"):
        self.station_id = station_id
        self.energy = 1000.0
        self.cert_fp = cert_fp  # fingerprint string
        self.expected_tls = expected_tls

    def create_ocpp_message(self, msg_type, payload):
        """
        Create a simplistic OCPP message with nonce + signature (app-level).
        """
        nonce = hashlib.sha256(os.urandom(8)).hexdigest()[:12]
        body = {
            "stationId": self.station_id,
            "type": msg_type,
            "payload": payload,
            "nonce": nonce,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        # app-level HMAC-like signature (simplified)
        signature = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        body["signature"] = signature
        return body

    def meter_values(self):
        self.energy += 9 + random.uniform(-1, 1)
        return self.create_ocpp_message("MeterValues", {"energyWh": round(self.energy, 2)})

class CentralSystem:
    def __init__(self, expected_peer_cert_fp, min_tls_version="TLS1.2"):
        self.expected_peer_cert_fp = expected_peer_cert_fp
        self.min_tls_version = min_tls_version
        self.seen_nonces = set()

    def validate_handshake(self, negotiated_tls, peer_fp):
        # Compare TLS versions roughly (assume "TLS1.0","TLS1.1","TLS1.2","TLS1.3")
        order = {"TLS1.0":0, "TLS1.1":1, "TLS1.2":2, "TLS1.3":3}
        if negotiated_tls not in order:
            return False, "UNKNOWN_TLS"
        if order[negotiated_tls] < order.get(self.min_tls_version,2):
            return False, "WEAK_TLS"
        if peer_fp != self.expected_peer_cert_fp:
            return False, "CERT_FINGERPRINT_MISMATCH"
        return True, "OK"

    def validate_ocpp_message(self, msg):
        # check signature exists and nonce not reused
        sig = msg.get("signature")
        nonce = msg.get("nonce")
        if not sig or not nonce:
            return False, "MISSING_SIGNATURE_OR_NONCE"
        if nonce in self.seen_nonces:
            return False, "REPLAY_NONCE"
        # Here we could verify signature properly; we simulate by recomputing
        recomputed = hashlib.sha256(json.dumps({
            k:v for k,v in msg.items() if k!="signature"
        }, sort_keys=True).encode()).hexdigest()
        if recomputed != sig:
            return False, "INVALID_SIGNATURE"
        # passed basic checks
        self.seen_nonces.add(nonce)
        return True, "OK"

# -----------------------
# Attacker (MitM + Downgrade + Inject)
# -----------------------
class Attacker:
    """
    Can perform:
     - downgrade TLS during handshake (force weak cipher/old TLS)
     - intercept and read messages
     - inject fake OCPP commands (RemoteStart/Stop) or fake MeterValues
     - either forward modified messages or block them
    """
    def __init__(self, active=True):
        self.captured = []
        self.active = active

    def mitm_handshake(self, client_wants, server_wants):
        """
        Simulate negotiation. Attacker can force a downgrade.
        Returns negotiated_tls (str) and peer_fp seen by server.
        """
        # Normally intersect client and server lists
        negotiated = None
        # Attacker decides to force downgrade sometimes
        if self.active and random.random() < 0.5:
            # Force downgrade to TLS1.0 or TLS1.1
            negotiated = random.choice(["TLS1.0","TLS1.1"])
            action = "FORCED_DOWNGRADE"
        else:
            # pick best mutual (choose highest)
            priorities = ["TLS1.3","TLS1.2","TLS1.1","TLS1.0"]
            for t in priorities:
                if t in client_wants and t in server_wants:
                    negotiated = t
                    break
            action = "NORMAL"
        # If attacker active he can also spoof certificate fingerprint sometimes
        if self.active and random.random() < 0.3:
            peer_fp = "SPOOFED:" + hashlib.sha256(os.urandom(8)).hexdigest()[:8]
        else:
            peer_fp = server_wants.get("cert_fp")
        return negotiated, peer_fp, action

    def intercept_and_maybe_modify(self, msg):
        # read + store
        self.captured.append(msg.copy())
        # decide to modify with some probability
        if self.active and random.random() < 0.4:
            # If MeterValues, tamper energy
            if msg.get("type") == "MeterValues":
                fake = msg.copy()
                # maliciously increase reported energy to cause overcharge/double-bill
                fake["payload"] = fake.get("payload", {}).copy()
                fake["payload"]["energyWh"] = round(fake["payload"].get("energyWh",0) * (1 + random.uniform(0.05,0.25)), 2)
                # re-sign (attacker cannot produce legit signature — so we'll mark invalid signature)
                fake["signature"] = "TAMPERED:"+hashlib.sha256(json.dumps(fake, sort_keys=True).encode()).hexdigest()[:12]
                logger.info("[ATTACKER] Injected tampered MeterValues")
                return fake, True
            # attacker may inject an unauthorized RemoteStart command
            if random.random() < 0.2:
                injected = {
                    "stationId": msg.get("stationId", "UNKNOWN"),
                    "type": "RemoteStartTransaction",
                    "payload": {"requestBy":"attacker"},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                injected["nonce"] = hashlib.sha256(os.urandom(8)).hexdigest()[:12]
                injected["signature"] = hashlib.sha256(json.dumps(injected, sort_keys=True).encode()).hexdigest()
                logger.info("[ATTACKER] Injected unauthorized RemoteStartTransaction")
                return injected, True
        # otherwise forward unchanged
        return msg, False

# -----------------------
# Simulation Controller (applies detection rules from your doc)
# -----------------------
class Simulator:
    def __init__(self):
        # expected cert fingerprint (what central trusts)
        self.expected_fp = "AB:1C:DE:FA:11:22:33:44:55"
        self.monitor = SecurityMonitor()
        self.central = CentralSystem(expected_peer_cert_fp=self.expected_fp, min_tls_version="TLS1.2")
        self.station = ChargingStation("ST-271", cert_fp=self.expected_fp, expected_tls="TLS1.3")
        self.attacker = Attacker(active=True)

    async def run(self):
        logger.info("=== TLS Downgrade Simulation START ===")
        # 1) simulate handshake
        client_wants = ["TLS1.3","TLS1.2"]
        server_wants = {"tls_supported": ["TLS1.3","TLS1.2","TLS1.1"], "cert_fp": self.station.cert_fp}

        negotiated, seen_peer_fp, action = self.attacker.mitm_handshake(client_wants, server_wants)
        self.monitor.record_event("TLS_NEGOTIATION", {
            "negotiated_tls": negotiated,
            "expected_min": self.central.min_tls_version,
            "peer_cert_fp": seen_peer_fp,
            "action_by_attacker": action
        })

        # central validates handshake
        ok, reason = self.central.validate_handshake(negotiated, seen_peer_fp)
        if not ok:
            # Reaction: terminate session, block further messages on this session
            self.monitor.log_attack("TLS_DOWGRADE_DETECTED", reason, blocked=True, meta={
                "negotiated": negotiated,
                "seen_fp": seen_peer_fp
            })
            self.monitor.record_event("SESSION_TERMINATED", {"reason": reason})
            # still continue simulation to demonstrate attacker tries to inject afterwards (but central should drop)
            session_allowed = False
        else:
            session_allowed = True

        # 2) run a few normal meter messages; attacker may intercept/modify
        for tick in range(1, 16):
            await asyncio.sleep(0)  # fast sim; no real wait
            orig = self.station.meter_values()
            # attacker intercepts and optionally modifies/injects
            forwarded, modified = self.attacker.intercept_and_maybe_modify(orig)
            # if session not allowed, central should reject all messages from this session
            if not session_allowed:
                self.monitor.record_event("OCPP_MSG_REJECTED", {
                    "reason": "TLS_SESSION_NOT_TRUSTED",
                    "msg_type": forwarded.get("type"),
                    "station": forwarded.get("stationId")
                })
                # log if attacker modified while session already terminated
                if modified:
                    self.monitor.log_attack("OCPP_INJECTION_ATTEMPT", "Message injected after session termination", blocked=True, meta={"msg": forwarded})
                continue

            # central validates OCPP message (signature/nonce)
            valid, vreason = self.central.validate_ocpp_message(forwarded)
            if not valid:
                # if invalid signature or replay -> log attack
                self.monitor.log_attack("OCPP_VALIDATION_FAIL", vreason, blocked=True, meta={"msg": forwarded})
                self.monitor.record_event("OCPP_MSG_REJECTED", {"reason": vreason, "msg_type": forwarded.get("type")})
                continue

            # Cross-check MeterValues consistency (simple heuristic)
            if forwarded.get("type") == "MeterValues":
                reported = forwarded["payload"].get("energyWh")
                # simple expected = previous energy + ~10 +-1 (we use central's seen history)
                # For sim, we compare against a naive baseline using station state
                expected = self.station.energy
                if abs(reported - expected) > expected * 0.15:  # big discrepancy threshold
                    self.monitor.log_attack("METER_INCONSISTENCY", "MeterValues deviate from expected", blocked=True, meta={"reported": reported, "expected": expected})
                    self.monitor.record_event("OCPP_MSG_REJECTED", {"reason": "METER_MISMATCH", "reported": reported})
                    continue

            # If reached here -> accepted
            self.monitor.record_event("OCPP_MSG_ACCEPTED", {"msg_type": forwarded.get("type"), "station": forwarded.get("stationId"), "modified_by_attacker": modified})

        # 3) attacker attempts to inject a RemoteStart despite session terminated/weak TLS
        inj = {
            "stationId": self.station.station_id,
            "type": "RemoteStartTransaction",
            "payload": {"requestedBy":"attacker"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        inj["nonce"] = hashlib.sha256(os.urandom(8)).hexdigest()[:12]
        inj["signature"] = hashlib.sha256(json.dumps(inj, sort_keys=True).encode()).hexdigest()

        # If session already terminated, central must reject
        if not session_allowed:
            self.monitor.record_event("OCPP_CMD_REJECTED", {"cmd": inj["type"], "reason": "TLS_NOT_TRUSTED"})
            self.monitor.log_attack("OCPP_CMD_REJECTED", "RemoteStart blocked due to TLS not trusted", blocked=True, meta={"cmd": inj})
        else:
            valid, vreason = self.central.validate_ocpp_message(inj)
            if not valid:
                self.monitor.log_attack("OCPP_CMD_REJECTED", vreason, blocked=True, meta={"cmd": inj})
            else:
                self.monitor.record_event("OCPP_CMD_ACCEPTED", {"cmd": inj["type"]})

        # finish
        self.monitor.save_report()
        logger.info("=== TLS Downgrade Simulation END ===")

# -----------------------
# run
# -----------------------
if __name__ == "__main__":
    sim = Simulator()
    try:
        asyncio.run(sim.run())
    except KeyboardInterrupt:
        print("Interrupted.")
