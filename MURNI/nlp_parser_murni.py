import re
import time
from pathlib import Path
import joblib
from policy_engine import build_network_policy

MODEL_PATH = Path(__file__).parent / "intent_model_murni.joblib"
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


def parse_intent_murni(text: str) -> dict:
    """
    Parser NLP Murni (Pure Machine Learning):
    - 100% klasifikasi intent mengandalkan probabilitas statistik Scikit-Learn TF-IDF.
    - Tanpa aturan sintaksis penimpa (No Syntactic Cue Override).
    - Tanpa normalisasi morfologi imbuhan (No Morphological Join).
    - Tanpa semantic action verb guard.
    """
    t0 = time.perf_counter()
    raw = text.strip() if isinstance(text, str) else ""

    # 1. PURE MACHINE LEARNING INTENT CLASSIFICATION
    probs = MODEL.predict_proba([raw])[0]
    best_idx = probs.argmax()
    intent = str(MODEL.classes_[best_idx])
    confidence = float(probs[best_idx])

    # 2. STANDARD BASIC ENTITY EXTRACTION
    ip_match = IP_PATTERN.search(raw)
    rate_match = RATE_PATTERN.search(raw)
    port_match = PORT_PATTERN.search(raw)
    ether_match = ETHER_PATTERN.search(raw)
    wlan_match = WLAN_PATTERN.search(raw)

    target = ip_match.group(0) if ip_match else None
    rate = rate_match.group(0) if rate_match else None
    dst_port = None
    protocol = "tcp"

    if not target:
        if ether_match:
            target = f"ether{ether_match.group(1)}"
        elif wlan_match:
            target = wlan_match.group(1).replace(" ", "").lower()
        elif port_match:
            port_num = int(port_match.group(1))
            if port_num <= 4:
                target = f"ether{port_num}"
            else:
                dst_port = port_num

    if port_match and not dst_port:
        port_num = int(port_match.group(1))
        if port_num > 4 or target is not None:
            dst_port = port_num

    # 3. BUILD POLICY VIA POLICY ENGINE
    policy = build_network_policy(
        intent=intent,
        target=target,
        rate=rate,
        dst_port=dst_port,
        protocol=protocol,
    )
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


# Alias kompatibel
parse_intent = parse_intent_murni
