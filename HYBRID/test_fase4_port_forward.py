"""
Test Suite Fase 4 (Tahap 2): Parser Multi-Port & Disambiguation for Port Forwarding
Verifies extraction of external port, internal host, internal port, and disambiguation
between port forwarding, firewall drops, and NAT masquerade.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nlp_parser import parse_intent


def test_port_forward_parser():
    print("Running Port Forwarding Parser & Multi-Port Extraction Tests (Fase 4)...")

    test_cases = [
        # 1. Dual port extraction: ext_port != int_port
        ("forward port 8080 ke server 192.168.88.50 port 80", "add_port_forward", 8080, 80, "192.168.88.50"),
        ("buka port 8080 lempar ke ip 192.168.88.50 port 80", "add_port_forward", 8080, 80, "192.168.88.50"),
        ("petakan port publik 3389 ke server rdp 192.168.88.40 port 3389", "add_port_forward", 3389, 3389, "192.168.88.40"),

        # 2. Single port with smart default: int_port = ext_port
        ("arahkan koneksi port 8443 ke web server lab 192.168.88.20", "add_port_forward", 8443, 8443, "192.168.88.20"),
        ("tembusin port 2222 ke server 192.168.88.99", "add_port_forward", 2222, 2222, "192.168.88.99"),

        # 3. Remove port forward
        ("hapus aturan port forwarding 8080", "remove_port_forward", 8080, None, None),
        ("cabut konfigurasi dst-nat port 2222", "remove_port_forward", 2222, None, None),
        ("jangan lempar port 2222 lagi", "remove_port_forward", 2222, None, None),
        ("tutup akses port forwarding 8080", "remove_port_forward", 8080, None, None),
        ("hapus semua port forwarding", "remove_port_forward", "all", None, None),

        # 4. Anti-confusion checks: SHOW vs NAT vs Firewall
        ("tampilkan daftar aturan port forwarding aktif", "get_nat_status", None, None, None),
        ("apakah internet nat sedang aktif", "get_nat_status", None, None, None),
        ("aktifkan nat internet", "enable_nat", None, None, None),
        ("matikan nat internet", "disable_nat", None, None, None),
        ("blokir port 80 untuk 192.168.88.50", "block_traffic", 80, None, "192.168.88.50"),
        ("buka blokir port 80 untuk 192.168.88.50", "unblock_traffic", 80, None, "192.168.88.50"),
    ]

    passed = 0
    for query, exp_intent, exp_ext, exp_int, exp_target in test_cases:
        res = parse_intent(query)
        act_intent = res["intent"]
        act_ext = res["entities"].get("dst_port")
        act_int = res["entities"].get("to_port")
        act_tgt = res["entities"].get("target")

        assert act_intent == exp_intent, f"FAIL '{query}': expected intent '{exp_intent}', got '{act_intent}'"
        if exp_ext is not None:
            assert act_ext == exp_ext, f"FAIL '{query}': expected ext_port {exp_ext}, got {act_ext}"
        if exp_int is not None:
            assert act_int == exp_int, f"FAIL '{query}': expected int_port {exp_int}, got {act_int}"
        if exp_target is not None:
            assert act_tgt == exp_target, f"FAIL '{query}': expected target {exp_target}, got {act_tgt}"

        print(f" [PASS] '{query}' -> intent={act_intent}, ext_port={act_ext}, int_port={act_int}, target={act_tgt}")
        passed += 1

    print(f"\nALL {passed}/{len(test_cases)} PARSER & MULTI-PORT TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    test_port_forward_parser()
