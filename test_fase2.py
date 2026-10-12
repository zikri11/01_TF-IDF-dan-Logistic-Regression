from policy_engine import (
    normalize_rate,
    normalize_target,
    check_safety,
    build_network_policy,
    execute_policy,
)
from mikrotik_adapter import MikroTikAdapter

DUMMY_IP = "192.168.88.250"


def test_rate_normalization():
    print("[1/5] Testing rate normalization...")
    cases = [
        ("2 Mbps", "2M/2M"),
        ("2 mega", "2M/2M"),
        ("2mbps", "2M/2M"),
        ("2M", "2M/2M"),
        ("512 kbps", "512k/512k"),
        ("512k", "512k/512k"),
        ("1.5M", "1500k/1500k"),
        ("1.5 mega", "1500k/1500k"),
        ("2M/2M", "2M/2M"),
        ("512k/2M", "512k/2M"),
    ]
    for raw, expected in cases:
        out = normalize_rate(raw)
        assert out == expected, f"Failed: '{raw}' -> got '{out}', expected '{expected}'"

    invalid_cases = ["", "invalid", "-2M", "0k", "100", "2.2.2M"]
    for inv in invalid_cases:
        try:
            normalize_rate(inv)
            assert False, f"Expected ValueError for '{inv}'"
        except ValueError:
            pass
    print("      OK: Semua variasi rate valid dan invalid teruji.")


def test_target_normalization():
    print("[2/5] Testing target normalization...")
    cases = [
        ("192.168.88.50", "192.168.88.50/32"),
        ("192.168.88.0/24", "192.168.88.0/24"),
        ("10.0.0.1", "10.0.0.1/32"),
        ("  192.168.88.250  ", "192.168.88.250/32"),
    ]
    for raw, expected in cases:
        out = normalize_target(raw)
        assert out == expected, f"Failed: '{raw}' -> got '{out}', expected '{expected}'"

    invalid_cases = ["", "invalid_ip", "999.999.999.999", "192.168.88.50/33"]
    for inv in invalid_cases:
        try:
            normalize_target(inv)
            assert False, f"Expected ValueError for '{inv}'"
        except ValueError:
            pass
    print("      OK: Normalisasi IP dan subnet valid.")


def test_anti_lockout_safety():
    print("[3/5] Testing anti-lockout safety...")
    # Blokir router IP / 127.0.0.1 harus gagal
    assert not check_safety("192.168.88.1", "block_traffic")[0]
    assert not check_safety("192.168.88.1/32", "drop")[0]
    assert not check_safety("127.0.0.1", "block")[0]
    assert not check_safety("192.168.88.0/24", "block_traffic")[0]

    # Blokir client IP biasa harus lolos
    assert check_safety("192.168.88.250", "block_traffic")[0]
    # Rate limit pada router IP bukan aksi drop/blokir
    assert check_safety("192.168.88.1", "limit_bandwidth")[0]

    # Melalui build_network_policy
    bad_pol = build_network_policy("block_traffic", "192.168.88.1")
    assert not bad_pol["is_valid"]
    assert "Anti-lockout" in bad_pol["error"]
    print("      OK: Proteksi anti-lockout router aktif dan valid.")


def test_policy_building():
    print("[4/5] Testing policy building...")
    p1 = build_network_policy("limit_bandwidth", DUMMY_IP, "2 Mbps")
    assert p1["is_valid"]
    assert p1["target"] == f"{DUMMY_IP}/32"
    assert p1["rate"] == "2M/2M"
    assert p1["name"] == f"qos_{DUMMY_IP}"

    p2 = build_network_policy("remove_limit", DUMMY_IP)
    assert p2["is_valid"]

    p3 = build_network_policy("block_traffic", DUMMY_IP)
    assert p3["is_valid"]

    p4 = build_network_policy("unblock_traffic", DUMMY_IP)
    assert p4["is_valid"]

    p_bad_intent = build_network_policy("destroy_router", DUMMY_IP)
    assert not p_bad_intent["is_valid"]

    p_no_rate = build_network_policy("limit_bandwidth", DUMMY_IP)
    assert not p_no_rate["is_valid"]
    print("      OK: Pembentukan Intermediate Policy terstruktur sesuai spesifikasi.")


def test_live_router_execution():
    print("[5/5] Testing live router execution & clean rollback...")
    with MikroTikAdapter() as adapter:
        # Pre-cleanup
        adapter.remove_bandwidth_limit(DUMMY_IP)
        adapter.remove_firewall_block(DUMMY_IP)

        # 1. Eksekusi QoS Limit Bandwidth
        pol_limit = build_network_policy("limit_bandwidth", DUMMY_IP, "2 Mbps")
        res_limit = execute_policy(pol_limit, adapter=adapter)
        assert res_limit["status"] == "success", f"Eksekusi QoS gagal: {res_limit}"
        q_list = adapter.get_bandwidth_limits()
        assert any(r.get("target", "").split("/")[0] == DUMMY_IP for r in q_list)
        print("      OK: Eksekusi QoS limit_bandwidth sukses di router.")

        # 2. Eksekusi Firewall Block
        pol_block = build_network_policy("block_traffic", DUMMY_IP)
        res_block = execute_policy(pol_block, adapter=adapter)
        assert res_block["status"] == "success", f"Eksekusi firewall block gagal: {res_block}"
        fw_list = adapter.get_firewall_blocks()
        assert any(r.get("src-address", "").split("/")[0] == DUMMY_IP for r in fw_list)
        print("      OK: Eksekusi firewall block_traffic sukses di router.")

        # 3. Eksekusi Policy Invalid (Anti-lockout pada router)
        pol_lockout = build_network_policy("block_traffic", "192.168.88.1")
        res_lockout = execute_policy(pol_lockout, adapter=adapter)
        assert res_lockout["status"] == "error"
        print("      OK: Eksekusi policy anti-lockout ditolak sistem.")

        # 4. Clean Rollback - Remove Limit
        pol_unlimit = build_network_policy("remove_limit", DUMMY_IP)
        res_unlimit = execute_policy(pol_unlimit, adapter=adapter)
        assert res_unlimit["status"] == "success"

        # 5. Clean Rollback - Unblock Traffic
        pol_unblock = build_network_policy("unblock_traffic", DUMMY_IP)
        res_unblock = execute_policy(pol_unblock, adapter=adapter)
        assert res_unblock["status"] == "success"

        # Verifikasi bersih total
        rem_q = [r for r in adapter.get_bandwidth_limits() if r.get("target", "").split("/")[0] == DUMMY_IP]
        rem_fw = [r for r in adapter.get_firewall_blocks() if r.get("src-address", "").split("/")[0] == DUMMY_IP]
        assert len(rem_q) == 0, "Sisa queue masih ada setelah rollback"
        assert len(rem_fw) == 0, "Sisa firewall drop masih ada setelah rollback"
        print("      OK: Rollback tuntas, router kembali bersih.")


def run_all_tests():
    test_rate_normalization()
    test_target_normalization()
    test_anti_lockout_safety()
    test_policy_building()
    test_live_router_execution()
    print("\nSEMUA PENGUJIAN FASE 2 SUKSES 100%!")


if __name__ == "__main__":
    run_all_tests()
