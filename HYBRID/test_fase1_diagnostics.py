"""
Test Suite Fase 1 (Tahap 3): Diagnostics & Maintenance Domain (OTHER)
Tests ping_host, flush_dns_cache, and get_system_health methods in MikroTikAdapter.
Uses mock API objects to verify functionality without requiring physical router connection.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent))

from mikrotik_adapter import MikroTikAdapter


def test_diagnostics_fase1():
    print("Menjalankan Pengujian Unit Driver API Domain OTHER (Fase 1)...")

    adapter = MikroTikAdapter()
    adapter.connected = True
    adapter.api = MagicMock()

    # 1. Test ping_host
    print("\n[1] Pengujian ping_host (ICMP RTT & Packet Loss)...")
    mock_ping_res = [
        {"host": "8.8.8.8", "status": "alive", "time": "18ms", "size": 56},
        {"host": "8.8.8.8", "status": "alive", "time": "22ms", "size": 56},
        {"host": "8.8.8.8", "status": "alive", "time": "19ms", "size": 56},
        {"host": "8.8.8.8", "status": "alive", "time": "21ms", "size": 56},
    ]
    adapter.api.path.return_value = MagicMock(return_value=mock_ping_res)

    res_ping = adapter.ping_host("8.8.8.8", count=4)
    assert res_ping["action"] == "ping_completed"
    assert res_ping["target"] == "8.8.8.8"
    assert res_ping["sent"] == 4
    assert res_ping["received"] == 4
    assert res_ping["packet_loss_pct"] == 0
    assert res_ping["min_rtt_ms"] == 18.0
    assert res_ping["avg_rtt_ms"] == 20.0
    assert res_ping["max_rtt_ms"] == 22.0
    print(f" [PASS] Ping 8.8.8.8: sent={res_ping['sent']}, loss={res_ping['packet_loss_pct']}%, avg_rtt={res_ping['avg_rtt_ms']} ms")

    # 1b. Test ping bound count (INV-DIAG-01: count=100 harus dibatasi ke 4)
    res_ping_bound = adapter.ping_host("8.8.8.8", count=100)
    assert res_ping_bound["sent"] == 4, f"Harus dibatasi ke 4, didapat: {res_ping_bound['sent']}"
    print(f" [PASS] INV-DIAG-01 Protection: count=100 otomatis dibatasi menjadi {res_ping_bound['sent']}")

    # 2. Test flush_dns_cache
    print("\n[2] Pengujian flush_dns_cache (Reset Memori Cache DNS)...")
    mock_dns_cache = MagicMock()
    adapter.api.path.return_value = mock_dns_cache
    res_dns = adapter.flush_dns_cache()
    assert res_dns["action"] == "dns_cache_flushed"
    assert res_dns["status"] == "success"
    print(f" [PASS] Flush DNS: action={res_dns['action']}, msg={res_dns['message']}")

    # 3. Test get_system_health
    print("\n[3] Pengujian get_system_health (Resource CPU/RAM/Uptime)...")
    mock_resource = [{
        "uptime": "2w3d14h20m",
        "version": "6.49.17 (stable)",
        "cpu": "MIPS 24KEc",
        "cpu-count": 1,
        "cpu-frequency": 650,
        "cpu-load": 12,
        "free-memory": 14 * 1024 * 1024,
        "total-memory": 32 * 1024 * 1024,
        "free-hdd-space": 4 * 1024 * 1024,
        "board-name": "hAP lite",
        "platform": "MikroTik",
    }]
    adapter.api.path.return_value = mock_resource
    res_health = adapter.get_system_health()
    assert res_health["action"] == "system_health_inspected"
    assert res_health["board_name"] == "hAP lite"
    assert res_health["cpu_load_pct"] == 12
    assert res_health["free_memory_mb"] == 14.0
    assert res_health["total_memory_mb"] == 32.0
    assert res_health["uptime"] == "2w3d14h20m"
    print(f" [PASS] System Health: board={res_health['board_name']}, cpu_load={res_health['cpu_load_pct']}%, free_ram={res_health['free_memory_mb']} MB / {res_health['total_memory_mb']} MB, uptime={res_health['uptime']}")

    print("\nSEMUA 3 METODE DOMAIN OTHER BERHASIL LOLOS UJI 100%!")


if __name__ == "__main__":
    test_diagnostics_fase1()
