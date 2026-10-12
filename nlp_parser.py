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

NAT_DISABLE_WORDS = ("matikan", "disable", "nonaktifkan", "hapus", "cabut", "hilangkan", "off", "tutup")
NAT_ENABLE_WORDS = ("aktifkan", "enable", "hidupkan", "nyalakan", "pasang", "on", "buat", "buka")

IFACE_DISABLE_WORDS = ("matikan", "disable", "nonaktifkan", "padamkan", "tutup", "off", "putus")
IFACE_ENABLE_WORDS = ("aktifkan", "enable", "hidupkan", "nyalakan", "buka", "on")


ALL_ACTION_WORDS = (
    "aktifkan", "hidupkan", "nyalakan", "enable", "pasang", "buat", "buka", "aktif", "hidup", "nyala", "on",
    "matikan", "disable", "nonaktifkan", "padamkan", "tutup", "putus", "cabut", "hapus", "mati", "padam", "off",
    "batasi", "limit", "cekik", "pangkas", "kecilkan", "alokasikan", "atur", "set", "batas",
    "normalkan", "kembalikan", "unlimit", "hilangkan", "lepas", "bebaskan",
    "blokir", "drop", "tolak", "cegat", "isolasi", "unblock", "izinkan", "pulihkan", "bolehkan",
    "hentikan", "henti", "jatuhkan", "jatuh", "cut"
)


def normalize_indonesian_verbs(text: str) -> str:
    # Menggabungkan kata kerja berimbuhan yang terpisah spasi (contoh: 'aktif kan' -> 'aktifkan')
    t = re.sub(r"\b(aktif|mati|hidup|nyala|buka|tutup|padam|putus|cabut|hapus|pasang|hilang)\s+kan\b", r"\1kan", text, flags=re.I)
    t = re.sub(r"\b(batas)\s+i\b", r"\1i", t, flags=re.I)
    t = re.sub(r"\b(un)\s*(block|limit)\b", r"\1\2", t, flags=re.I)
    return t


def _has_word(words: tuple, text: str) -> bool:
    for w in words:
        if w in ("on", "off"):
            if re.search(rf"\b{w}\b", text):
                return True
        elif w in text:
            return True
    return False


def parse_intent(text: str) -> dict:
    t0 = time.perf_counter()
    raw = normalize_indonesian_verbs(text.strip() if isinstance(text, str) else "")

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
    elif any(w in text_lower for w in ("blokir", "drop")):
        intent = "block_traffic"
        confidence = 1.0

    ip_match = IP_PATTERN.search(raw)
    rate_match = RATE_PATTERN.search(raw)
    target = ip_match.group(0) if ip_match else None
    rate = rate_match.group(0) if rate_match else None
    dst_port = None
    protocol = "udp" if "udp" in text_lower else "tcp"

    if rate_match and any(w in text_lower for w in LIMIT_WORDS) and not any(w in text_lower for w in UNLIMIT_WORDS):
        intent = "limit_bandwidth"
        confidence = 1.0

    ether_match = ETHER_PATTERN.search(raw)
    wlan_match = WLAN_PATTERN.search(raw)
    if not target:
        if ether_match:
            target = f"ether{ether_match.group(1)}"
        elif wlan_match:
            target = wlan_match.group(1).replace(" ", "").lower()
        elif any(w in text_lower for w in ("wifi", "wi-fi", "wireless")):
            target = "wlan1"

    port_match = PORT_PATTERN.search(raw)
    if port_match:
        port_num = int(port_match.group(1))
        if intent in ("limit_bandwidth", "remove_limit", "enable_interface", "disable_interface", "enable_nat", "disable_nat"):
            target = f"ether{port_num}"
        elif intent in ("block_traffic", "unblock_traffic"):
            if port_num > 4 or target:
                dst_port = port_num
            else:
                target = f"ether{port_num}"

    if dst_port is None and intent in ("block_traffic", "unblock_traffic"):
        for alias, p in SERVICE_ALIASES.items():
            if re.search(rf"\b{alias}\b", text_lower):
                dst_port = p
                break

    if "nat" in text_lower or "masquerade" in text_lower:
        if _has_word(NAT_DISABLE_WORDS, text_lower):
            intent = "disable_nat"
            confidence = 1.0
        elif _has_word(NAT_ENABLE_WORDS, text_lower):
            intent = "enable_nat"
            confidence = 1.0
        if target is None:
            target = "ether1"

    if (
        (
            "interface" in text_lower
            or "antarmuka" in text_lower
            or "wifi" in text_lower
            or "wlan" in text_lower
            or ("port" in text_lower and rate is None and dst_port is None)
        )
        and "nat" not in text_lower
        and "masquerade" not in text_lower
        and "blokir" not in text_lower
        and "drop" not in text_lower
        and "limit" not in text_lower
        and "bandwidth" not in text_lower
        and "batasi" not in text_lower
    ):
        if _has_word(IFACE_DISABLE_WORDS, text_lower):
            intent = "disable_interface"
            confidence = 1.0
        elif _has_word(IFACE_ENABLE_WORDS, text_lower):
            intent = "enable_interface"
            confidence = 1.0

    if port_match and intent in ("enable_interface", "disable_interface", "enable_nat", "disable_nat"):
        target = f"ether{port_match.group(1)}"

    # Guard: Tolak kalimat sampah / gibberish tanpa kata kerja aksi yang jelas
    if not any(w in text_lower for w in ALL_ACTION_WORDS):
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "raw_text": text,
            "intent": "unknown",
            "confidence": round(confidence, 4),
            "entities": {
                "target": target,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": None,
            },
            "policy": {
                "intent": "unknown",
                "action": None,
                "target": target,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": None,
                "name": None,
                "is_valid": False,
                "error": "Perintah tidak dipahami atau tidak mengandung kata kerja aksi yang jelas (misal: 'aktifkan', 'matikan', 'batasi', 'blokir').",
            },
            "processing_time_ms": round(elapsed_ms, 3),
        }

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
