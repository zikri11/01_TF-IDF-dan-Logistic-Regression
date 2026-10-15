from mikrotik_adapter import MikroTikAdapter
from policy_engine import build_network_policy, execute_policy, normalize_ip_address


def test_build_policy_get_interface_ip():
    print("[1/5] Testing build_network_policy for 'get_interface_ip'...")
    # None (all interfaces)
    p_none = build_network_policy("get_interface_ip")
    assert p_none["is_valid"]
    assert p_none["target"] is None
    assert p_none["name"] == "check_ip"
    assert p_none["action"] == "get_interface_telemetry"

    # Single 'port 1'
    p_port1 = build_network_policy("get_interface_ip", "port 1")
    assert p_port1["is_valid"]
    assert p_port1["target"] == "ether1"
    assert p_port1["name"] == "check_ip"

    # Single 'jalur 1'
    p_jalur1 = build_network_policy("get_interface_ip", "jalur 1")
    assert p_jalur1["is_valid"]
    assert p_jalur1["target"] == "ether1"
    assert p_jalur1["name"] == "check_ip"

    # Multi ['port 1', 'port 3']
    p_multi = build_network_policy("get_interface_ip", ["port 1", "port 3"])
    assert p_multi["is_valid"]
    assert p_multi["target"] == ["ether1", "ether3"]
    assert p_multi["name"] == "check_ip"

    # Multi with 'jalur'
    p_multi_jalur = build_network_policy("get_interface_ip", ["jalur 2", "ether4"])
    assert p_multi_jalur["is_valid"]
    assert p_multi_jalur["target"] == ["ether2", "ether4"]
    print("      OK: Policy get_interface_ip (None, port 1, jalur 1, multi) valid.")


def test_invalid_interface_rejection():
    print("[2/5] Testing invalid interface rejection ('port 5' / 'jalur 5')...")
    for inv in ("port 5", "jalur 5", "ether5", "port 10"):
        p_telem = build_network_policy("get_interface_ip", inv)
        assert not p_telem["is_valid"]
        assert "tidak ada di hAP lite" in p_telem["error"]

        p_add = build_network_policy("add_ip_address", "10.10.10.1", interface=inv)
        assert not p_add["is_valid"]
        assert "tidak ada di hAP lite" in p_add["error"]

    p_multi_inv = build_network_policy("get_interface_ip", ["port 1", "port 5"])
    assert not p_multi_inv["is_valid"]
    assert "tidak ada di hAP lite" in p_multi_inv["error"]
    print("      OK: Penolakan interface invalid edukatif dan akurat.")


def test_add_ip_normalization():
    print("[3/5] Testing add_ip_address normalization ('10.10.10.1' di 'port 3' -> '/24' di 'ether3')...")
    # Unit test normalize_ip_address
    assert normalize_ip_address("10.10.10.1") == "10.10.10.1/24"
    assert normalize_ip_address("10.10.10.1/16") == "10.10.10.1/16"

    # Target as IP, interface as 'port 3'
    p1 = build_network_policy("add_ip_address", target="10.10.10.1", interface="port 3")
    assert p1["is_valid"]
    assert p1["address"] == "10.10.10.1/24"
    assert p1["interface"] == "ether3"
    assert p1["name"] == "ip_ether3"

    # Target as IP, interface as 'jalur 3'
    p2 = build_network_policy("add_ip_address", target="10.10.10.1", interface="jalur 3")
    assert p2["is_valid"]
    assert p2["address"] == "10.10.10.1/24"
    assert p2["interface"] == "ether3"

    # Explicit address & interface kwargs
    p3 = build_network_policy("add_ip_address", address="10.10.10.1", interface="port 3")
    assert p3["is_valid"]
    assert p3["address"] == "10.10.10.1/24"
    assert p3["interface"] == "ether3"
    print("      OK: Normalisasi '/24' otomatis dan konversi port/jalur sukses.")


def test_anti_lockout():
    print("[4/5] Testing anti-lockout protection for 192.168.88.1...")
    # Add IP manajemen
    for bad_ip in ("192.168.88.1", "192.168.88.1/24"):
        p_add = build_network_policy("add_ip_address", address=bad_ip, interface="ether3")
        assert not p_add["is_valid"]
        assert "Anti-lockout" in p_add["error"]

        res_add = execute_policy(p_add)
        assert res_add["status"] == "error"
        assert "Anti-lockout" in res_add["error"]

    # Remove IP manajemen
    for bad_ip in ("192.168.88.1", "192.168.88.1/24"):
        p_rem = build_network_policy("remove_ip_address", address=bad_ip)
        assert not p_rem["is_valid"]
        assert "Anti-lockout" in p_rem["error"]

        res_rem = execute_policy(p_rem)
        assert res_rem["status"] == "error"
        assert "Anti-lockout" in res_rem["error"]

    # Remove on management interface bridge without address
    p_rem_bridge = build_network_policy("remove_ip_address", interface="bridge")
    assert not p_rem_bridge["is_valid"]
    assert "Anti-lockout" in p_rem_bridge["error"]
    print("      OK: Proteksi Anti-lockout 192.168.88.1 (add & remove) aktif 100%.")


def test_live_router_execution():
    print("[5/5] Testing live router execution via execute_policy()...")
    test_ip = "10.10.10.1/24"
    test_iface = "ether3"

    with MikroTikAdapter() as adapter:
        # Pre-cleanup
        adapter.remove_ip_address(address=test_ip, interface=test_iface)

        # 1. Cek telemetry ether1 (baca IP dan status)
        p_telem_eth1 = build_network_policy("get_interface_ip", "ether1")
        res_telem_eth1 = execute_policy(p_telem_eth1, adapter=adapter)
        assert res_telem_eth1["status"] == "success", f"Telemetry ether1 gagal: {res_telem_eth1}"
        assert isinstance(res_telem_eth1["result"], list) and len(res_telem_eth1["result"]) == 1
        eth1_info = res_telem_eth1["result"][0]
        assert eth1_info["name"] == "ether1"
        assert "ips" in eth1_info
        assert "running" in eth1_info
        assert "disabled" in eth1_info
        print(f"      OK: Telemetry ether1 terbaca (running={eth1_info['running']}, ips={eth1_info['ips']}).")

        # 2. Tambah IP 10.10.10.1/24 di ether3 via execute_policy
        p_add = build_network_policy("add_ip_address", target="10.10.10.1", interface="port 3")
        res_add = execute_policy(p_add, adapter=adapter)
        assert res_add["status"] == "success", f"Add IP gagal: {res_add}"
        assert res_add["result"]["action"] == "added"
        assert res_add["result"]["address"] == test_ip
        assert res_add["result"]["interface"] == test_iface

        # Idempotensi add_ip_address
        res_add_noop = execute_policy(p_add, adapter=adapter)
        assert res_add_noop["status"] == "success"
        assert res_add_noop["result"]["action"] == "noop"
        print(f"      OK: IP {test_ip} berhasil ditambahkan di {test_iface} via execute_policy() & idempoten.")

        # 3. Cek telemetry ether3 terkonfirmasi IP 10.10.10.1/24
        p_telem_eth3 = build_network_policy("get_interface_ip", "port 3")
        res_telem_eth3 = execute_policy(p_telem_eth3, adapter=adapter)
        assert res_telem_eth3["status"] == "success"
        assert len(res_telem_eth3["result"]) == 1
        eth3_info = res_telem_eth3["result"][0]
        assert eth3_info["name"] == test_iface
        assert test_ip in eth3_info["ips"], f"IP {test_ip} tidak terkonfirmasi di telemetry {test_iface}: {eth3_info['ips']}"
        print(f"      OK: Telemetry ether3 mengonfirmasi keberadaan IP {test_ip}.")

        # 4. Rollback bersih via remove_ip_address
        p_rem = build_network_policy("remove_ip_address", target="10.10.10.1", interface="port 3")
        res_rem = execute_policy(p_rem, adapter=adapter)
        assert res_rem["status"] == "success", f"Remove IP gagal: {res_rem}"
        assert res_rem["result"]["action"] == "removed"
        assert res_rem["result"]["count"] >= 1

        # Verifikasi bersih via telemetry
        res_verify = execute_policy(p_telem_eth3, adapter=adapter)
        assert res_verify["status"] == "success"
        assert test_ip not in res_verify["result"][0]["ips"], f"Rollback gagal: {test_ip} masih ada di ether3"
        print(f"      OK: Rollback sukses, {test_ip} bersih dari router.")


def run_all():
    test_build_policy_get_interface_ip()
    test_invalid_interface_rejection()
    test_add_ip_normalization()
    test_anti_lockout()
    test_live_router_execution()
    print("\nSEMUA PENGUJIAN FASE 2 (IP ADDRESS & TELEMETRY) SUKSES 100%!")


if __name__ == "__main__":
    run_all()