"""
Test Suite Fase 3: Quality Audit & Disambiguation / Anti-Overlap Guard
Verifies that SHOW intents (bandwidth, firewall, nat, interface) do NOT collide
with SET (limit, block, enable, add) or DELETE (remove, unblock, disable) commands.
"""

import sys
from pathlib import Path

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from nlp_parser import parse_intent
from policy_engine import execute_policy


def test_anti_overlap_show():
    test_cases = [
        # 1. SHOW Bandwidth vs SET/DELETE Bandwidth
        ("tampilkan seluruh antrean simple queue", "get_bandwidth_status", True),
        ("siapa saja yang lagi dibatasi bandwidth", "get_bandwidth_status", True),
        ("cek limit bandwidth host 192.168.88.50", "get_bandwidth_status", True),
        ("port 3 internetnya dicekik gak sih", "get_bandwidth_status", True),
        ("batasi bandwidth 192.168.88.50 jadi 2 Mbps", "limit_bandwidth", True),
        ("hapus limit bandwidth 192.168.88.50", "remove_limit", True),
        ("jangan batasi lagi 192.168.88.50", "remove_limit", True),

        # 2. SHOW Firewall vs SET/DELETE Firewall
        ("tampilkan seluruh aturan firewall filter drop", "get_firewall_status", True),
        ("siapa saja yang lagi diblokir internetnya", "get_firewall_status", True),
        ("cek status firewall untuk ip 192.168.88.99", "get_firewall_status", True),
        ("apakah port 80 sedang ditutup firewall", "get_firewall_status", True),
        ("blokir akses internet untuk 192.168.88.99", "block_traffic", True),
        ("buka blokir untuk 192.168.88.99", "unblock_traffic", True),
        ("izinkan kembali port 80", "unblock_traffic", True),

        # 3. SHOW NAT vs SET/DELETE NAT
        ("tampilkan seluruh aturan nat yang aktif", "get_nat_status", True),
        ("apakah internet nat sedang aktif", "get_nat_status", True),
        ("cek konfigurasi nat router", "get_nat_status", True),
        ("tampilkan daftar aturan port forwarding aktif", "get_nat_status", True),
        ("aktifkan nat internet", "enable_nat", True),
        ("matikan nat internet", "disable_nat", True),

        # 4. SHOW Interface & IP vs SET/DELETE IP
        ("cek semua ip", "get_interface_ip", True),
        ("cek ip port 1", "get_interface_ip", True),
        ("cek jalur 2", "get_interface_ip", True),
        ("tampilkan semua interface router", "get_interface_ip", True),
        ("tambahkan ip 10.10.10.1/24 di port 3", "add_ip_address", True),
        ("ganti ip port 3 jadi 10.10.99.1/24", "update_ip_address", True),
        ("hapus ip di port 3", "remove_ip_address", True),

        # 5. Ambiguity Guard
        ("hapus port 1", "unknown", False),
    ]

    print("Running Anti-Overlap Audit Test Suite (Fase 3)...")
    passed = 0
    for query, expected_intent, expected_valid in test_cases:
        res = parse_intent(query)
        actual_intent = res["intent"]
        is_valid = res["policy"]["is_valid"]
        
        assert actual_intent == expected_intent, (
            f"FAIL on '{query}': expected intent '{expected_intent}', got '{actual_intent}'"
        )
        assert is_valid == expected_valid, (
            f"FAIL on '{query}': expected valid={expected_valid}, got valid={is_valid} ({res['policy'].get('error')})"
        )
        print(f" [PASS] '{query}' -> {actual_intent} (valid={is_valid})")
        passed += 1

    print(f"\nALL {passed}/{len(test_cases)} TEST CASES PASSED PERFECTLY!")


if __name__ == "__main__":
    test_anti_overlap_show()
