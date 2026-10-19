"""
Test Suite Fase 2 (Tahap 3): Policy Engine & Safety Guard for Domain OTHER
Validates:
1. ping_host validation (target presence, domain/IP format, INV-DIAG-01 bound count)
2. flush_dns_cache policy generation & execution
3. get_system_health policy generation & execution
4. Error handling for empty or malformed ping targets
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent))

from policy_engine import build_network_policy, execute_policy


def test_diagnostics_fase2():
    print("Menjalankan Pengujian Unit Policy Engine Domain OTHER (Fase 2)...")

    # 1. ping_host validation
    print("\n[1] Validasi Policy ping_host...")
    p1 = build_network_policy("ping_host", target="8.8.8.8", dst_port=4)
    assert p1["is_valid"] is True
    assert p1["action"] == "ping_host"
    assert p1["target"] == "8.8.8.8"
    assert p1["count"] == 4
    print(" [PASS] Ping IP valid 8.8.8.8 -> is_valid=True, count=4")

    p2 = build_network_policy("ping_host", target="google.com", dst_port=100)
    assert p2["is_valid"] is True
    assert p2["target"] == "google.com"
    assert p2["count"] == 4, f"INV-DIAG-01: count 100 harus dibatasi ke 4, didapat: {p2['count']}"
    print(" [PASS] Ping Domain google.com + INV-DIAG-01 -> count 100 dibatasi ke 4")

    # Empty target test
    p3 = build_network_policy("ping_host", target="")
    assert p3["is_valid"] is False
    assert "wajib diisi" in p3["error"]
    print(f" [PASS] Ping target kosong ditolak: {p3['error']}")

    # Malformed target test
    p4 = build_network_policy("ping_host", target="8.8.8.8; rm -rf /")
    assert p4["is_valid"] is False
    assert "tidak valid" in p4["error"]
    print(f" [PASS] Ping target jahat/injeksi ditolak: {p4['error']}")

    # 2. flush_dns_cache validation
    print("\n[2] Validasi Policy flush_dns_cache...")
    p_dns = build_network_policy("flush_dns_cache")
    assert p_dns["is_valid"] is True
    assert p_dns["action"] == "flush_dns_cache"
    assert p_dns["name"] == "flush_dns"
    print(" [PASS] flush_dns_cache -> is_valid=True, action=flush_dns_cache")

    # 3. get_system_health validation
    print("\n[3] Validasi Policy get_system_health...")
    p_health = build_network_policy("get_system_health")
    assert p_health["is_valid"] is True
    assert p_health["action"] == "get_system_health"
    assert p_health["name"] == "system_health"
    print(" [PASS] get_system_health -> is_valid=True, action=get_system_health")

    # 4. Mock execution via execute_network_policy
    print("\n[4] Pengujian Eksekusi Policy via Mock Adapter...")
    mock_adapter = MagicMock()
    mock_adapter.ping_host.return_value = {
        "action": "ping_completed",
        "target": "8.8.8.8",
        "sent": 4,
        "received": 4,
        "packet_loss_pct": 0,
        "avg_rtt_ms": 18.5,
    }
    mock_adapter.flush_dns_cache.return_value = {
        "action": "dns_cache_flushed",
        "status": "success",
    }
    mock_adapter.get_system_health.return_value = {
        "action": "system_health_inspected",
        "cpu_load_pct": 10,
        "free_memory_mb": 15.2,
    }

    res_exec_ping = execute_policy(p1, adapter=mock_adapter)
    assert res_exec_ping["status"] == "success"
    assert res_exec_ping["result"]["packet_loss_pct"] == 0
    print(" [PASS] Eksekusi ping_host via Policy Engine -> status=success")

    res_exec_dns = execute_policy(p_dns, adapter=mock_adapter)
    assert res_exec_dns["status"] == "success"
    print(" [PASS] Eksekusi flush_dns_cache via Policy Engine -> status=success")

    res_exec_health = execute_policy(p_health, adapter=mock_adapter)
    assert res_exec_health["status"] == "success"
    print(" [PASS] Eksekusi get_system_health via Policy Engine -> status=success")

    print("\nSEMUA PENGUJIAN POLICY ENGINE & SAFETY GUARDS DOMAIN OTHER LOLOS 100%!")


if __name__ == "__main__":
    test_diagnostics_fase2()
