from mikrotik_adapter import MikroTikAdapter, MANAGEMENT_INTERFACES
from policy_engine import build_network_policy, execute_policy


def test_build_network_policy():
    print("[1/5] Testing build_network_policy for interface & NAT...")
    # Interface valid
    p1 = build_network_policy("enable_interface", "ether4")
    assert p1["is_valid"] and p1["target"] == "ether4" and p1["name"] == "iface_ether4"

    p2 = build_network_policy("disable_interface", "ether4")
    assert p2["is_valid"] and p2["target"] == "ether4" and p2["name"] == "iface_ether4"

    # Interface normalisasi 'port X' -> 'etherX'
    p3 = build_network_policy("enable_interface", "port 4")
    assert p3["is_valid"] and p3["target"] == "ether4" and p3["name"] == "iface_ether4"

    # Interface kosong
    p_empty = build_network_policy("enable_interface", "")
    assert not p_empty["is_valid"] and "wajib diisi" in p_empty["error"]

    # NAT default out_interface ether1
    p_nat_def = build_network_policy("enable_nat")
    assert p_nat_def["is_valid"]
    assert p_nat_def["target"] == "ether1"
    assert p_nat_def["name"] == "nat_ether1"
    assert p_nat_def["comment"] == "IBN_NAT_MASQ"

    # NAT explicit out_interface
    p_nat_eth2 = build_network_policy("enable_nat", "ether2")
    assert p_nat_eth2["is_valid"] and p_nat_eth2["target"] == "ether2" and p_nat_eth2["name"] == "nat_ether2"

    p_nat_dis = build_network_policy("disable_nat")
    assert p_nat_dis["is_valid"] and p_nat_dis["target"] == "ether1" and p_nat_dis["name"] == "nat_ether1"
    print("      OK: Policy building & normalisasi interface/NAT valid.")


def test_anti_lockout_interface():
    print("[2/5] Testing anti-lockout interface shield (ether2 & bridge)...")
    for iface in ("ether2", "bridge", "port 2"):
        pol = build_network_policy("disable_interface", iface)
        assert not pol["is_valid"], f"Policy disable {iface} harus ditolak!"
        assert "Anti-lockout" in pol["error"], f"Pesan anti-lockout tidak ada: {pol['error']}"

        res = execute_policy(pol)
        assert res["status"] == "error", f"Eksekusi {iface} harus gagal!"
        assert "Anti-lockout" in res["error"]

    # Namun enable ether2 / bridge diizinkan
    assert build_network_policy("enable_interface", "ether2")["is_valid"]
    assert build_network_policy("enable_interface", "bridge")["is_valid"]
    print("      OK: Proteksi anti-lockout menolak disable interface manajemen.")


def test_invalid_interface_rejection():
    print("[3/5] Testing invalid interface rejection (port 5, ether5, dll)...")
    for inv in ("port 5", "ether5", "port 10", "unknown_iface"):
        p_en = build_network_policy("enable_interface", inv)
        assert not p_en["is_valid"]
        assert "tidak ada di hAP lite" in p_en["error"]

        p_dis = build_network_policy("disable_interface", inv)
        assert not p_dis["is_valid"]
        assert "tidak ada di hAP lite" in p_dis["error"]
    print("      OK: Penolakan interface invalid edukatif dan tepat sasaran.")


def test_live_router_interface_execution():
    print("[4/5] Testing live router execution: disable & enable ether4 via execute_policy()...")
    with MikroTikAdapter() as adapter:
        # Pre-kondisi: pastikan ether4 enable
        adapter.enable_interface("ether4")

        # 1. Disable ether4 via execute_policy
        p_dis = build_network_policy("disable_interface", "ether4")
        res_dis = execute_policy(p_dis, adapter=adapter)
        assert res_dis["status"] == "success", f"Disable ether4 gagal: {res_dis}"
        assert res_dis["result"]["action"] == "disabled"
        assert res_dis["result"]["disabled"] is True

        state_dis = next(i for i in adapter.get_interface_states() if i.get("name") == "ether4")
        assert state_dis.get("disabled") is True, "Status ether4 di router bukan disabled"

        # Idempotensi disable
        res_dis_noop = execute_policy(p_dis, adapter=adapter)
        assert res_dis_noop["result"]["action"] == "noop"

        # 2. Enable ether4 via execute_policy
        p_en = build_network_policy("enable_interface", "ether4")
        res_en = execute_policy(p_en, adapter=adapter)
        assert res_en["status"] == "success", f"Enable ether4 gagal: {res_en}"
        assert res_en["result"]["action"] == "enabled"
        assert res_en["result"]["disabled"] is False

        state_en = next(i for i in adapter.get_interface_states() if i.get("name") == "ether4")
        assert state_en.get("disabled") is False, "Status ether4 di router bukan active/enabled"

        # Idempotensi enable
        res_en_noop = execute_policy(p_en, adapter=adapter)
        assert res_en_noop["result"]["action"] == "noop"
        print("      OK: Siklus disable & enable ether4 via execute_policy() sukses & idempoten.")


def test_live_router_nat_execution_and_rollback():
    print("[5/5] Testing live router execution: enable_nat & disable_nat ether1 & rollback...")
    with MikroTikAdapter() as adapter:
        # Pre-cleanup
        p_clean = build_network_policy("disable_nat", "ether1")
        execute_policy(p_clean, adapter=adapter)

        # 1. Enable NAT via execute_policy (default ether1)
        p_nat = build_network_policy("enable_nat")
        res_nat = execute_policy(p_nat, adapter=adapter)
        assert res_nat["status"] == "success", f"Enable NAT gagal: {res_nat}"
        assert res_nat["result"]["action"] == "added"

        # Verifikasi rule ada di router
        rules = [r for r in adapter.get_nat_rules() if r.get("comment") == "IBN_NAT_MASQ"]
        assert len(rules) == 1, f"Expected 1 NAT rule, got {len(rules)}"
        assert rules[0].get("out-interface") == "ether1"
        assert rules[0].get("action") == "masquerade"

        # Idempotensi NAT
        res_nat_noop = execute_policy(p_nat, adapter=adapter)
        assert res_nat_noop["result"]["action"] == "noop"

        # 2. Disable NAT via execute_policy & clean rollback
        p_dis_nat = build_network_policy("disable_nat", "ether1")
        res_dis_nat = execute_policy(p_dis_nat, adapter=adapter)
        assert res_dis_nat["status"] == "success", f"Disable NAT gagal: {res_dis_nat}"
        assert res_dis_nat["result"]["action"] == "removed"
        assert res_dis_nat["result"]["count"] >= 1

        # Verifikasi bersih total
        rules_after = [r for r in adapter.get_nat_rules() if r.get("comment") == "IBN_NAT_MASQ"]
        assert len(rules_after) == 0, f"Sisa NAT rule masih ada: {rules_after}"

        # Pastikan interface ether4 dalam kondisi pulih/aktif
        iface_ether4 = next(i for i in adapter.get_interface_states() if i.get("name") == "ether4")
        assert iface_ether4.get("disabled") is False, "ether4 tidak aktif setelah rollback"
        print("      OK: NAT masquerade berhasil dibuat, diuji, dan dibersihkan total (clean rollback).")


def run_all():
    test_build_network_policy()
    test_anti_lockout_interface()
    test_invalid_interface_rejection()
    test_live_router_interface_execution()
    test_live_router_nat_execution_and_rollback()
    print("\nSEMUA PENGUJIAN FASE 2 (INTERFACE & NAT) SUKSES 100%!")


if __name__ == "__main__":
    run_all()
