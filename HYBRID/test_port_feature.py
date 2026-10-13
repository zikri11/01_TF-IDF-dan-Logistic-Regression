from mikrotik_adapter import MikroTikAdapter
from nlp_parser import parse_intent
from policy_engine import execute_policy, build_network_policy


def test_nlp_parsing_port_features():
    print("[1/5] Testing NLP parsing & entity extraction for port features...")

    # Case 1: Physical interface QoS
    p1 = parse_intent("saya ingin port 3 kasih limit 5mb")
    assert p1["intent"] == "limit_bandwidth", f"Intent salah: {p1['intent']}"
    assert p1["entities"]["target"] == "ether3", f"Target salah: {p1['entities']['target']}"
    assert p1["entities"]["rate"] == "5mb", f"Rate salah: {p1['entities']['rate']}"
    assert p1["policy"]["is_valid"], f"Policy invalid: {p1['policy']['error']}"
    assert p1["policy"]["target"] == "ether3"
    assert p1["policy"]["rate"] == "5M/5M"
    assert p1["policy"]["name"] == "qos_ether3"
    print("      OK: 'saya ingin port 3 kasih limit 5mb' -> target=ether3, rate=5M/5M")

    # Case 2: Protocol port with target IP
    p2 = parse_intent("blokir port 80 untuk 192.168.88.50")
    assert p2["intent"] == "block_traffic", f"Intent salah: {p2['intent']}"
    assert p2["entities"]["target"] == "192.168.88.50"
    assert p2["entities"]["dst_port"] == 80
    assert p2["policy"]["is_valid"], f"Policy invalid: {p2['policy']['error']}"
    assert p2["policy"]["target"] == "192.168.88.50/32"
    assert p2["policy"]["dst_port"] == 80
    assert p2["policy"]["protocol"] == "tcp"
    print("      OK: 'blokir port 80 untuk 192.168.88.50' -> target=192.168.88.50/32, dst_port=80")

    # Case 3: Global protocol port drop (without IP)
    p3 = parse_intent("blokir port 443")
    assert p3["intent"] == "block_traffic", f"Intent salah: {p3['intent']}"
    assert p3["entities"]["target"] is None
    assert p3["entities"]["dst_port"] == 443
    assert p3["policy"]["is_valid"], f"Policy invalid: {p3['policy']['error']}"
    assert p3["policy"]["target"] is None
    assert p3["policy"]["dst_port"] == 443
    assert p3["policy"]["protocol"] == "tcp"
    print("      OK: 'blokir port 443' -> global drop dst_port=443")

    # Case 4: Invalid interface rejected with educational message
    p4 = parse_intent("port 5 kasih limit 5mb")
    assert p4["intent"] == "limit_bandwidth", f"Intent salah: {p4['intent']}"
    assert p4["entities"]["target"] == "ether5"
    assert not p4["policy"]["is_valid"]
    assert "Interface ether5 tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)" in p4["policy"]["error"]
    print("      OK: 'port 5 kasih limit 5mb' -> ditolak edukatif (hAP lite ether1-ether4)")


def test_service_aliases():
    print("[2/5] Testing firewall service aliases (http, https, ssh, dns)...")
    aliases = [
        ("blokir http untuk 192.168.88.50", 80),
        ("blokir https", 443),
        ("blokir ssh untuk 192.168.88.50", 22),
        ("blokir dns", 53),
    ]
    for text, exp_port in aliases:
        parsed = parse_intent(text)
        assert parsed["intent"] == "block_traffic"
        assert parsed["entities"]["dst_port"] == exp_port, f"Failed for '{text}': got {parsed['entities']['dst_port']}"
        assert parsed["policy"]["is_valid"]
        assert parsed["policy"]["dst_port"] == exp_port
    print("      OK: Semua service alias (http->80, https->443, ssh->22, dns->53) valid.")


def test_physical_port_qos_router():
    print("[3/5] Testing live router QoS interface ('saya ingin port 3 kasih limit 5mb') & rollback...")
    with MikroTikAdapter() as adapter:
        adapter.remove_bandwidth_limit("ether3")

        parsed = parse_intent("saya ingin port 3 kasih limit 5mb")
        res = execute_policy(parsed["policy"], adapter=adapter)
        assert res["status"] == "success", f"Eksekusi gagal: {res}"

        # Verifikasi antrean di router
        queues = adapter.get_bandwidth_limits()
        match = [q for q in queues if q.get("name") == "qos_ether3" or q.get("target") == "ether3"]
        assert len(match) == 1, f"Queue ether3 tidak ditemukan di router: {queues}"
        assert match[0].get("target") == "ether3"
        print(f"      OK: Queue ether3 aktif di router (id={match[0]['.id']}).")

        # Rollback
        removed = adapter.remove_bandwidth_limit("ether3")
        assert removed >= 1, "Gagal rollback queue ether3"
        remaining = [q for q in adapter.get_bandwidth_limits() if q.get("target") == "ether3"]
        assert len(remaining) == 0, "Sisa queue ether3 masih ada!"
        print("      OK: Rollback queue ether3 tuntas.")


def test_protocol_port_firewall_router():
    print("[4/5] Testing live router Firewall port blocks & idempotency & rollback...")
    with MikroTikAdapter() as adapter:
        # Pre-cleanup
        adapter.remove_firewall_block(target="192.168.88.50", dst_port=80)
        adapter.remove_firewall_block(dst_port=443)

        # 1. Target IP + Dst Port 80
        p_p80 = parse_intent("blokir port 80 untuk 192.168.88.50")
        res_p80 = execute_policy(p_p80["policy"], adapter=adapter)
        assert res_p80["status"] == "success"
        assert res_p80["result"]["action"] == "added"

        # Idempotent check
        res_p80_idem = execute_policy(p_p80["policy"], adapter=adapter)
        assert res_p80_idem["status"] == "success"
        assert res_p80_idem["result"]["action"] == "noop", f"Idempotensi port 80 gagal: {res_p80_idem}"
        print("      OK: Blokir port 80 untuk IP sukses & terbukti idempoten (action='noop').")

        # 2. Global Port 443 Drop
        p_p443 = parse_intent("blokir port 443")
        res_p443 = execute_policy(p_p443["policy"], adapter=adapter)
        assert res_p443["status"] == "success"
        assert res_p443["result"]["action"] == "added"

        # Idempotent check
        res_p443_idem = execute_policy(p_p443["policy"], adapter=adapter)
        assert res_p443_idem["status"] == "success"
        assert res_p443_idem["result"]["action"] == "noop", f"Idempotensi port 443 gagal: {res_p443_idem}"
        print("      OK: Global drop port 443 sukses & terbukti idempoten (action='noop').")

        # Verifikasi keberadaan rules di router
        fw_rules = adapter.get_firewall_blocks()
        has_p80 = any(
            str(r.get("dst-port", "")) == "80" and r.get("src-address", "").split("/")[0] == "192.168.88.50"
            for r in fw_rules
        )
        has_p443 = any(str(r.get("dst-port", "")) == "443" for r in fw_rules)
        assert has_p80, "Rule port 80 tidak ditemukan di firewall filter"
        assert has_p443, "Rule port 443 tidak ditemukan di firewall filter"

        # Rollback via intent / adapter
        rem_p80 = adapter.remove_firewall_block(target="192.168.88.50", dst_port=80)
        rem_p443 = adapter.remove_firewall_block(dst_port=443)
        assert rem_p80 >= 1, "Gagal rollback firewall port 80"
        assert rem_p443 >= 1, "Gagal rollback firewall port 443"

        # Verifikasi bersih total
        fw_after = adapter.get_firewall_blocks()
        assert not any(str(r.get("dst-port", "")) in ("80", "443") for r in fw_after), "Sisa rule firewall port masih ada!"
        print("      OK: Rollback firewall port 80 & 443 tuntas, router bersih.")


def test_invalid_interface_rejected():
    print("[5/5] Testing rejection of invalid interface ('port 5 kasih limit 5mb')...")
    with MikroTikAdapter() as adapter:
        parsed = parse_intent("port 5 kasih limit 5mb")
        res = execute_policy(parsed["policy"], adapter=adapter)
        assert res["status"] == "error", f"Policy harusnya gagal dieksekusi: {res}"
        assert "Interface ether5 tidak ada di hAP lite" in res["error"]
        print("      OK: Eksekusi ditolak secara edukatif.")


def run_all():
    test_nlp_parsing_port_features()
    test_service_aliases()
    test_physical_port_qos_router()
    test_protocol_port_firewall_router()
    test_invalid_interface_rejected()
    print("\nSEMUA PENGUJIAN PORT FEATURE SUKSES 100%!")


if __name__ == "__main__":
    run_all()
