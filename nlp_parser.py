import re
import time
from pathlib import Path
import joblib
from policy_engine import build_network_policy

MODEL_PATH = Path(__file__).parent / "intent_model.joblib"
MODEL = joblib.load(MODEL_PATH)
MODEL.predict_proba(["warmup"])

IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")
RATE_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mbps|mbit|megabit|mega|mb|kbps|kbit|kilobit|kilo|kb|gbps|gbit|gigabit|giga|gb|m|k|g)\b",
    re.IGNORECASE,
)
PORT_PATTERN = re.compile(r"\bport\s*(\d+)\b", re.IGNORECASE)
ETHER_PATTERN = re.compile(r"\b(?:ethernet|ether)\s*(\d+)\b", re.IGNORECASE)
WLAN_PATTERN = re.compile(r"\b(wlan\s*\d+|bridge)\b", re.IGNORECASE)

SERVICE_ALIASES = {
    "http": 80,
    "https": 443,
    "ssh": 22,
    "dns": 53,
}

UNBLOCK_WORDS = ("buka", "unblock", "izinkan", "lepas", "pulihkan")
UNLIMIT_WORDS = ("hapus", "cabut", "unlimit", "hilangkan")
LIMIT_WORDS = ("limit", "bandwidth", "kecepatan")


def parse_intent(text: str) -> dict:
    t0 = time.perf_counter()
    raw = text.strip() if isinstance(text, str) else ""

    probs = MODEL.predict_proba([raw])[0]
    best_idx = probs.argmax()
    intent = str(MODEL.classes_[best_idx])
    confidence = float(probs[best_idx])

    text_lower = raw.lower()
    if any(w in text_lower for w in UNBLOCK_WORDS) and ("blokir" in text_lower or "port" in text_lower):
        intent = "unblock_traffic"
        confidence = 1.0
    elif any(w in text_lower for w in UNLIMIT_WORDS) and any(w in text_lower for w in LIMIT_WORDS):
        intent = "remove_limit"
        confidence = 1.0

    ip_match = IP_PATTERN.search(raw)
    rate_match = RATE_PATTERN.search(raw)
    target = ip_match.group(0) if ip_match else None
    rate = rate_match.group(0) if rate_match else None
    dst_port = None
    protocol = "udp" if "udp" in text_lower else "tcp"

    # Deteksi interface fisik eksplisit (etherX / wlan / bridge)
    ether_match = ETHER_PATTERN.search(raw)
    wlan_match = WLAN_PATTERN.search(raw)
    if not target:
        if ether_match:
            target = f"ether{ether_match.group(1)}"
        elif wlan_match:
            target = wlan_match.group(1).replace(" ", "").lower()

    # Deteksi dan disambiguasi 'port X'
    port_match = PORT_PATTERN.search(raw)
    if port_match:
        port_num = int(port_match.group(1))
        if intent in ("limit_bandwidth", "remove_limit"):
            target = f"ether{port_num}"
        elif intent in ("block_traffic", "unblock_traffic"):
            if port_num > 4 or target:
                dst_port = port_num
            else:
                target = f"ether{port_num}"

    # Deteksi alias layanan jika belum ada dst_port
    if dst_port is None and intent in ("block_traffic", "unblock_traffic"):
        for alias, p in SERVICE_ALIASES.items():
            if re.search(rf"\b{alias}\b", text_lower):
                dst_port = p
                break

    policy = build_network_policy(intent, target, rate, dst_port, protocol)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "raw_text": text,
        "intent": intent,
        "confidence": round(confidence, 4),
        "entities": {
            "target": target,
            "rate": rate,
            "dst_port": dst_port,
            "protocol": protocol if dst_port else None,
        },
        "policy": policy,
        "processing_time_ms": round(elapsed_ms, 3),
    }
