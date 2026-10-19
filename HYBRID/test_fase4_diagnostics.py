"""
Test Suite Fase 4 (Tahap 3): Parser & Disambiguation Cues for Domain OTHER
Validates parsing and extraction for:
1. ping_host (IP target, Domain target, Count parameter)
2. flush_dns_cache (DNS resolver cache clearing keywords)
3. get_system_health (Resource CPU/RAM/Uptime keywords)
4. Anti-confusion checks across all domains
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nlp_parser import parse_intent


def test_diagnostics_parser():
    print("Menjalankan Pengujian Unit Parser & Disambiguasi Domain OTHER (Fase 4)...")

    test_cases = [
        # 1. Ping Host (IP target, Domain target, Count)
        ("ping 8.8.8.8", "ping_host", "8.8.8.8", 4),
        ("ping google.com count 4", "ping_host", "google.com", 4),
        ("coba ping ke 192.168.88.50 dong", "ping_host", "192.168.88.50", 4),
        ("lakukan ping sebanyak 4 kali ke 1.1.1.1", "ping_host", "1.1.1.1", 4),
        ("tes konektivitas ping ke cloudflare.com", "ping_host", "cloudflare.com", 4),

        # 2. Flush DNS Cache
        ("flush dns cache", "flush_dns_cache", None, None),
        ("bersihkan cache dns router", "flush_dns_cache", None, None),
        ("reset cache dns di router", "flush_dns_cache", None, None),
        ("kosongkan tabel cache dns", "flush_dns_cache", None, None),
        ("tolong flush dns mikrotik sekarang", "flush_dns_cache", None, None),

        # 3. System Health Monitoring
        ("system resource print", "get_system_health", None, None),
        ("cek beban cpu router", "get_system_health", None, None),
        ("tampilkan sisa ram router", "get_system_health", None, None),
        ("lihat status uptime mikrotik", "get_system_health", None, None),
        ("gimana kesehatan hardware mikrotik", "get_system_health", None, None),

        # 4. Anti-Confusion across other domains
        ("tampilkan seluruh aturan nat yang aktif", "get_nat_status", None, None),
        ("forward port 8080 ke server 192.168.88.50 port 80", "add_port_forward", "192.168.88.50", 8080),
        ("blokir port 80 untuk 192.168.88.50", "block_traffic", "192.168.88.50", 80),
        ("siapa saja yang lagi dibatasi bandwidth", "get_bandwidth_status", None, None),
    ]

    passed = 0
    for query, exp_intent, exp_target, exp_param in test_cases:
        res = parse_intent(query)
        act_intent = res["intent"]
        act_tgt = res["entities"].get("target")
        act_p = res["entities"].get("dst_port")

        assert act_intent == exp_intent, f"GAGAL '{query}': diharapkan intent '{exp_intent}', didapat '{act_intent}'"
        if exp_target is not None:
            assert act_tgt == exp_target, f"GAGAL '{query}': diharapkan target '{exp_target}', didapat '{act_tgt}'"
        if exp_param is not None and exp_intent == "ping_host":
            assert act_p == exp_param, f"GAGAL '{query}': diharapkan count/port {exp_param}, didapat {act_p}"

        print(f" [PASS] '{query}' -> intent={act_intent}, target={act_tgt}, count/port={act_p}")
        passed += 1

    print(f"\nSEMUA {passed}/{len(test_cases)} PENGUJIAN PARSER DOMAIN OTHER LOLOS 100%!")


if __name__ == "__main__":
    test_diagnostics_parser()
