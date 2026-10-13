from mikrotik_adapter import (
    MikroTikAdapter,
    MANAGEMENT_INTERFACES,
    get_interface_states,
    enable_interface,
    disable_interface,
    get_nat_rules,
    enable_nat,
    disable_nat,
)

TARGET_IFACE = "ether4"
NAT_IFACE = "ether1"
NAT_COMMENT = "IBN_NAT_MASQ"


def run_tests():
    with MikroTikAdapter() as adapter:
        print("[1/5] Testing get_interface_states()...")
        ifaces = adapter.get_interface_states()
        assert isinstance(ifaces, list) and len(ifaces) > 0, "Daftar interface kosong"
        names = {i.get("name") for i in ifaces}
        assert TARGET_IFACE in names, f"Interface {TARGET_IFACE} tidak ditemukan di router"
        assert "ether2" in names, "Interface ether2 tidak ditemukan"
        print(f"      OK: Ditemukan {len(ifaces)} interface ({', '.join(sorted(names))}).")

        print(f"[2/5] Testing disable & enable pada {TARGET_IFACE}...")
        # Pastikan interface aktif sebelum pengujian
        adapter.enable_interface(TARGET_IFACE)

        # Matikan interface
        res_dis = adapter.disable_interface(TARGET_IFACE)
        assert res_dis["action"] == "disabled", f"Expected 'disabled', got {res_dis}"
        assert res_dis["disabled"] is True
        assert res_dis["name"] == TARGET_IFACE

        # Verifikasi status di router
        state_dis = next(i for i in adapter.get_interface_states() if i.get("name") == TARGET_IFACE)
        assert state_dis.get("disabled") is True, "Status interface di router bukan disabled=True"

        # Cek idempoten disable
        res_dis_noop = adapter.disable_interface(TARGET_IFACE)
        assert res_dis_noop["action"] == "noop", f"Expected 'noop', got {res_dis_noop}"
        assert res_dis_noop["disabled"] is True

        # Pulihkan / aktifkan kembali interface
        res_en = adapter.enable_interface(TARGET_IFACE)
        assert res_en["action"] == "enabled", f"Expected 'enabled', got {res_en}"
        assert res_en["disabled"] is False
        assert res_en["name"] == TARGET_IFACE

        # Verifikasi pemulihan di router
        state_en = next(i for i in adapter.get_interface_states() if i.get("name") == TARGET_IFACE)
        assert state_en.get("disabled") is False, "Status interface di router bukan disabled=False"

        # Cek idempoten enable
        res_en_noop = adapter.enable_interface(TARGET_IFACE)
        assert res_en_noop["action"] == "noop", f"Expected 'noop', got {res_en_noop}"
        assert res_en_noop["disabled"] is False
        print(f"      OK: Siklus disable -> verify -> enable -> verify pada {TARGET_IFACE} sukses.")

        print("[3/5] Testing Anti-Lockout rejection...")
        for mgmt_iface in MANAGEMENT_INTERFACES:
            try:
                adapter.disable_interface(mgmt_iface)
                assert False, f"Anti-lockout gagal: {mgmt_iface} diizinkan untuk dimatikan!"
            except ValueError as e:
                assert "Anti-lockout" in str(e), f"Pesan error tidak sesuai: {e}"
        print(f"      OK: Proteksi anti-lockout menolak pemutusan {MANAGEMENT_INTERFACES}.")

        print("[4/5] Testing enable_nat() idempoten pada ether1...")
        # Pre-cleanup
        adapter.disable_nat(NAT_IFACE, NAT_COMMENT)

        # Add NAT
        res_nat_add = adapter.enable_nat(NAT_IFACE, NAT_COMMENT)
        assert res_nat_add["action"] == "added", f"Expected 'added', got {res_nat_add}"
        assert res_nat_add["out_interface"] == NAT_IFACE
        assert res_nat_add["comment"] == NAT_COMMENT

        # Verifikasi di router
        nat_rules = [r for r in adapter.get_nat_rules() if r.get("comment") == NAT_COMMENT]
        assert len(nat_rules) == 1, f"Expected 1 NAT rule, got {len(nat_rules)}"
        assert nat_rules[0].get("action") == "masquerade"
        assert nat_rules[0].get("out-interface") == NAT_IFACE

        # Cek idempoten
        res_nat_noop = adapter.enable_nat(NAT_IFACE, NAT_COMMENT)
        assert res_nat_noop["action"] == "noop", f"Expected 'noop', got {res_nat_noop}"
        nat_rules_after = [r for r in adapter.get_nat_rules() if r.get("comment") == NAT_COMMENT]
        assert len(nat_rules_after) == 1, "Duplikasi rule NAT terdeteksi!"
        print(f"      OK: NAT rule ditambahkan dan terbukti idempoten (id={res_nat_add['id']}).")

        print("[5/5] Testing disable_nat() & clean rollback...")
        res_nat_del = adapter.disable_nat(NAT_IFACE, NAT_COMMENT)
        assert res_nat_del["action"] == "removed", f"Expected 'removed', got {res_nat_del}"
        assert res_nat_del["count"] >= 1, "Tidak ada rule yang dihapus"

        # Verifikasi clean rollback
        nat_remaining = [r for r in adapter.get_nat_rules() if r.get("comment") == NAT_COMMENT]
        assert len(nat_remaining) == 0, f"Rollback gagal: masih ada rule NAT {nat_remaining}"

        # Idempoten disable_nat
        res_nat_del2 = adapter.disable_nat(NAT_IFACE, NAT_COMMENT)
        assert res_nat_del2["action"] == "removed"
        assert res_nat_del2["count"] == 0
        print("      OK: NAT rule berhasil dibersihkan (clean rollback).")

    # Verifikasi modul-level functions juga dapat dipanggil
    mod_ifaces = get_interface_states()
    assert isinstance(mod_ifaces, list)
    mod_nat = get_nat_rules()
    assert isinstance(mod_nat, list)
    print("      OK: Modul-level wrappers berfungsi normal.")

    print("\nSEMUA PENGUJIAN FASE 1 (INTERFACE & NAT) SUKSES 100%!")


if __name__ == "__main__":
    run_tests()
