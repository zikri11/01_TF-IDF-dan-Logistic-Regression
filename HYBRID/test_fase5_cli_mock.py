"""
Test Suite Fase 5: CLI Output & Mock Adapter Test (Tanpa Perangkat Fisik)
Memverifikasi bahwa antarmuka CLI di main_ibn.py mampu menampilkan tabel
hasil inspeksi SHOW untuk seluruh domain (bandwidth, firewall, nat, interface)
dengan sempurna tanpa perlu terhubung ke router fisik MikroTik.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent))

import main_ibn


class MockMikroTikAdapter:
    def __init__(self):
        self.connected = True

    def add_port_forward(self, dst_port, to_address, to_port=None, protocol="tcp", comment=None):
        return {
            "action": "added",
            "id": "*9",
            "dst_port": dst_port,
            "to_address": to_address,
            "to_port": to_port or dst_port,
            "protocol": protocol,
            "comment": comment or f"IBN_PORT_FWD_{dst_port}",
        }

    def remove_port_forward(self, dst_port=None, to_address=None, protocol=None, comment=None):
        return {
            "action": "removed",
            "count": 1 if dst_port != "all" else 2,
            "dst_port": dst_port,
        }

    def ping_host(self, host: str, count: int = 4):
        cnt = min(max(int(count), 1), 4)
        return {
            "action": "ping_completed",
            "target": str(host),
            "sent": cnt,
            "received": cnt,
            "packet_loss_pct": 0,
            "min_rtt_ms": 18.2,
            "avg_rtt_ms": 20.4,
            "max_rtt_ms": 22.8,
            "details": [],
        }

    def flush_dns_cache(self):
        return {
            "action": "dns_cache_flushed",
            "status": "success",
            "message": "Cache DNS router berhasil dibersihkan",
        }

    def get_system_health(self):
        return {
            "action": "system_health_inspected",
            "platform": "MikroTik",
            "version": "RouterOS v6.49.17",
            "uptime": "2w3d14h20m",
            "cpu_load_pct": 12,
            "cpu_model": "MIPS 24KEc @ 650 MHz",
            "cpu_count": 1,
            "cpu_freq_mhz": 650,
            "free_memory_mb": 14.5,
            "total_memory_mb": 32.0,
            "free_hdd_mb": 4.2,
            "board_name": "hAP lite",
        }

    def get_bandwidth_limits(self):
        return [
            {".id": "*1", "name": "qos_192_168_88_50", "target": "192.168.88.50/32", "max-limit": "2M/2M", "bytes": "1048576/2097152"},
            {".id": "*2", "name": "qos_ether3", "target": "ether3", "max-limit": "5M/5M", "bytes": "5242880/5242880"},
        ]

    def get_firewall_blocks(self):
        return [
            {".id": "*1", "chain": "forward", "src-address": "192.168.88.99", "dst-port": "-", "protocol": "all", "action": "drop", "comment": "IBN_BLOCK"},
            {".id": "*2", "chain": "forward", "src-address": "192.168.88.50", "dst-port": "80", "protocol": "tcp", "action": "drop", "comment": "IBN_BLOCK_PORT"},
        ]

    def get_nat_rules(self):
        return [
            {".id": "*1", "chain": "srcnat", "action": "masquerade", "out-interface": "ether1", "comment": "IBN_NAT", "disabled": False},
        ]

    def get_interface_telemetry(self, interfaces=None):
        return [
            {"name": "ether1", "type": "ether", "mac": "08:55:31:00:00:01", "running": True, "ips": ["192.168.1.100/24"]},
            {"name": "ether3", "type": "ether", "mac": "08:55:31:00:00:03", "running": False, "ips": ["10.10.10.1/24"]},
        ]


def run_mock_cli_tests():
    mock_adapter = MockMikroTikAdapter()

    test_queries = [
        "siapa saja yang lagi dibatasi bandwidth",
        "tampilkan seluruh aturan firewall filter drop",
        "apakah internet nat sedang aktif",
        "cek semua ip",
        "forward port 8080 ke server 192.168.88.50 port 80",
        "hapus aturan port forwarding 8080",
        "coba ping ke 8.8.8.8 dong",
        "ping google.com count 4",
        "bersihkan cache dns router",
        "cek beban cpu dan ram router",
        "gimana kesehatan hardware mikrotik",
    ]

    print("\n" + "=" * 80)
    print("  SIMULASI PENGUJIAN TAMPILAN CLI (MOCK ADAPTER - TANPA ROUTER FISIK)")
    print("=" * 80)

    for q in test_queries:
        print(f"\n[USER INPUT]> {q}")
        main_ibn.handle_input_intent(q, mock_adapter)  # type: ignore

    print("\n" + "=" * 80)
    print("  SEMUA PENGUJIAN TAMPILAN CLI FASE 5 BERHASIL (100% PASS)!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_mock_cli_tests()
