import ipaddress
import re
from typing import Optional, Tuple, Union
from config import ROUTER_HOST
from mikrotik_adapter import (
    apply_bandwidth_limit,
    remove_bandwidth_limit,
    apply_firewall_block,
    remove_firewall_block,
    MikroTikAdapter,
)

PROTECTED_IPS = {"127.0.0.1", "192.168.88.1", ROUTER_HOST}
VALID_INTERFACES = {"ether1", "ether2", "ether3", "ether4", "wlan1", "bridge"}
SUPPORTED_INTENTS = {
    "limit_bandwidth": "apply_bandwidth_limit",
    "remove_limit": "remove_bandwidth_limit",
    "block_traffic": "apply_firewall_block",
    "unblock_traffic": "remove_firewall_block",
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


def normalize_target(target_str: str) -> str:
    if not isinstance(target_str, str) or not target_str.strip():
        raise ValueError("Target IP cannot be empty")
    s = target_str.strip().lower()
    if s in VALID_INTERFACES:
        return s
    if re.match(r"^(?:ether\d+|wlan\d+|bridge\d*|port\s*\d+)$", s):
        if s.startswith("port"):
            num = re.search(r"\d+", s).group(0)
            s = f"ether{num}"
        raise ValueError(f"Interface {s} tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)")
    if "/" in s:
        return str(ipaddress.ip_network(s, strict=False))
    return f"{ipaddress.ip_address(s)}/32"


def check_safety(target: Optional[str], action: str) -> Tuple[bool, str]:
    act = action.lower() if isinstance(action, str) else ""
    if "block" not in act and "drop" not in act:
        return True, ""
    if not target:
        return True, ""
    if target in VALID_INTERFACES:
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
    target: Optional[str] = None,
    rate: Optional[str] = None,
    dst_port: Optional[Union[str, int]] = None,
    protocol: Optional[str] = "tcp",
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
            "name": None,
            "is_valid": False,
            "error": f"Intent tidak dikenali: '{intent}'",
        }

    action = SUPPORTED_INTENTS[intent_norm]

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
            res = (
                adapter.apply_firewall_block(target=target, dst_port=dst_port, protocol=protocol)
                if adapter
                else apply_firewall_block(target=target, dst_port=dst_port, protocol=protocol)
            )
        elif intent == "unblock_traffic":
            res = (
                adapter.remove_firewall_block(target=target, dst_port=dst_port)
                if adapter
                else remove_firewall_block(target=target, dst_port=dst_port)
            )
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
            "dst_port": dst_port,
            "protocol": protocol if dst_port else None,
            "error": str(e),
            "result": None,
        }

