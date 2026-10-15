from mikrotik_adapter import (
    MikroTikAdapter,
    MANAGEMENT_INTERFACES,
    MANAGEMENT_IPS,
    remove_ip_address,
)
from nlp_parser import parse_intent
from policy_engine import execute_policy


def test_parsing():
    print("[1/3] Menguji parsing intent 'update_ip_address' & ekstraksi entitas...")
    samples = [
        ("ganti ip port 3 jadi 10.10.10.1/24", "ether3", "10.10.10.1/24"),
        ("ubah ip lan 4 ke 172.16.20.1", "ether4", "172.16.20.1/24"),
        ("ganti ip lan 1 menjadi 192.168.30.1/24", "ether1", "192.168.30.1/24"),
        ("tukar ip jalur 3 dengan 10.20.30.1", "ether3", "10.20.30.1/24"),
        ("update ip address port 4 ke 192.168.40.1", "ether4", "192.168.40.1/24"),
        ("replace ip port 1 dengan 172.20.0.1/24", "ether1", "172.20.0.1/24"),
    ]
    for prompt, exp_tgt, exp_addr in samples:
        res = parse_intent(prompt)
        assert res["intent"] == "update_ip_address", f"Intent mismatch for '{prompt}': {res['intent']}"
        assert res["confidence"] >= 0.50, f"Confidence too low: {res['confidence']}"
        assert res["entities"]["target"] == exp_tgt, f"Target mismatch: {res['entities']['target']}"
        assert res["policy"]["is_valid"] is True, f"Policy invalid for '{prompt}': {res['policy']['error']}"
        assert res["policy"]["target"] == exp_tgt, f"Policy target mismatch: {res['policy']['target']}"
        assert res["policy"]["address"] == exp_addr, f"Policy addr mismatch: {res['policy']['address']}"
    print("      OK: Parsing dan normalisasi entitas update_ip_address valid.")


def test_anti_lockout():
    print("[2/3] Menguji proteksi Anti-Lockout...")
    res1 = parse_intent("ganti ip port 2 jadi 10.10.10.1")
    assert res1["intent"] == "update_ip_address"
    assert res1["policy"]["is_valid"] is False
    assert "Anti-lockout" in res1["policy"]["error"]

    res2 = parse_intent("ganti ip port 3 jadi 192.168.88.1")
    assert res2["intent"] == "update_ip_address"
    assert res2["policy"]["is_valid"] is False
    assert "Anti-lockout" in res2["policy"]["error"]

    with MikroTikAdapter() as adapter:
        for mgmt_iface in MANAGEMENT_INTERFACES:
            try:
                adapter.update_ip_address(mgmt_iface, "10.10.10.1/24")
                assert False, f"Anti-lockout gagal mencegah update pada {mgmt_iface}"
            except ValueError as e:
                assert "Anti-lockout" in str(e)

        for mgmt_ip in ("192.168.88.1", "192.168.88.1/24"):
            try:
                adapter.update_ip_address("ether3", mgmt_ip)
                assert False, f"Anti-lockout gagal mencegah update dengan IP manajemen {mgmt_ip}"
            except ValueError as e:
                assert "Anti-lockout" in str(e)

    print("      OK: Proteksi Anti-Lockout port manajemen dan IP router 100% aktif.")


def test_live_router_execution():
    print("[3/3] Menguji eksekusi live router MikroTik & rollback...")
    initial_ip = "192.168.99.1/24"
    new_ip = "10.10.99.1/24"
    target_iface = "ether3"

    with MikroTikAdapter() as adapter:
        adapter.remove_ip_address(initial_ip, target_iface)
        adapter.remove_ip_address(new_ip, target_iface)

        adapter.add_ip_address(initial_ip, target_iface)
        curr = adapter.get_ip_addresses(target_iface)
        assert any(r.get("address") == initial_ip for r in curr), "IP awal gagal dipasang"

        cmd = f"ganti ip port 3 jadi {new_ip}"
        parsed = parse_intent(cmd)
        assert parsed["policy"]["is_valid"] is True

        exec_res = execute_policy(parsed["policy"], adapter)
        assert exec_res["status"] == "success", f"Eksekusi gagal: {exec_res['error']}"
        assert exec_res["result"]["action"] == "updated"
        assert exec_res["result"]["old_address"] == initial_ip
        assert exec_res["result"]["new_address"] == new_ip

        curr_after = adapter.get_ip_addresses(target_iface)
        addrs_after = [r.get("address") for r in curr_after]
        assert initial_ip not in addrs_after, f"IP lama {initial_ip} masih ada di router"
        assert new_ip in addrs_after, f"IP baru {new_ip} tidak ditemukan di router"

        noop_res = execute_policy(parsed["policy"], adapter)
        assert noop_res["status"] == "success"
        assert noop_res["result"]["action"] == "noop"

        del_res = adapter.remove_ip_address(new_ip, target_iface)
        assert del_res["action"] == "removed"
        final_ips = adapter.get_ip_addresses(target_iface)
        final_addrs = [r.get("address") for r in final_ips]
        assert new_ip not in final_addrs, f"Rollback gagal: {new_ip} masih ada di router"

    print("      OK: Eksekusi update IP dan rollback bersih terverifikasi.")


if __name__ == "__main__":
    print("=" * 65)
    print("  TEST FASE UPDATE IP (CRUD UPDATE IP ADDRESS)")
    print("=" * 65)
    test_parsing()
    test_anti_lockout()
    test_live_router_execution()
    print("=" * 65)
    print("  SEMUA PENGUJIAN FITUR GANTI IP BERHASIL (100% PASS)")
    print("=" * 65)
