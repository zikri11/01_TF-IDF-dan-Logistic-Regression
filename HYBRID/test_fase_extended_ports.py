import re
from mikrotik_adapter import MikroTikAdapter
from nlp_parser import parse_intent, _extract_interfaces
from policy_engine import _normalize_interface_str, normalize_target, execute_policy


def test_parsing_dan_normalisasi_alias():
    print("[1/5] Testing parsing dan normalisasi setiap alias ethernet...")
    test_cases = [
        ("port 1", "ether1"),
        ("eth 2", "ether2"),
        ("lan 3", "ether3"),
        ("int 4", "ether4"),
        ("jalur 1", "ether1"),
        ("iface 2", "ether2"),
        ("colokan 3", "ether3"),
        ("kabel lan 4", "ether4"),
        ("link 1", "ether1"),
        ("interfaces 2", "ether2"),
    ]
    for alias, expected in test_cases:
        norm_iface = _normalize_interface_str(alias)
        assert norm_iface == expected, f"Normalize interface failed for '{alias}': got {norm_iface}, expected {expected}"

        norm_tgt = normalize_target(alias)
        assert norm_tgt == expected, f"Normalize target failed for '{alias}': got {norm_tgt}, expected {expected}"

        ext = _extract_interfaces(alias)
        assert expected in ext, f"Extract interfaces failed for '{alias}': got {ext}, expected {expected}"

        # Test full NLP command parsing
        cmd = f"batasi {alias} jadi 2mb"
        parsed = parse_intent(cmd)
        assert parsed["intent"] == "limit_bandwidth", f"Intent wrong for '{cmd}': {parsed['intent']}"
        assert parsed["entities"]["target"] == expected, f"Target entity wrong for '{cmd}': {parsed['entities']['target']}"
        assert parsed["policy"]["is_valid"], f"Policy invalid for '{cmd}': {parsed['policy']['error']}"
        assert parsed["policy"]["target"] == expected, f"Policy target wrong for '{cmd}': {parsed['policy']['target']}"
        assert parsed["policy"]["rate"] == "2M/2M"

    print("      OK: Seluruh 10 alias ethernet berhasil diparsing dan dinormalisasi.")


def test_penulisan_tanpa_spasi():
    print("[2/5] Testing penulisan interface tanpa spasi (lan1, eth2, int3, iface4)...")
    no_space_cases = [
        ("lan1", "ether1"),
        ("eth2", "ether2"),
        ("int3", "ether3"),
        ("iface4", "ether4"),
    ]
    for alias, expected in no_space_cases:
        norm_iface = _normalize_interface_str(alias)
        assert norm_iface == expected, f"Normalize interface failed for '{alias}': got {norm_iface}, expected {expected}"

        norm_tgt = normalize_target(alias)
        assert norm_tgt == expected, f"Normalize target failed for '{alias}': got {norm_tgt}, expected {expected}"

        ext = _extract_interfaces(alias)
        assert expected in ext, f"Extract interfaces failed for '{alias}': got {ext}, expected {expected}"

        # Test NLP parsing
        cmd = f"cek ip {alias}"
        parsed = parse_intent(cmd)
        assert parsed["intent"] == "get_interface_ip", f"Intent wrong for '{cmd}': {parsed['intent']}"
        assert parsed["entities"]["target"] == expected, f"Target entity wrong for '{cmd}': {parsed['entities']['target']}"
        assert parsed["policy"]["is_valid"], f"Policy invalid for '{cmd}': {parsed['policy']['error']}"
        assert parsed["policy"]["target"] == expected

    print("      OK: Seluruh alias tanpa spasi berhasil dinormalisasi dan diekstrak.")


def test_multi_target_campuran():
    print("[3/5] Testing multi-target campuran ('cek ip lan 1 dan colokan 3')...")
    cmd = "cek ip lan 1 dan colokan 3"
    parsed = parse_intent(cmd)
    assert parsed["intent"] == "get_interface_ip", f"Intent wrong: {parsed['intent']}"
    assert parsed["entities"]["target"] == ["ether1", "ether3"], f"Target entities wrong: {parsed['entities']['target']}"
    assert parsed["policy"]["is_valid"], f"Policy invalid: {parsed['policy']['error']}"
    assert parsed["policy"]["target"] == ["ether1", "ether3"]
    assert parsed["policy"]["action"] == "get_interface_telemetry"
    print("      OK: 'cek ip lan 1 dan colokan 3' -> ['ether1', 'ether3'] valid.")


def test_penolakan_port_invalid():
    print("[4/5] Testing penolakan port invalid ('cek lan 5' & 'batasi eth 5 jadi 2mb')...")
    # Case 1: cek lan 5
    p1 = parse_intent("cek lan 5")
    assert p1["intent"] == "get_interface_ip"
    assert p1["entities"]["target"] == "ether5"
    assert not p1["policy"]["is_valid"]
    assert "Interface ether5 tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)" in p1["policy"]["error"]
    print("      OK: 'cek lan 5' ditolak edukatif (ether5 tidak tersedia).")

    # Case 2: batasi eth 5 jadi 2mb
    p2 = parse_intent("batasi eth 5 jadi 2mb")
    assert p2["intent"] == "limit_bandwidth"
    assert p2["entities"]["target"] == "ether5"
    assert not p2["policy"]["is_valid"]
    assert "Interface ether5 tidak ada di hAP lite (tersedia: ether1 - ether4, wlan1)" in p2["policy"]["error"]
    print("      OK: 'batasi eth 5 jadi 2mb' ditolak edukatif (ether5 tidak tersedia).")


def test_live_router_execution_dan_rollback():
    print("[5/5] Testing live router execution & rollback (batasi eth 3, cek ip lan 1, rollback)...")
    with MikroTikAdapter() as adapter:
        # Pre-cleanup
        adapter.remove_bandwidth_limit("ether3")

        # 1. Batasi eth 3
        p_limit = parse_intent("batasi eth 3 jadi 2mb")
        assert p_limit["policy"]["is_valid"], f"Policy invalid: {p_limit['policy']['error']}"
        res_limit = execute_policy(p_limit["policy"], adapter=adapter)
        assert res_limit["status"] == "success", f"Exec limit failed: {res_limit}"
        assert res_limit["result"]["target"] == "ether3"
        assert res_limit["result"]["max_limit"] == "2M/2M"

        # Verifikasi queue aktif di router
        queues = adapter.get_bandwidth_limits()
        match_q = [q for q in queues if q.get("target") == "ether3"]
        assert len(match_q) == 1, f"Queue ether3 tidak ditemukan di router: {queues}"
        print(f"      OK: Queue ether3 aktif di router (id={match_q[0]['.id']}, max-limit={match_q[0].get('max-limit')}).")

        # 2. Cek ip lan 1
        p_cek = parse_intent("cek ip lan 1")
        assert p_cek["policy"]["is_valid"], f"Policy invalid: {p_cek['policy']['error']}"
        res_cek = execute_policy(p_cek["policy"], adapter=adapter)
        assert res_cek["status"] == "success", f"Exec cek ip failed: {res_cek}"
        telemetry = res_cek["result"]
        assert isinstance(telemetry, list) and len(telemetry) >= 1
        assert telemetry[0]["name"] == "ether1"
        print(f"      OK: Telemetri lan 1 (ether1) terbaca: {telemetry[0]['ips']}.")

        # 3. Rollback
        removed = adapter.remove_bandwidth_limit("ether3")
        assert removed >= 1, "Gagal rollback queue ether3"
        queues_after = [q for q in adapter.get_bandwidth_limits() if q.get("target") == "ether3"]
        assert len(queues_after) == 0, "Sisa queue ether3 masih tertinggal!"
        print("      OK: Rollback queue ether3 tuntas, router bersih.")


if __name__ == "__main__":
    print("=" * 70)
    print("  PENGUJIAN PERLUASAN KOSAKATA ETHERNET (EXTENDED PORTS TEST)")
    print("=" * 70)
    test_parsing_dan_normalisasi_alias()
    test_penulisan_tanpa_spasi()
    test_multi_target_campuran()
    test_penolakan_port_invalid()
    test_live_router_execution_dan_rollback()
    print("=" * 70)
    print("  SEMUA PENGUJIAN EXTENDED PORTS SUKSES 100%!")
    print("=" * 70)
