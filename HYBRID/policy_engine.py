import ipaddress
import re
from typing import Optional, Tuple, Union
from config import ROUTER_HOST
from mikrotik_adapter import (
    apply_bandwidth_limit,
    remove_bandwidth_limit,
    apply_firewall_block,
    remove_firewall_block,
    enable_interface,
    disable_interface,
    enable_nat,
    disable_nat,
    get_bandwidth_limits,
    get_firewall_blocks,
    get_nat_rules,
    get_ip_addresses,
    get_interface_telemetry,
    add_ip_address,
    remove_ip_address,
    update_ip_address,
    add_port_forward,
    remove_port_forward,
    ping_host,
    flush_dns_cache,
    get_system_health,
    MANAGEMENT_IPS,
    MANAGEMENT_INTERFACES,
    MikroTikAdapter,
)

PROTECTED_IPS = {"127.0.0.1", "192.168.88.1", ROUTER_HOST}
VALID_INTERFACES = {"ether1", "ether2", "ether3", "ether4", "wlan1", "bridge", "pwr-line1"}
SUPPORTED_INTENTS = {
    "limit_bandwidth": "apply_bandwidth_limit",
    "remove_limit": "remove_bandwidth_limit",
    "block_traffic": "apply_firewall_block",
    "unblock_traffic": "remove_firewall_block",
    "enable_interface": "enable_interface",
    "disable_interface": "disable_interface",
    "enable_nat": "enable_nat",
    "disable_nat": "disable_nat",
    "get_bandwidth_status": "get_bandwidth_limits",
    "get_firewall_status": "get_firewall_blocks",
    "get_nat_status": "get_nat_rules",
    "get_interface_ip": "get_interface_telemetry",
    "add_ip_address": "add_ip_address",
    "remove_ip_address": "remove_ip_address",
    "update_ip_address": "update_ip_address",
    "add_port_forward": "add_port_forward",
    "remove_port_forward": "remove_port_forward",
    "ping_host": "ping_host",
    "flush_dns_cache": "flush_dns_cache",
    "get_system_health": "get_system_health",
}


def _parse_single_rate(s: str) -> str:
    s = s.strip().lower()
    if not s:
        raise ValueError("Rate string cannot be empty")

    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*([a-z]+)$", s)
    if not m:
        raise ValueError(f"Invalid rate format: '{s}'")

    num_str, unit = m.group(1), m.group(2)
    val = float(num_str)
    if val <= 0:
        raise ValueError(f"Rate must be positive: '{s}'")

    if unit in ("m", "mb", "mbps", "mega", "megabit", "megabits", "mbit"):
        if val.is_integer():
            return f"{int(val)}M"
        k_val = val * 1000
        return f"{int(k_val)}k" if k_val.is_integer() else f"{k_val:g}k"

    if unit in ("k", "kb", "kbps", "kilo", "kilobit", "kilobits", "kbit"):
        return f"{int(val)}k"

    if unit in ("g", "gb", "gbps", "giga", "gigabit", "gigabits", "gbit"):
        m_val = val * 1000
        return f"{int(m_val)}M" if m_val.is_integer() else f"{int(m_val * 1000)}k"

    raise ValueError(f"Unrecognized rate unit: '{unit}'")


def normalize_rate(rate_str: str) -> str:
    if not isinstance(rate_str, str) or not rate_str.strip():
        raise ValueError("Rate string cannot be empty")
    s = rate_str.strip()
    if "/" in s:
        parts = s.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid rate format: '{rate_str}'")
        return f"{_parse_single_rate(parts[0])}/{_parse_single_rate(parts[1])}"
    single = _parse_single_rate(s)
    return f"{single}/{single}"


IFACE_PREFIX_PATTERN = re.compile(
    r"^(?:port\s*lan|port\s*eth|kabel\s*lan|jalur\s*kabel|port|ethernet|ether|eth|lan|jalur|interfaces?|iface|colokan|kabel|link|int)\s*(\d+)$"
    r"|^(?:eth|ether|lan|int|port|iface)(\d+)$",
    re.IGNORECASE,
)


def _normalize_interface_str(tgt_str: str) -> str:
    s = str(tgt_str).strip().lower()
    m = IFACE_PREFIX_PATTERN.match(s)
    if m:
        num = m.group(1) or m.group(2)
        return f"ether{num}"
    if s in ("wifi", "wi-fi", "wireless"):
        return "wlan1"
    return s


def normalize_ip_address(addr_str: str) -> str:
    if not isinstance(addr_str, str) or not addr_str.strip():
        raise ValueError("IP address cannot be empty")
    s = addr_str.strip()
    if "/" not in s:
        s = f"{s}/24"
    iface = ipaddress.ip_interface(s)
    return str(iface)


def _is_ip_like(s: str) -> bool:
    if not isinstance(s, str):
        return False
    clean = s.strip().split("/")[0].strip()
    parts = clean.split(".")
    return len(parts) == 4 and all(p.isdigit() for p in parts)


def normalize_target(target_str: str) -> str:
    if not isinstance(target_str, str) or not target_str.strip():
        raise ValueError("Target IP cannot be empty")
    s = str(target_str).strip().lower()
    if s in ("all", "semua", "seluruh"):
        return "all"
    norm_iface = _normalize_interface_str(s)
    if norm_iface in VALID_INTERFACES:
        return norm_iface
    if re.match(r"^(?:ether\d+|wlan\d+|bridge\d*)$", norm_iface):
        raise ValueError(f"Interface {norm_iface} tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)")
    if re.match(r"^(?:[a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$", s):
        return s
    if "/" in s:
        return str(ipaddress.ip_network(s, strict=False))
    return f"{ipaddress.ip_address(s)}/32"


def check_safety(target: Optional[str], action: str) -> Tuple[bool, str]:
    act = action.lower() if isinstance(action, str) else ""
    if "block" not in act and "drop" not in act:
        return True, ""
    if not target or str(target).lower() in ("all", "semua", "seluruh"):
        return True, ""
    if target in VALID_INTERFACES:
        return True, ""
    if not _is_ip_like(str(target)):
        return True, ""

    clean_target = target.strip().split("/")[0]
    if clean_target in PROTECTED_IPS:
        return False, f"Anti-lockout: Dilarang memblokir IP router/gateway ({clean_target})"

    try:
        net = (
            ipaddress.ip_network(target.strip(), strict=False)
            if "/" in target
            else ipaddress.ip_network(f"{target.strip()}/32")
        )
        for p in PROTECTED_IPS:
            if p and ipaddress.ip_address(p) in net:
                return False, f"Anti-lockout: Dilarang memblokir subnet yang mencakup router IP ({p})"
    except ValueError:
        pass

    return True, ""


def build_network_policy(
    intent: str,
    target: Optional[Union[str, list]] = None,
    rate: Optional[str] = None,
    dst_port: Optional[Union[str, int]] = None,
    protocol: Optional[str] = "tcp",
    address: Optional[str] = None,
    interface: Optional[str] = None,
    to_port: Optional[Union[str, int]] = None,
) -> dict:
    intent_norm = intent.strip().lower() if isinstance(intent, str) else ""
    if intent_norm not in SUPPORTED_INTENTS:
        return {
            "intent": intent,
            "action": None,
            "target": target,
            "rate": rate,
            "dst_port": dst_port,
            "protocol": protocol,
            "address": address,
            "interface": interface,
            "name": None,
            "is_valid": False,
            "error": f"Intent tidak dikenali: '{intent}'",
        }

    action = SUPPORTED_INTENTS[intent_norm]

    if intent_norm in ("enable_interface", "disable_interface"):
        if not target or not str(target).strip():
            return {
                "intent": intent_norm,
                "action": action,
                "target": None,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": protocol,
                "name": None,
                "is_valid": False,
                "error": "Target interface wajib diisi",
            }
        tgt = _normalize_interface_str(str(target))

        if tgt not in VALID_INTERFACES:
            return {
                "intent": intent_norm,
                "action": action,
                "target": tgt,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": protocol,
                "name": None,
                "is_valid": False,
                "error": f"Interface {tgt} tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)",
            }

        if intent_norm == "disable_interface" and tgt in MANAGEMENT_INTERFACES:
            return {
                "intent": intent_norm,
                "action": action,
                "target": tgt,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": protocol,
                "name": None,
                "is_valid": False,
                "error": f"Anti-lockout: Dilarang mematikan interface manajemen ({tgt}) karena sedang digunakan Controller!",
            }

        return {
            "intent": intent_norm,
            "action": action,
            "target": tgt,
            "rate": None,
            "dst_port": None,
            "protocol": None,
            "name": f"iface_{tgt}",
            "is_valid": True,
            "error": None,
        }

    if intent_norm in ("enable_nat", "disable_nat"):
        out_interface = _normalize_interface_str(str(target)) if target and str(target).strip() else "ether1"
        comment = "IBN_NAT_MASQ"
        return {
            "intent": intent_norm,
            "action": action,
            "target": out_interface,
            "out_interface": out_interface,
            "comment": comment,
            "rate": None,
            "dst_port": None,
            "protocol": None,
            "name": f"nat_{out_interface}",
            "is_valid": True,
            "error": None,
        }

    if intent_norm == "get_interface_ip":
        raw_target = target if target is not None else interface
        if not raw_target:
            norm_target = None
        elif isinstance(raw_target, (list, tuple)):
            norm_target = []
            for item in raw_target:
                tgt = _normalize_interface_str(item)
                if tgt not in VALID_INTERFACES:
                    return {
                        "intent": intent_norm,
                        "action": action,
                        "target": tgt,
                        "address": None,
                        "interface": tgt,
                        "rate": None,
                        "dst_port": None,
                        "protocol": None,
                        "name": None,
                        "is_valid": False,
                        "error": f"Interface {tgt} tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)",
                    }
                norm_target.append(tgt)
        else:
            tgt = _normalize_interface_str(str(raw_target))
            if tgt not in VALID_INTERFACES:
                return {
                    "intent": intent_norm,
                    "action": action,
                    "target": tgt,
                    "address": None,
                    "interface": tgt,
                    "rate": None,
                    "dst_port": None,
                    "protocol": None,
                    "name": None,
                    "is_valid": False,
                    "error": f"Interface {tgt} tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)",
                }
            norm_target = tgt

        return {
            "intent": intent_norm,
            "action": action,
            "target": norm_target,
            "address": None,
            "interface": norm_target,
            "rate": None,
            "dst_port": None,
            "protocol": None,
            "name": "check_ip",
            "is_valid": True,
            "error": None,
        }

    if intent_norm in ("get_bandwidth_status", "get_firewall_status", "get_nat_status"):
        return {
            "intent": intent_norm,
            "action": action,
            "target": target,
            "address": address,
            "interface": interface,
            "rate": rate,
            "dst_port": dst_port,
            "protocol": protocol,
            "name": f"show_{intent_norm}",
            "is_valid": True,
            "error": None,
        }

    if intent_norm == "add_port_forward":
        # Target internal host
        cand_addr = address or target
        if not cand_addr:
            return {
                "intent": intent_norm,
                "action": action,
                "target": None,
                "address": None,
                "dst_port": dst_port,
                "name": None,
                "is_valid": False,
                "error": "Alamat IP internal (to_address) wajib diisi untuk port forwarding",
            }
        cand_str = str(cand_addr).strip()
        if "/" in cand_str:
            return {
                "intent": intent_norm,
                "action": action,
                "target": cand_str,
                "address": cand_str,
                "dst_port": dst_port,
                "name": None,
                "is_valid": False,
                "error": f"INV-NAT-02: Alamat IP internal wajib berupa single host IP valid, bukan subnet ({cand_str})",
            }
        try:
            ip_obj = ipaddress.ip_address(cand_str)
            if ip_obj.is_multicast or ip_obj.is_loopback:
                raise ValueError()
        except Exception:
            return {
                "intent": intent_norm,
                "action": action,
                "target": cand_str,
                "address": cand_str,
                "dst_port": dst_port,
                "name": None,
                "is_valid": False,
                "error": f"Alamat IP internal tidak valid: '{cand_str}'",
            }

        # Port validation
        if dst_port is None:
            return {
                "intent": intent_norm,
                "action": action,
                "target": cand_str,
                "address": cand_str,
                "dst_port": None,
                "name": None,
                "is_valid": False,
                "error": "Port eksternal (dst_port) wajib diisi untuk port forwarding",
            }
        try:
            p_ext = int(dst_port)
            if not (1 <= p_ext <= 65535):
                raise ValueError()
        except Exception:
            return {
                "intent": intent_norm,
                "action": action,
                "target": cand_str,
                "address": cand_str,
                "dst_port": dst_port,
                "name": None,
                "is_valid": False,
                "error": f"Port eksternal tidak valid: {dst_port} (harus antara 1-65535)",
            }

        # Anti-lockout: protect controller & Winbox ports
        if p_ext == 8728:
            return {
                "intent": intent_norm,
                "action": action,
                "target": cand_str,
                "address": cand_str,
                "dst_port": p_ext,
                "name": None,
                "is_valid": False,
                "error": "INV-NAT-03: Anti-lockout dilarang mem-forward port RouterOS Binary API (8728)!",
            }
        if p_ext == 8291:
            return {
                "intent": intent_norm,
                "action": action,
                "target": cand_str,
                "address": cand_str,
                "dst_port": p_ext,
                "name": None,
                "is_valid": False,
                "error": "INV-NAT-03: Anti-lockout dilarang mem-forward port Winbox (8291)!",
            }

        p_int = p_ext if to_port is None else to_port
        try:
            p_int = int(p_int)
            if not (1 <= p_int <= 65535):
                raise ValueError()
        except Exception:
            return {
                "intent": intent_norm,
                "action": action,
                "target": cand_str,
                "address": cand_str,
                "dst_port": p_ext,
                "to_port": to_port,
                "name": None,
                "is_valid": False,
                "error": f"Port internal tidak valid: {to_port} (harus antara 1-65535)",
            }

        proto = (protocol or "tcp").lower()
        if proto not in ("tcp", "udp"):
            return {
                "intent": intent_norm,
                "action": action,
                "target": cand_str,
                "address": cand_str,
                "dst_port": p_ext,
                "protocol": protocol,
                "name": None,
                "is_valid": False,
                "error": f"Protokol tidak didukung: '{protocol}' (harus tcp atau udp)",
            }

        return {
            "intent": intent_norm,
            "action": action,
            "target": cand_str,
            "address": cand_str,
            "dst_port": p_ext,
            "to_port": p_int,
            "protocol": proto,
            "name": f"portfwd_{p_ext}",
            "is_valid": True,
            "error": None,
        }

    if intent_norm == "remove_port_forward":
        p_ext = None
        if dst_port is not None and str(dst_port).lower() not in ("all", "semua", "seluruh"):
            try:
                p_ext = int(dst_port)
                if not (1 <= p_ext <= 65535):
                    raise ValueError()
            except Exception:
                return {
                    "intent": intent_norm,
                    "action": action,
                    "target": target,
                    "dst_port": dst_port,
                    "name": None,
                    "is_valid": False,
                    "error": f"Port eksternal tidak valid: {dst_port} (harus antara 1-65535)",
                }
        else:
            p_ext = "all" if str(dst_port).lower() in ("all", "semua", "seluruh") else None

        return {
            "intent": intent_norm,
            "action": action,
            "target": target,
            "dst_port": p_ext,
            "protocol": (protocol or "tcp").lower() if p_ext and p_ext != "all" else None,
            "name": f"rm_portfwd_{p_ext or 'all'}",
            "is_valid": True,
            "error": None,
        }

    # Diagnostics & Utility Domain (OTHER)
    if intent_norm == "ping_host":
        cand_host = target or address
        if not cand_host or not str(cand_host).strip():
            return {
                "intent": intent_norm,
                "action": action,
                "target": None,
                "name": None,
                "is_valid": False,
                "error": "Target IP atau hostname untuk ping wajib diisi",
            }

        host_str = str(cand_host).strip()
        # Clean domain or IP
        if not re.match(r"^[a-zA-Z0-9\.\-_]+$", host_str):
            return {
                "intent": intent_norm,
                "action": action,
                "target": host_str,
                "name": None,
                "is_valid": False,
                "error": f"Format target ping tidak valid: '{host_str}'",
            }

        # Bound count (INV-DIAG-01: max count=4)
        count_val = 4
        if dst_port is not None:
            try:
                count_val = min(max(int(dst_port), 1), 4)
            except Exception:
                count_val = 4

        return {
            "intent": intent_norm,
            "action": action,
            "target": host_str,
            "count": count_val,
            "name": f"ping_{host_str.replace('.', '_')}",
            "is_valid": True,
            "error": None,
        }

    if intent_norm == "flush_dns_cache":
        return {
            "intent": intent_norm,
            "action": action,
            "name": "flush_dns",
            "is_valid": True,
            "error": None,
        }

    if intent_norm == "get_system_health":
        return {
            "intent": intent_norm,
            "action": action,
            "name": "system_health",
            "is_valid": True,
            "error": None,
        }

    if intent_norm == "add_ip_address":
        cand_addr = address
        cand_iface = interface

        if cand_addr is None and target and _is_ip_like(str(target)):
            cand_addr = str(target).strip()

        if cand_iface is None:
            if interface is not None:
                cand_iface = interface
            elif target and not _is_ip_like(str(target)):
                cand_iface = str(target).strip()

        if not cand_iface or not str(cand_iface).strip():
            return {
                "intent": intent_norm,
                "action": action,
                "target": None,
                "address": cand_addr,
                "interface": None,
                "name": None,
                "is_valid": False,
                "error": "Interface wajib diisi",
            }

        norm_iface = _normalize_interface_str(cand_iface)
        if norm_iface not in VALID_INTERFACES:
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": cand_addr,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": f"Interface {norm_iface} tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)",
            }

        if not cand_addr or not str(cand_addr).strip():
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": None,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": "Address IP wajib diisi",
            }

        try:
            norm_addr = normalize_ip_address(str(cand_addr))
        except ValueError as e:
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": cand_addr,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": str(e),
            }

        addr_clean = norm_addr.split("/")[0].strip()
        raw_addr_clean = str(cand_addr).strip().split("/")[0].strip()
        if (
            addr_clean in ("192.168.88.1", ROUTER_HOST)
            or raw_addr_clean in ("192.168.88.1", ROUTER_HOST)
            or norm_addr in MANAGEMENT_IPS
            or str(cand_addr).strip() in MANAGEMENT_IPS
            or addr_clean in MANAGEMENT_IPS
        ):
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": norm_addr,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": f"Anti-lockout: Dilarang mengubah IP manajemen ({norm_addr})",
            }

        return {
            "intent": intent_norm,
            "action": action,
            "target": norm_iface,
            "address": norm_addr,
            "interface": norm_iface,
            "rate": None,
            "dst_port": None,
            "protocol": None,
            "name": f"ip_{norm_iface}",
            "is_valid": True,
            "error": None,
        }

    if intent_norm == "remove_ip_address":
        cand_addr = address
        cand_iface = interface

        if cand_addr is None and target and _is_ip_like(str(target)):
            cand_addr = str(target).strip()

        if cand_iface is None:
            if interface is not None:
                cand_iface = interface
            elif target and not _is_ip_like(str(target)):
                cand_iface = str(target).strip()

        if not cand_addr and not cand_iface:
            return {
                "intent": intent_norm,
                "action": action,
                "target": None,
                "address": None,
                "interface": None,
                "name": None,
                "is_valid": False,
                "error": "Harap tentukan address atau interface yang ingin dihapus",
            }

        norm_iface = None
        if cand_iface:
            norm_iface = _normalize_interface_str(cand_iface)
            if norm_iface not in VALID_INTERFACES:
                return {
                    "intent": intent_norm,
                    "action": action,
                    "target": norm_iface,
                    "address": cand_addr,
                    "interface": norm_iface,
                    "name": None,
                    "is_valid": False,
                    "error": f"Interface {norm_iface} tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)",
                }

            if norm_iface in MANAGEMENT_INTERFACES and not cand_addr:
                return {
                    "intent": intent_norm,
                    "action": action,
                    "target": norm_iface,
                    "address": None,
                    "interface": norm_iface,
                    "name": None,
                    "is_valid": False,
                    "error": f"Anti-lockout: Dilarang menghapus IP pada interface manajemen ({norm_iface})",
                }

        norm_addr = None
        if cand_addr:
            raw_clean = str(cand_addr).strip().split("/")[0].strip()
            if (
                raw_clean in ("192.168.88.1", ROUTER_HOST)
                or str(cand_addr).strip() in MANAGEMENT_IPS
                or raw_clean in MANAGEMENT_IPS
            ):
                return {
                    "intent": intent_norm,
                    "action": action,
                    "target": norm_iface or str(cand_addr).strip(),
                    "address": str(cand_addr).strip(),
                    "interface": norm_iface,
                    "name": None,
                    "is_valid": False,
                    "error": f"Anti-lockout: Dilarang menghapus IP manajemen ({cand_addr})",
                }

            try:
                norm_addr = normalize_ip_address(str(cand_addr))
            except ValueError as e:
                return {
                    "intent": intent_norm,
                    "action": action,
                    "target": norm_iface,
                    "address": cand_addr,
                    "interface": norm_iface,
                    "name": None,
                    "is_valid": False,
                    "error": str(e),
                }

            addr_clean = norm_addr.split("/")[0].strip()
            if (
                addr_clean in ("192.168.88.1", ROUTER_HOST)
                or norm_addr in MANAGEMENT_IPS
                or addr_clean in MANAGEMENT_IPS
            ):
                return {
                    "intent": intent_norm,
                    "action": action,
                    "target": norm_iface or norm_addr,
                    "address": norm_addr,
                    "interface": norm_iface,
                    "name": None,
                    "is_valid": False,
                    "error": f"Anti-lockout: Dilarang menghapus IP manajemen ({norm_addr})",
                }

        name = f"del_ip_{norm_iface}" if norm_iface else f"del_ip_{norm_addr.split('/')[0]}"
        return {
            "intent": intent_norm,
            "action": action,
            "target": norm_iface or norm_addr,
            "address": norm_addr,
            "interface": norm_iface,
            "rate": None,
            "dst_port": None,
            "protocol": None,
            "name": name,
            "is_valid": True,
            "error": None,
        }

    if intent_norm == "update_ip_address":
        cand_addr = address
        cand_iface = interface

        if cand_addr is None and target and _is_ip_like(str(target)):
            cand_addr = str(target).strip()

        if cand_iface is None:
            if interface is not None:
                cand_iface = interface
            elif target and not _is_ip_like(str(target)):
                cand_iface = str(target).strip()

        if not cand_iface or not str(cand_iface).strip():
            return {
                "intent": intent_norm,
                "action": action,
                "target": None,
                "address": cand_addr,
                "interface": None,
                "name": None,
                "is_valid": False,
                "error": "Interface wajib diisi",
            }

        norm_iface = _normalize_interface_str(cand_iface)
        if norm_iface not in VALID_INTERFACES:
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": cand_addr,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": f"Interface {norm_iface} tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)",
            }

        if norm_iface in MANAGEMENT_INTERFACES:
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": cand_addr,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": f"Anti-lockout: Dilarang mengubah IP pada interface manajemen ({norm_iface})",
            }

        if not cand_addr or not str(cand_addr).strip():
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": None,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": "Address IP wajib diisi",
            }

        try:
            norm_addr = normalize_ip_address(str(cand_addr))
        except ValueError as e:
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": cand_addr,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": str(e),
            }

        addr_clean = norm_addr.split("/")[0].strip()
        raw_addr_clean = str(cand_addr).strip().split("/")[0].strip()
        if (
            addr_clean in ("192.168.88.1", ROUTER_HOST)
            or raw_addr_clean in ("192.168.88.1", ROUTER_HOST)
            or norm_addr in MANAGEMENT_IPS
            or str(cand_addr).strip() in MANAGEMENT_IPS
            or addr_clean in MANAGEMENT_IPS
        ):
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_iface,
                "address": norm_addr,
                "interface": norm_iface,
                "name": None,
                "is_valid": False,
                "error": f"Anti-lockout: Dilarang mengubah IP manajemen ({norm_addr})",
            }

        return {
            "intent": intent_norm,
            "action": action,
            "target": norm_iface,
            "address": norm_addr,
            "interface": norm_iface,
            "rate": None,
            "dst_port": None,
            "protocol": None,
            "name": f"ip_{norm_iface}",
            "is_valid": True,
            "error": None,
        }

    # Validate dst_port
    norm_dst_port = None
    if dst_port is not None:
        try:
            port_num = int(dst_port)
            if not (1 <= port_num <= 65535):
                raise ValueError()
            norm_dst_port = port_num
        except (ValueError, TypeError):
            return {
                "intent": intent_norm,
                "action": action,
                "target": target,
                "rate": rate,
                "dst_port": dst_port,
                "protocol": protocol,
                "name": None,
                "is_valid": False,
                "error": f"Port tidak valid: {dst_port} (harus antara 1-65535)",
            }

    # Validate protocol
    norm_protocol = (protocol or "tcp").lower()
    if norm_dst_port is not None and norm_protocol not in ("tcp", "udp"):
        return {
            "intent": intent_norm,
            "action": action,
            "target": target,
            "rate": rate,
            "dst_port": norm_dst_port,
            "protocol": protocol,
            "name": None,
            "is_valid": False,
            "error": f"Protokol tidak didukung: '{protocol}' (harus tcp atau udp)",
        }

    # Validate target presence
    if not target and norm_dst_port is None:
        return {
            "intent": intent_norm,
            "action": action,
            "target": target,
            "rate": rate,
            "dst_port": norm_dst_port,
            "protocol": norm_protocol,
            "name": None,
            "is_valid": False,
            "error": "Target IP cannot be empty" if "limit" in intent_norm else "Target IP atau port wajib diisi",
        }

    norm_target = None
    if target:
        try:
            norm_target = normalize_target(target)
        except ValueError as e:
            return {
                "intent": intent_norm,
                "action": action,
                "target": target,
                "rate": rate,
                "dst_port": norm_dst_port,
                "protocol": norm_protocol,
                "name": None,
                "is_valid": False,
                "error": str(e),
            }

    safe, msg = check_safety(norm_target, intent_norm)
    if not safe:
        return {
            "intent": intent_norm,
            "action": action,
            "target": norm_target,
            "rate": rate,
            "dst_port": norm_dst_port,
            "protocol": norm_protocol,
            "name": None,
            "is_valid": False,
            "error": msg,
        }

    norm_rate = None
    if intent_norm == "limit_bandwidth":
        if not rate:
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_target,
                "rate": None,
                "dst_port": norm_dst_port,
                "protocol": norm_protocol,
                "name": None,
                "is_valid": False,
                "error": "Parameter rate wajib diisi untuk intent limit_bandwidth",
            }
        try:
            norm_rate = normalize_rate(rate)
        except ValueError as e:
            return {
                "intent": intent_norm,
                "action": action,
                "target": norm_target,
                "rate": rate,
                "dst_port": norm_dst_port,
                "protocol": norm_protocol,
                "name": None,
                "is_valid": False,
                "error": str(e),
            }

    # Generate name
    if "bandwidth" in action:
        target_name = norm_target.split("/")[0] if norm_target else "unknown"
        name = f"qos_{target_name}"
    else:
        if norm_target and norm_dst_port:
            target_name = norm_target.split("/")[0]
            name = f"fw_{target_name}_p{norm_dst_port}"
        elif norm_target:
            target_name = norm_target.split("/")[0]
            name = f"fw_{target_name}"
        elif norm_dst_port:
            name = f"fw_port_{norm_dst_port}"
        else:
            name = "fw_drop"

    return {
        "intent": intent_norm,
        "action": action,
        "target": norm_target,
        "rate": norm_rate,
        "dst_port": norm_dst_port,
        "protocol": norm_protocol if norm_dst_port is not None else None,
        "name": name,
        "is_valid": True,
        "error": None,
    }


def execute_policy(policy: dict, adapter: Optional[MikroTikAdapter] = None) -> dict:
    if not policy or not policy.get("is_valid", False):
        return {
            "status": "error",
            "intent": policy.get("intent") if policy else None,
            "error": policy.get("error", "Policy tidak valid") if policy else "Policy kosong",
            "result": None,
        }

    intent = policy["intent"]
    target = policy.get("target")
    name = policy.get("name")
    rate = policy.get("rate")
    dst_port = policy.get("dst_port")
    protocol = policy.get("protocol", "tcp") or "tcp"
    out_iface = policy.get("out_interface") or target or "ether1"
    comment = policy.get("comment", "IBN_NAT_MASQ")
    address = policy.get("address")
    interface = policy.get("interface")

    try:
        if intent == "limit_bandwidth":
            res = (
                adapter.apply_bandwidth_limit(name=name, target=target, max_limit=rate)
                if adapter
                else apply_bandwidth_limit(name=name, target=target, max_limit=rate)
            )
        elif intent == "remove_limit":
            res = (
                adapter.remove_bandwidth_limit(target=target)
                if adapter
                else remove_bandwidth_limit(target=target)
            )
        elif intent == "block_traffic":
            is_site = target and "." in str(target) and not _is_ip_like(str(target))
            site_val = str(target).lower() if is_site else None
            target_val = None if is_site else target
            port_val = 443 if is_site else dst_port
            res = (
                adapter.apply_firewall_block(target=target_val, dst_port=port_val, protocol=protocol, site=site_val)
                if adapter
                else apply_firewall_block(target=target_val, dst_port=port_val, protocol=protocol, site=site_val)
            )
        elif intent == "unblock_traffic":
            is_site = target and "." in str(target) and not _is_ip_like(str(target))
            site_val = str(target).lower() if is_site else None
            target_val = None if is_site else target
            res = (
                adapter.remove_firewall_block(target=target_val, dst_port=dst_port, site=site_val)
                if adapter
                else remove_firewall_block(target=target_val, dst_port=dst_port, site=site_val)
            )
        elif intent == "enable_interface":
            res = (
                adapter.enable_interface(name=target)
                if adapter
                else enable_interface(name=target)
            )
        elif intent == "disable_interface":
            res = (
                adapter.disable_interface(name=target)
                if adapter
                else disable_interface(name=target)
            )
        elif intent == "enable_nat":
            res = (
                adapter.enable_nat(out_interface=out_iface, comment=comment)
                if adapter
                else enable_nat(out_interface=out_iface, comment=comment)
            )
        elif intent == "disable_nat":
            res = (
                adapter.disable_nat(out_interface=out_iface, comment=comment)
                if adapter
                else disable_nat(out_interface=out_iface, comment=comment)
            )
        elif intent == "get_interface_ip":
            res = (
                adapter.get_interface_telemetry(interfaces=target)
                if adapter
                else get_interface_telemetry(interfaces=target)
            )
        elif intent == "get_bandwidth_status":
            res = (
                adapter.get_bandwidth_limits()
                if adapter
                else get_bandwidth_limits()
            )
        elif intent == "get_firewall_status":
            res = (
                adapter.get_firewall_blocks()
                if adapter
                else get_firewall_blocks()
            )
        elif intent == "get_nat_status":
            res = (
                adapter.get_nat_rules()
                if adapter
                else get_nat_rules()
            )
        elif intent == "add_ip_address":
            res = (
                adapter.add_ip_address(address=address, interface=interface)
                if adapter
                else add_ip_address(address=address, interface=interface)
            )
        elif intent == "remove_ip_address":
            res = (
                adapter.remove_ip_address(address=address, interface=interface)
                if adapter
                else remove_ip_address(address=address, interface=interface)
            )
        elif intent == "update_ip_address":
            res = (
                adapter.update_ip_address(interface=interface, new_address=address)
                if adapter
                else update_ip_address(interface=interface, new_address=address)
            )
        elif intent == "add_port_forward":
            to_addr = str(policy.get("address") or policy.get("target") or "")
            to_p = policy.get("to_port") or policy.get("dst_port")
            res = (
                adapter.add_port_forward(
                    dst_port=policy["dst_port"],
                    to_address=to_addr,
                    to_port=to_p,
                    protocol=policy.get("protocol", "tcp") or "tcp",
                )
                if adapter
                else add_port_forward(
                    dst_port=policy["dst_port"],
                    to_address=to_addr,
                    to_port=to_p,
                    protocol=policy.get("protocol", "tcp") or "tcp",
                )
            )
        elif intent == "remove_port_forward":
            res = (
                adapter.remove_port_forward(
                    dst_port=policy.get("dst_port"),
                    to_address=policy.get("target"),
                    protocol=policy.get("protocol"),
                )
                if adapter
                else remove_port_forward(
                    dst_port=policy.get("dst_port"),
                    to_address=policy.get("target"),
                    protocol=policy.get("protocol"),
                )
            )
        elif intent == "ping_host":
            target_host = str(policy.get("target") or "")
            res = (
                adapter.ping_host(
                    host=target_host,
                    count=policy.get("count", 4),
                )
                if adapter
                else ping_host(
                    host=target_host,
                    count=policy.get("count", 4),
                )
            )
        elif intent == "flush_dns_cache":
            res = adapter.flush_dns_cache() if adapter else flush_dns_cache()
        elif intent == "get_system_health":
            res = adapter.get_system_health() if adapter else get_system_health()
        else:
            return {
                "status": "error",
                "intent": intent,
                "error": f"Intent tidak didukung untuk eksekusi: {intent}",
                "result": None,
            }

        return {
            "status": "success",
            "intent": intent,
            "action": policy.get("action"),
            "target": target,
            "address": address,
            "interface": interface,
            "dst_port": dst_port,
            "protocol": protocol if dst_port else None,
            "result": res,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "intent": intent,
            "action": policy.get("action"),
            "target": target,
            "address": address,
            "interface": interface,
            "dst_port": dst_port,
            "protocol": protocol if dst_port else None,
            "error": str(e),
            "result": None,
        }

