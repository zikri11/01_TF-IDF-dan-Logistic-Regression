from mikrotik_adapter import (
    MikroTikAdapter,
    MANAGEMENT_IPS,
    get_ip_addresses,
    get_interface_telemetry,
    add_ip_address,
    remove_ip_address,
)

TARGET_IP = "10.10.10.1/24"
TARGET_IFACE = "ether3"
MGMT_IP = "192.168.88.1/24"


def run_tests():
    with MikroTikAdapter() as adapter:
        print("[1/6] Testing get_ip_addresses() global & filtered...")
        all_ips = adapter.get_ip_addresses()
        assert isinstance(all_ips, list) and len(all_ips) > 0, "Daftar IP address kosong"
        assert any(MGMT_IP in r.get("address", "") for r in all_ips), f"IP manajemen {MGMT_IP} tidak ditemukan"

        ether1_ips = adapter.get_ip_addresses("ether1")
        assert isinstance(ether1_ips, list) and len(ether1_ips) > 0, "IP ether1 kosong"
        assert all(
            r.get("interface", "").lower() == "ether1" or r.get("actual-interface", "").lower() == "ether1"
            for r in ether1_ips
        ), "Filter interface ether1 tidak cocok"
        print(f"      OK: get_ip_addresses() global ({len(all_ips)} record) & filter ether1 ({len(ether1_ips)} record).")

        print("[2/6] Testing get_interface_telemetry() single & multi...")
        telem_single = adapter.get_interface_telemetry("ether1")
        assert isinstance(telem_single, list) and len(telem_single) == 1, "Expected single telemetry item"
        item = telem_single[0]
        for key in ("name", "type", "mac", "disabled", "running", "ips"):
            assert key in item, f"Missing key '{key}' in telemetry: {item}"
        assert item["name"] == "ether1"
        assert isinstance(item["disabled"], bool)
        assert isinstance(item["running"], bool)
        assert isinstance(item["ips"], list)

        telem_multi = adapter.get_interface_telemetry(["ether1", "ether2"])
        assert isinstance(telem_multi, list) and len(telem_multi) == 2, "Expected 2 telemetry items"
        names = {i["name"] for i in telem_multi}
        assert names == {"ether1", "ether2"}, f"Names mismatch: {names}"
        print("      OK: get_interface_telemetry() single ('ether1') & multi (['ether1', 'ether2']) valid.")

        print(f"[3/6] Testing add_ip_address('{TARGET_IP}', '{TARGET_IFACE}')...")
        # Pre-cleanup
        adapter.remove_ip_address(TARGET_IP, TARGET_IFACE)

        res_add = adapter.add_ip_address(TARGET_IP, TARGET_IFACE)
        assert res_add["action"] == "added", f"Expected 'added', got {res_add}"
        assert res_add["address"] == TARGET_IP
        assert res_add["interface"] == TARGET_IFACE
        assert "id" in res_add

        # Verifikasi di router
        current_ether3 = adapter.get_ip_addresses(TARGET_IFACE)
        assert any(r.get("address") == TARGET_IP for r in current_ether3), "IP baru tidak ditemukan di router"
        print(f"      OK: add_ip_address sukses (id={res_add['id']}).")

        print(f"[4/6] Testing idempotensi add_ip_address pada {TARGET_IFACE}...")
        res_noop = adapter.add_ip_address(TARGET_IP, TARGET_IFACE)
        assert res_noop["action"] == "noop", f"Expected 'noop', got {res_noop}"
        assert res_noop["id"] == res_add["id"]
        assert res_noop["address"] == TARGET_IP
        assert res_noop["interface"] == TARGET_IFACE

        # Konflik interface lain
        try:
            adapter.add_ip_address(TARGET_IP, "ether4")
            assert False, "Harus melempar ValueError jika IP sudah ada di interface lain"
        except ValueError as e:
            assert "sudah ada di interface lain" in str(e)
        print("      OK: Idempotensi terverifikasi (noop) & konflik interface lain ditolak.")

        print("[5/6] Testing proteksi Anti-Lockout (192.168.88.1/24)...")
        # Tolak add IP manajemen
        for test_ip in (MGMT_IP, "192.168.88.1"):
            try:
                adapter.add_ip_address(test_ip, "ether3")
                assert False, f"Anti-lockout gagal: diizinkan add {test_ip}"
            except ValueError as e:
                assert "Anti-lockout" in str(e), f"Pesan error salah: {e}"

        # Tolak remove IP manajemen
        for test_ip in (MGMT_IP, "192.168.88.1"):
            try:
                adapter.remove_ip_address(address=test_ip)
                assert False, f"Anti-lockout gagal: diizinkan remove {test_ip}"
            except ValueError as e:
                assert "Anti-lockout" in str(e), f"Pesan error salah: {e}"

        # Tolak remove interface tempat IP manajemen terpasang
        try:
            adapter.remove_ip_address(interface="bridge")
            assert False, "Anti-lockout gagal: diizinkan remove IP di bridge manajemen"
        except ValueError as e:
            assert "Anti-lockout" in str(e), f"Pesan error salah: {e}"
        print("      OK: Proteksi anti-lockout 192.168.88.1/24 dan bridge aktif 100%.")

        print(f"[6/6] Testing remove_ip_address('{TARGET_IP}', '{TARGET_IFACE}') & rollback...")
        res_del = adapter.remove_ip_address(TARGET_IP, TARGET_IFACE)
        assert res_del["action"] == "removed", f"Expected 'removed', got {res_del}"
        assert res_del["count"] >= 1

        # Verifikasi bersih di router
        clean_ether3 = adapter.get_ip_addresses(TARGET_IFACE)
        assert not any(r.get("address") == TARGET_IP for r in clean_ether3), "Rollback gagal: IP masih ada di router"

        # Idempoten remove
        res_del_noop = adapter.remove_ip_address(TARGET_IP, TARGET_IFACE)
        assert res_del_noop["action"] == "removed"
        assert res_del_noop["count"] == 0
        print("      OK: remove_ip_address berhasil dan rollback bersih.")

    # Verifikasi modul-level wrapper
    assert isinstance(get_ip_addresses(), list)
    assert isinstance(get_interface_telemetry(), list)
    print("      OK: Modul-level wrappers berfungsi normal.")

    print("\nSEMUA PENGUJIAN FASE 1 (IP ADDRESS & TELEMETRY) SUKSES 100%!")


if __name__ == "__main__":
    run_tests()
