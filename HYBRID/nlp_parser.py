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
JALUR_PATTERN = re.compile(r"\bjalur\s*(\d+)\b", re.IGNORECASE)
ETHER_PATTERN = re.compile(r"\b(?:ethernet|ether)\s*(\d+)\b", re.IGNORECASE)
WLAN_PATTERN = re.compile(r"\b(wlan\s*\d+|bridge)\b", re.IGNORECASE)
ETH_PHYSICAL_PATTERN = re.compile(
    r"\b(?:port\s*lan|port\s*eth|kabel\s*lan|ethernet|ether|eth|lan|jalur|interfaces?|iface|colokan|kabel|link|int)\s*(\d+)\b"
    r"|\b(?:eth|ether|lan|int|iface)(\d+)\b"
    r"|\bport\s*([1-4])\b|\bport([1-4])\b",
    re.IGNORECASE,
)
ETHER_UNIFIED_PATTERN = ETH_PHYSICAL_PATTERN

SERVICE_ALIASES = {
    "http": 80,
    "https": 443,
    "ssh": 22,
    "dns": 53,
}

UNBLOCK_WORDS = ("buka", "unblock", "izinkan", "lepas", "lepaskan", "pulihkan", "bolehkan")
UNLIMIT_WORDS = (
    "hapus", "cabut", "unlimit", "hilangkan", "lepas", "lepaskan",
    "bebaskan", "reset", "kembalikan", "normalkan", "normalisasikan", "normalisasi",
    "jangan batasi", "jangan limit", "jangan",
)
LIMIT_WORDS = ("limit", "bandwidth", "kecepatan", "batasi", "cekik", "pangkas", "alokasikan", "batas", "batasan", "kendalikan")

CONFIDENCE_THRESHOLD = 0.50

REMOVE_VERBS = ("hapus", "cabut", "hilangkan", "buang", "delete", "remove", "bersihkan")
QOS_OBJECT_WORDS = (
    "limit", "kecepatan", "bandwidth", "pembatasan", "qos", "queue",
    "speed", "batasan", "batas", "rate", "limitasi", "transfer rate",
)
IP_OBJECT_WORDS = ("ip", "address", "alamat", "subnet")
FW_OBJECT_WORDS = (
    "blokir", "blokiran", "pemblokiran", "block", "drop", "firewall",
    "cegat", "pencegatan", "isolasi", "aturan drop", "paket", "koneksi", "akses",
)
NAT_OBJECT_WORDS = ("nat", "masquerade")

BLOCK_WORDS = (
    "blokir", "drop", "cegat", "isolasi", "tutup akses",
    "putus koneksi", "putus akses", "tolak semua",
)

NAT_DISABLE_WORDS = ("matikan", "disable", "nonaktifkan", "hapus", "cabut", "hilangkan", "off", "tutup")
NAT_ENABLE_WORDS = ("aktifkan", "enable", "hidupkan", "nyalakan", "pasang", "on", "buat", "buka", "terapkan", "jalankan")

IFACE_DISABLE_WORDS = ("matikan", "disable", "nonaktifkan", "padamkan", "tutup", "off", "putus")
IFACE_ENABLE_WORDS = ("aktifkan", "enable", "hidupkan", "nyalakan", "buka", "on")

QUERY_WORDS = ("cek", "periksa", "lihat", "tampilkan", "tampil", "inspeksi", "info")
ADD_WORDS = (
    "tambahkan", "tambah", "pasang", "pasangkan", "beri", "berikan",
    "masukkan", "input", "konfigurasi", "konfigurasikan", "tetapkan"
)
UPDATE_IP_WORDS = ("ganti", "ubah", "tukar", "replace", "update", "pindahkan", "gantikan", "setel ulang", "set ulang")

ALL_ACTION_WORDS = (
    "aktifkan", "hidupkan", "nyalakan", "enable", "pasang", "buat", "buka", "aktif", "hidup", "nyala", "on",
    "matikan", "disable", "nonaktifkan", "padamkan", "tutup", "putus", "cabut", "hapus", "mati", "padam", "off",
    "batasi", "limit", "cekik", "pangkas", "kecilkan", "alokasikan", "atur", "set", "batas", "kendalikan",
    "normalkan", "kembalikan", "unlimit", "hilangkan", "lepas", "lepaskan", "bebaskan", "normalisasikan", "normalisasi",
    "blokir", "drop", "tolak", "cegat", "isolasi", "unblock", "izinkan", "pulihkan", "bolehkan",
    "hentikan", "henti", "jatuhkan", "jatuh", "cut",
    "cek", "periksa", "lihat", "tampilkan", "tampil", "inspeksi", "info",
    "tambahkan", "tambah", "pasangkan", "beri", "berikan", "masukkan", "input", "konfigurasi", "konfigurasikan", "tetapkan",
    "ganti", "ubah", "tukar", "replace", "update", "pindahkan", "gantikan", "setel ulang", "set ulang",
    "terapkan", "jalankan", "jangan"
)


def normalize_indonesian_verbs(text: str) -> str:
    # Menggabungkan kata kerja berimbuhan yang terpisah spasi (contoh: 'aktif kan' -> 'aktifkan')
    t = re.sub(
        r"\b(aktif|mati|hidup|nyala|buka|tutup|padam|putus|cabut|hapus|pasang|hilang|tambah|masuk|beri)\s+kan\b",
        r"\1kan",
        text,
        flags=re.I,
    )
    t = re.sub(r"\b(batas)\s+i\b", r"\1i", t, flags=re.I)
    t = re.sub(r"\b(un)\s*(block|limit)\b", r"\1\2", t, flags=re.I)
    return t


def _extract_interfaces(text: str) -> list:
    found = []
    for m in ETHER_UNIFIED_PATTERN.finditer(text):
        num_m = re.search(r"\d+", m.group(0))
        if num_m:
            iface = f"ether{num_m.group(0)}"
            if iface not in found:
                found.append(iface)
    for m in WLAN_PATTERN.finditer(text):
        item = m.group(1).lower().replace(" ", "")
        if item in ("wifi", "wi-fi", "wireless"):
            item = "wlan1"
        if item not in found:
            found.append(item)
    return found


def _has_word(words: tuple, text: str) -> bool:
    for w in words:
        if re.search(rf"\b{re.escape(w)}\b", text):
            return True
    return False


def _is_ip_like(s: str) -> bool:
    if not isinstance(s, str):
        return False
    clean = s.strip().split("/")[0].strip()
    parts = clean.split(".")
    return len(parts) == 4 and all(p.isdigit() for p in parts)


def parse_intent(text: str) -> dict:
    t0 = time.perf_counter()
    raw = normalize_indonesian_verbs(text.strip() if isinstance(text, str) else "")

    probs = MODEL.predict_proba([raw])[0]
    best_idx = probs.argmax()
    intent = str(MODEL.classes_[best_idx])
    confidence = float(probs[best_idx])

    text_lower = raw.lower()
    ambiguous_removal = False

    if any(w in text_lower for w in UNBLOCK_WORDS) and (
        _has_word(FW_OBJECT_WORDS, text_lower) or "port" in text_lower
    ):
        intent = "unblock_traffic"
        confidence = 1.0
    elif any(w in text_lower for w in UNLIMIT_WORDS) and any(w in text_lower for w in LIMIT_WORDS):
        intent = "remove_limit"
        confidence = 1.0
    elif any(w in text_lower for w in REMOVE_VERBS):
        if _has_word(FW_OBJECT_WORDS, text_lower):
            intent = "unblock_traffic"
            confidence = 1.0
        elif _has_word(QOS_OBJECT_WORDS, text_lower):
            intent = "remove_limit"
            confidence = 1.0
        elif _has_word(IP_OBJECT_WORDS, text_lower):
            intent = "remove_ip_address"
            confidence = 1.0
        elif _has_word(NAT_OBJECT_WORDS, text_lower):
            intent = "disable_nat"
            confidence = 1.0
        else:
            ambiguous_removal = True
    elif any(w in text_lower for w in BLOCK_WORDS):
        intent = "block_traffic"
        confidence = 1.0
    elif any(w in text_lower for w in QUERY_WORDS) and _has_word(
        (
            "ip", "jalur", "port", "interface", "interfaces", "antarmuka",
            "ether", "ethernet", "eth", "lan", "int", "iface", "colokan", "kabel", "link",
        ),
        text_lower,
    ):
        intent = "get_interface_ip"
        confidence = 1.0
    elif (
        any(w in text_lower for w in UPDATE_IP_WORDS)
        and ("ip" in text_lower or IP_PATTERN.search(raw))
    ):
        intent = "update_ip_address"
        confidence = 1.0
    elif (
        any(w in text_lower for w in ADD_WORDS)
        and ("ip" in text_lower or IP_PATTERN.search(raw))
        and not any(w in text_lower for w in LIMIT_WORDS)
    ):
        intent = "add_ip_address"
        confidence = 1.0

    ip_match = IP_PATTERN.search(raw)
    rate_match = RATE_PATTERN.search(raw)
    target = ip_match.group(0) if ip_match else None
    rate = rate_match.group(0) if rate_match else None
    dst_port = None
    protocol = "udp" if "udp" in text_lower else "tcp"
    address = None
    interface = None

    if any(w in text_lower for w in LIMIT_WORDS) and not any(w in text_lower for w in REMOVE_VERBS) and not any(w in text_lower for w in UNLIMIT_WORDS):
        intent = "limit_bandwidth"
        confidence = 1.0

    unified_match = ETHER_UNIFIED_PATTERN.search(raw)
    port_match = PORT_PATTERN.search(raw)
    wlan_match = WLAN_PATTERN.search(raw)
    if not target:
        if ip_match and intent not in ("enable_interface", "disable_interface", "enable_nat", "disable_nat"):
            target = ip_match.group(0)
        elif wlan_match:
            target = wlan_match.group(1).replace(" ", "").lower()
        elif any(w in text_lower for w in ("wifi", "wi-fi", "wireless")):
            target = "wlan1"
        elif unified_match:
            num_m = re.search(r"\d+", unified_match.group(0))
            num = int(num_m.group(0)) if num_m else 1
            matched_str = unified_match.group(0).lower().strip()
            is_plain_port = (matched_str.startswith("port") or matched_str.startswith("port ")) and not any(
                matched_str.startswith(p) for p in ("port lan", "port eth", "portlan", "porteth")
            )
            if is_plain_port and intent in ("block_traffic", "unblock_traffic") and num > 4:
                dst_port = num
                target = None
            else:
                target = f"ether{num}"

    if port_match:
        port_num = int(port_match.group(1))
        if intent in ("block_traffic", "unblock_traffic"):
            if port_num > 4 or (target and target != f"ether{port_num}"):
                dst_port = port_num
            else:
                target = f"ether{port_num}"
        elif intent in ("limit_bandwidth", "remove_limit", "enable_interface", "disable_interface", "enable_nat", "disable_nat"):
            if not target:
                target = f"ether{port_num}"
    elif unified_match and intent in ("limit_bandwidth", "remove_limit", "enable_interface", "disable_interface", "enable_nat", "disable_nat"):
        num_m = re.search(r"\d+", unified_match.group(0))
        if num_m:
            target = f"ether{num_m.group(0)}"

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

    ether_detection_words = (
        "interface", "interfaces", "antarmuka", "wifi", "wlan",
        "port", "lan", "eth", "ether", "ethernet", "int", "iface", "colokan", "kabel", "link", "jalur",
    )
    if (
        (
            _has_word(ether_detection_words, text_lower)
            and rate is None
            and dst_port is None
            and ip_match is None
        )
        and "nat" not in text_lower
        and "masquerade" not in text_lower
        and "blokir" not in text_lower
        and "drop" not in text_lower
        and "limit" not in text_lower
        and "bandwidth" not in text_lower
        and "batasi" not in text_lower
        and intent not in ("get_interface_ip", "add_ip_address", "update_ip_address")
    ):
        if _has_word(IFACE_DISABLE_WORDS, text_lower):
            intent = "disable_interface"
            confidence = 1.0
        elif _has_word(IFACE_ENABLE_WORDS, text_lower):
            intent = "enable_interface"
            confidence = 1.0

    if unified_match and intent in ("enable_interface", "disable_interface", "enable_nat", "disable_nat"):
        num_m = re.search(r"\d+", unified_match.group(0))
        if num_m:
            target = f"ether{num_m.group(0)}"
    elif port_match and intent in ("enable_interface", "disable_interface", "enable_nat", "disable_nat"):
        target = f"ether{port_match.group(1)}"

    if intent == "get_interface_ip":
        if any(w in text_lower for w in ("semua", "seluruh")):
            target = None
            interface = None
        else:
            ifaces = _extract_interfaces(raw)
            if len(ifaces) > 1:
                target = ifaces
                interface = ifaces
            elif len(ifaces) == 1:
                target = ifaces[0]
                interface = ifaces[0]
            else:
                target = None
                interface = None
        address = None
        rate = None
        dst_port = None
    elif intent == "update_ip_address":
        address = ip_match.group(0) if ip_match else None
        ifaces = _extract_interfaces(raw)
        interface = ifaces[0] if ifaces else None
        target = interface
        rate = None
        dst_port = None
    elif intent in ("add_ip_address", "remove_ip_address"):
        address = ip_match.group(0) if ip_match else None
        ifaces = _extract_interfaces(raw)
        interface = ifaces[0] if ifaces else None
        target = interface or address
        rate = None
        dst_port = None
    elif intent in ("enable_interface", "disable_interface", "enable_nat", "disable_nat"):
        interface = target

    if ambiguous_removal:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        target_display = target or (f"port {port_match.group(1)}" if port_match else None)
        if target_display and (
            str(target_display).startswith("ether")
            or any(k in text_lower for k in ("port", "lan", "eth", "colokan", "int", "iface", "jalur"))
        ):
            ambiguity_error = (
                f"Perintah ambigu: Port fisik ({target_display}) tidak dapat dihapus dari hardware router. "
                f"Gunakan 'matikan {target_display}' untuk menonaktifkan interface, "
                f"'hapus limit {target_display}' untuk mencabut batasan bandwidth, "
                f"atau 'hapus ip {target_display}' untuk menghapus alamat IP."
            )
        elif isinstance(target, str) and _is_ip_like(target):
            ambiguity_error = (
                f"Perintah ambigu: Harap tentukan konfigurasi untuk {target} yang ingin dihapus "
                f"(misal: 'hapus limit {target}', 'buka blokir {target}', atau 'hapus ip {target}')."
            )
        else:
            ambiguity_error = (
                "Perintah ambigu: Harap sebutkan konfigurasi spesifik yang ingin dihapus "
                "(misal: 'hapus limit port 1', 'hapus ip 10.10.10.1', atau 'buka blokir port 80')."
            )

        return {
            "raw_text": text,
            "intent": "unknown",
            "confidence": round(confidence, 4),
            "entities": {
                "target": target,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": None,
                "address": address,
                "interface": interface,
            },
            "policy": {
                "intent": "unknown",
                "action": None,
                "target": target,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": None,
                "address": address,
                "interface": interface,
                "name": None,
                "is_valid": False,
                "error": ambiguity_error,
            },
            "processing_time_ms": round(elapsed_ms, 3),
        }

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
                "address": address,
                "interface": interface,
            },
            "policy": {
                "intent": "unknown",
                "action": None,
                "target": target,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": None,
                "address": address,
                "interface": interface,
                "name": None,
                "is_valid": False,
                "error": "Perintah tidak dipahami atau tidak mengandung kata kerja aksi yang jelas (misal: 'aktifkan', 'matikan', 'batasi', 'blokir').",
            },
            "processing_time_ms": round(elapsed_ms, 3),
        }

    # Guard: Tolak jika tingkat keyakinan model di bawah ambang batas minimum
    if confidence < CONFIDENCE_THRESHOLD:
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
                "address": address,
                "interface": interface,
            },
            "policy": {
                "intent": "unknown",
                "action": None,
                "target": target,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": None,
                "address": address,
                "interface": interface,
                "name": None,
                "is_valid": False,
                "error": (
                    f"Tingkat keyakinan sistem terlalu rendah ({confidence * 100:.2f}% < {CONFIDENCE_THRESHOLD * 100:.1f}%). "
                    "Harap berikan perintah konfigurasi yang lebih spesifik."
                ),
            },
            "processing_time_ms": round(elapsed_ms, 3),
        }

    policy = build_network_policy(intent, target, rate, dst_port, protocol, address=address, interface=interface)
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
            "address": address,
            "interface": interface,
        },
        "policy": policy,
        "processing_time_ms": round(elapsed_ms, 3),
    }
