import re
import time
from pathlib import Path
import joblib
from policy_engine import build_network_policy

MODEL_PATH = Path(__file__).parent / "intent_model.joblib"
MODEL = joblib.load(MODEL_PATH)
MODEL.predict_proba(["warmup"])

IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")
SITE_PATTERN = re.compile(r"\b(?:https?://)?(?:www\.)?([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)\b", re.IGNORECASE)
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
LIMIT_WORDS = (
    "limit", "dilimit", "bandwidth", "kecepatan", "batasi", "dibatasi",
    "cekik", "dicekik", "pangkas", "dipangkas", "alokasikan", "batas",
    "batasan", "kendalikan", "speed", "data rate",
)

CONFIDENCE_THRESHOLD = 0.50

REMOVE_VERBS = ("hapus", "cabut", "hilangkan", "buang", "delete", "remove", "bersihkan")
QOS_OBJECT_WORDS = (
    "limit", "dilimit", "kecepatan", "bandwidth", "pembatasan", "qos", "queue",
    "speed", "batasan", "batas", "rate", "limitasi", "transfer rate", "dicekik", "dipangkas",
)
IP_OBJECT_WORDS = ("ip", "address", "alamat", "subnet")
FW_OBJECT_WORDS = (
    "blokir", "diblokir", "blokiran", "pemblokiran", "block", "drop", "di-drop", "didrop",
    "firewall", "cegat", "dicegat", "pencegatan", "isolasi", "diisolasi", "aturan drop",
    "paket", "koneksi", "akses", "tutup", "ditutup", "putus", "diputus", "pencegahan", "blacklist",
    "situs", "website", "web", "domain", "cekal",
)
NAT_OBJECT_WORDS = ("nat", "masquerade", "sharing internet", "akses internet", "internet nat")
PING_WORDS = ("ping", "icmp", "latency", "latensi", "rtt", "reachability", "keterjangkauan", "echo")
DNS_WORDS = ("dns", "dns cache", "cache dns", "resolver", "lookup", "cache nama domain", "cache domain", "riwayat domain")
HEALTH_WORDS = ("system resource", "resource", "kesehatan", "hardware", "cpu", "ram", "memori", "uptime", "overload", "board name", "beban router")

BLOCK_WORDS = (
    "blokir", "drop", "cegat", "isolasi", "tutup akses",
    "putus koneksi", "putus akses", "tolak semua", "cekal",
)

NAT_DISABLE_WORDS = ("matikan", "disable", "nonaktifkan", "hapus", "cabut", "hilangkan", "off", "tutup")
NAT_ENABLE_WORDS = ("aktifkan", "enable", "hidupkan", "nyalakan", "pasang", "on", "buat", "buka", "terapkan", "jalankan")

IFACE_DISABLE_WORDS = ("matikan", "disable", "nonaktifkan", "padamkan", "tutup", "off", "putus")
IFACE_ENABLE_WORDS = ("aktifkan", "enable", "hidupkan", "nyalakan", "buka", "on")

QUERY_WORDS = (
    "cek", "periksa", "lihat", "tampilkan", "tampil", "inspeksi", "info",
    "siapa", "apakah", "daftar", "status", "pantau", "monitoring", "berapa",
    "bagaimana", "ada siapa", "mana saja",
)
QUESTION_TAGS = ("gak", "nggak", "kah", "belum", "sih", "gimana")

FORWARD_WORDS = ("forward", "forwarding", "dstnat", "dst-nat", "redirect", "petakan", "arahkan", "teruskan", "lempar", "tembusin", "salurkan", "mapping", "mengarah")
PORT_FORWARD_OBJECTS = ("port forward", "port forwarding", "dst-nat", "dstnat", "mapping port", "pemetaan port", "redirect port", "forward port")

ADD_WORDS = (
    "tambahkan", "tambah", "pasang", "pasangkan", "beri", "berikan",
    "masukkan", "input", "konfigurasi", "konfigurasikan", "tetapkan", "buat"
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
    "siapa", "apakah", "daftar", "status", "pantau", "monitoring", "berapa", "bagaimana", "tabel",
    "tambahkan", "tambah", "pasangkan", "beri", "berikan", "masukkan", "input", "konfigurasi", "konfigurasikan", "tetapkan",
    "ganti", "ubah", "tukar", "replace", "update", "pindahkan", "gantikan", "setel ulang", "set ulang",
    "terapkan", "jalankan", "jangan", "bisa", "internetan", "diteruskan", "teruskan", "forward", "mapping", "translasi",
    "sharing", "gak", "nggak", "belum", "sudah", "lempar", "tembusin", "tembuskan", "salurkan", "petakan", "redirect", "hubungkan", "sambungkan", "batalkan", "arahkan",
    "ping", "icmp", "latency", "latensi", "rtt", "flush", "dns", "resource", "kesehatan", "hardware", "cpu", "ram", "memori", "uptime", "kosongkan", "bersihkan", "clear",
    "terima", "perbarui", "buang", "refresh"
)


def normalize_indonesian_verbs(text: str) -> str:
    # Menggabungkan kata kerja berimbuhan yang terpisah spasi (contoh: 'aktif kan' -> 'aktifkan')
    t = re.sub(
        r"\b(aktif|mati|hidup|nyala|buka|tutup|padam|putus|cabut|hapus|pasang|hilang|tambah|masuk|beri|bersih)\s+kan\b",
        r"\1kan",
        text,
        flags=re.I,
    )
    t = re.sub(r"\b(bersih)\s*in\b", r"\1kan", t, flags=re.I)
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
    is_explicit_query = _has_word(("apakah", "cek", "periksa", "lihat", "tampilkan", "siapa", "daftar", "status", "pantau", "monitoring", "berapa", "bagaimana"), text_lower)
    has_remove_verb = (any(w in text_lower for w in REMOVE_VERBS) or any(w in text_lower for w in UNBLOCK_WORDS) or any(w in text_lower for w in UNLIMIT_WORDS)) and not is_explicit_query
    if any(w in text_lower for w in ("bersihkan daftar drop", "hapus semua aturan blokir", "buka semua pemblokiran")):
        has_remove_verb = True
        is_explicit_query = False
    is_query = is_explicit_query or ((_has_word(QUERY_WORDS, text_lower) or _has_word(QUESTION_TAGS, text_lower)) and not has_remove_verb)

    is_port_forward_domain = (
        _has_word(FORWARD_WORDS, text_lower)
        or _has_word(PORT_FORWARD_OBJECTS, text_lower)
        or "dst-nat" in text_lower
        or "dstnat" in text_lower
    )
    is_port_forward_action = is_port_forward_domain and not any(w in text_lower for w in ("tidak di-forward", "jangan di-forward", "jangan forward", "batal forward", "hapus", "cabut", "batalkan", "jangan", "hentikan", "tutup", "lepas", "hilangkan", "kembalikan port"))

    if is_query:
        if _has_word(HEALTH_WORDS, text_lower):
            intent = "get_system_health"
            confidence = 1.0
        elif _has_word(PING_WORDS, text_lower):
            intent = "ping_host"
            confidence = 1.0
        elif _has_word(DNS_WORDS, text_lower) and any(w in text_lower for w in ("flush", "bersihkan", "reset", "hapus", "clear", "kosongkan")):
            intent = "flush_dns_cache"
            confidence = 1.0
        elif _has_word(NAT_OBJECT_WORDS + ("nat", "masquerade", "sharing internet", "berbagi koneksi", "port forwarding", "forwarding", "dst-nat", "dstnat", "mapping", "translasi", "diteruskan", "teruskan", "forward"), text_lower):
            intent = "get_nat_status"
            confidence = 1.0
        elif _has_word(LIMIT_WORDS + QOS_OBJECT_WORDS + ("antrean", "antrian", "speed", "limitnya"), text_lower):
            intent = "get_bandwidth_status"
            confidence = 1.0
        elif _has_word(FW_OBJECT_WORDS + ("blokir", "drop", "cegat", "pencekalan", "pencegahan", "blacklist", "internetan", "port layanan"), text_lower):
            intent = "get_firewall_status"
            confidence = 1.0
        elif _has_word(
            (
                "ip", "jalur", "port", "interface", "interfaces", "antarmuka",
                "ether", "ethernet", "eth", "lan", "int", "iface", "colokan", "kabel", "link", "telemetri", "telemetry", "mac",
            ),
            text_lower,
        ):
            intent = "get_interface_ip"
            confidence = 1.0
    elif any(w in text_lower for w in ("flush", "kosongkan", "bersihkan", "clear", "reset", "perbarui")) and _has_word(DNS_WORDS, text_lower):
        intent = "flush_dns_cache"
        confidence = 1.0
    elif any(w in text_lower for w in REMOVE_VERBS) and ("cache" in text_lower or "dns" in text_lower) and _has_word(DNS_WORDS, text_lower):
        intent = "flush_dns_cache"
        confidence = 1.0
    elif _has_word(("ping", "icmp"), text_lower):
        intent = "ping_host"
        confidence = 1.0
    elif _has_word(("system resource", "resource router", "resource hardware", "kesehatan router", "kesehatan hardware", "beban cpu", "sisa ram"), text_lower) and not is_port_forward_action:
        intent = "get_system_health"
        confidence = 1.0
    elif any(w in text_lower for w in ("batalkan", "jangan", "hentikan", "cabut", "hapus", "tutup", "lepas", "hilangkan", "kembalikan")) and (
        _has_word(PORT_FORWARD_OBJECTS + ("forward", "forwarding", "lempar", "lemparan", "dst-nat", "dstnat", "pemetaan port", "mapping port"), text_lower)
    ):
        intent = "remove_port_forward"
        confidence = 1.0
    elif is_port_forward_action and not any(w in text_lower for w in ("hapus", "cabut", "batalkan", "jangan", "hentikan", "tutup", "lepas", "hilangkan", "buka blokir")):
        intent = "add_port_forward"
        confidence = 1.0
    elif any(w in text_lower for w in UNLIMIT_WORDS) and (any(w in text_lower for w in LIMIT_WORDS) or "bandwidth" in text_lower):
        intent = "remove_limit"
        confidence = 1.0
    elif any(w in text_lower for w in UNBLOCK_WORDS) and (
        _has_word(FW_OBJECT_WORDS, text_lower) or "port" in text_lower or _is_ip_like(raw) or IP_PATTERN.search(raw)
    ) and not any(w in text_lower for w in ("bandwidth", "kecepatan", "speed")):
        intent = "unblock_traffic"
        confidence = 1.0
    elif any(w in text_lower for w in REMOVE_VERBS):
        if _has_word(QOS_OBJECT_WORDS, text_lower):
            intent = "remove_limit"
            confidence = 1.0
        elif _has_word(PORT_FORWARD_OBJECTS + ("forward", "forwarding", "pemetaan", "mapping", "dst-nat", "dstnat"), text_lower):
            intent = "remove_port_forward"
            confidence = 1.0
        elif _has_word(FW_OBJECT_WORDS + ("drop", "drop rule", "rule drop", "aturan drop"), text_lower):
            intent = "unblock_traffic"
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
        and not is_port_forward_action
    ):
        intent = "add_ip_address"
        confidence = 1.0

    ip_match = IP_PATTERN.search(raw)
    rate_match = RATE_PATTERN.search(raw)
    target = ip_match.group(0) if ip_match else None
    rate = rate_match.group(0) if rate_match else None
    dst_port = None
    to_port = None
    protocol = "udp" if "udp" in text_lower else "tcp"
    address = None
    interface = None

    if any(w in text_lower for w in LIMIT_WORDS) and not any(w in text_lower for w in REMOVE_VERBS) and not any(w in text_lower for w in UNLIMIT_WORDS) and not is_query:
        intent = "limit_bandwidth"
        confidence = 1.0

    unified_match = ETHER_UNIFIED_PATTERN.search(raw)
    port_match = PORT_PATTERN.search(raw)
    wlan_match = WLAN_PATTERN.search(raw)
    site_match = SITE_PATTERN.search(raw)
    if not target:
        if any(w in text_lower for w in ("semua", "seluruh", "semuanya", "daftar", "seluruhnya")) and intent in ("remove_limit", "unblock_traffic", "disable_nat"):
            target = "all"
        elif site_match and intent in ("block_traffic", "unblock_traffic"):
            target = site_match.group(1).lower()
            dst_port = 443
            protocol = "tcp"
        elif ip_match and intent not in ("enable_interface", "disable_interface", "enable_nat", "disable_nat"):
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

    if ("nat" in text_lower or "masquerade" in text_lower) and not is_query and not is_port_forward_domain:
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
        and intent not in ("get_interface_ip", "add_ip_address", "update_ip_address", "get_bandwidth_status", "get_firewall_status", "get_nat_status", "add_port_forward", "remove_port_forward")
        and not is_query
        and not is_port_forward_domain
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

    if intent in ("get_interface_ip", "get_bandwidth_status", "get_firewall_status", "get_nat_status"):
        if any(w in text_lower for w in ("semua", "seluruh", "all")):
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
            elif ip_match:
                target = ip_match.group(0)
                interface = None
            else:
                target = None
                interface = None
        address = None
        rate = None
        if intent != "get_firewall_status":
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
    elif intent == "add_port_forward":
        # Extract external port vs internal port
        # Find all port numbers in string
        raw_ports = [int(m.group(1)) for m in re.finditer(r"\bport\s*(\d+)\b", raw, re.I)]
        standalone_nums = [int(n) for n in re.findall(r"\b(\d+)\b", raw) if not any(n == octet for octet in (ip_match.group(0).split(".") if ip_match else []))]
        
        target = ip_match.group(0) if ip_match else None
        address = target

        if len(raw_ports) >= 2:
            dst_port = raw_ports[0]
            to_port = raw_ports[1]
        elif len(raw_ports) == 1:
            dst_port = raw_ports[0]
            to_port = raw_ports[0]
        elif standalone_nums:
            dst_port = standalone_nums[0]
            to_port = standalone_nums[1] if len(standalone_nums) > 1 else standalone_nums[0]
        else:
            dst_port = None
            to_port = None

        if "udp" in text_lower:
            protocol = "udp"
        else:
            protocol = "tcp"
    elif intent == "remove_port_forward":
        raw_ports = [int(m.group(1)) for m in re.finditer(r"\bport\s*(\d+)\b", raw, re.I)]
        standalone_nums = [int(n) for n in re.findall(r"\b(\d+)\b", raw) if not any(n == octet for octet in (ip_match.group(0).split(".") if ip_match else []))]
        
        target = ip_match.group(0) if ip_match else None
        if any(w in text_lower for w in ("semua", "seluruh", "semuanya")):
            dst_port = "all"
        elif raw_ports:
            dst_port = raw_ports[0]
        elif standalone_nums:
            dst_port = standalone_nums[0]
        else:
            dst_port = None
        to_port = None
        protocol = "udp" if "udp" in text_lower else "tcp"
    elif intent == "ping_host":
        # Extract target host (IP or Domain)
        if ip_match:
            target = ip_match.group(0)
        else:
            # Look for domain like google.com, unsil.ac.id, etc.
            domain_m = re.search(r"\b([a-zA-Z0-9\-]+\.(?:com|org|net|id|ac\.id|co\.id|io|edu|gov))\b", raw, re.I)
            if domain_m:
                target = domain_m.group(1).lower()
            else:
                # Fallback to word after 'ping'
                ping_after = re.search(r"\bping\s+(?:ke\s+|host\s+|server\s+|ip\s+|domain\s+)?([a-zA-Z0-9\.\-_]+)", raw, re.I)
                if ping_after and ping_after.group(1).lower() not in ("ke", "dong", "dulu", "test", "tes"):
                    target = ping_after.group(1)
                else:
                    target = None
        
        # Extract count if mentioned (e.g., 'count 4' or '4 kali')
        count_m = re.search(r"\b(?:count\s*(\d+)|(\d+)\s*kali)\b", text_lower)
        if count_m:
            dst_port = int(count_m.group(1) or count_m.group(2))
        else:
            dst_port = 4  # Default INV-DIAG-01 count
    elif intent in ("flush_dns_cache", "get_system_health"):
        target = None
        dst_port = None

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

    if intent != "add_port_forward":
        to_port = None

    policy = build_network_policy(intent, target, rate, dst_port, protocol, address=address, interface=interface, to_port=to_port)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "raw_text": text,
        "intent": intent,
        "confidence": round(confidence, 4),
        "entities": {
            "target": target,
            "rate": rate,
            "dst_port": dst_port,
            "to_port": to_port if intent == "add_port_forward" else None,
            "protocol": protocol if dst_port else None,
            "address": address,
            "interface": interface,
        },
        "policy": policy,
        "processing_time_ms": round(elapsed_ms, 3),
    }
