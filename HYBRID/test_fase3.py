import time
from mikrotik_adapter import MikroTikAdapter
from nlp_parser import parse_intent
from policy_engine import execute_policy

DUMMY_IP = "192.168.88.250"


def test_unseen_prompts():
    print("[1/5] Testing 8 unseen natural language prompts...")
    cases = [
        # (text, expected_intent, expected_target, expected_rate)
        (
            "Tolong pasang limit kecepatan client 192.168.88.200 ke 3 Mbps",
            "limit_bandwidth",
            "192.168.88.200",
            "3 Mbps",
        ),
        (
            "Batasin kecepatan internet user 192.168.88.201 hingga 512k",
            "limit_bandwidth",
            "192.168.88.201",
            "512k",
        ),
        (
            "Hilangkan batasan bandwidth untuk laptop 192.168.88.202",
            "remove_limit",
            "192.168.88.202",
            None,
        ),
        (
            "Cabut pembatasan kecepatan pada perangkat 192.168.88.203",
            "remove_limit",
            "192.168.88.203",
            None,
        ),
        (
            "Tutup akses komunikasi internet komputer 192.168.88.204",
            "block_traffic",
            "192.168.88.204",
            None,
        ),
        (
            "Blokir trafik data dari host 192.168.88.205",
            "block_traffic",
            "192.168.88.205",
            None,
        ),
        (
            "Buka kembali blokir firewall untuk 192.168.88.206",
            "unblock_traffic",
            "192.168.88.206",
            None,
        ),
        (
            "Pulihkan akses koneksi yang diblokir untuk 192.168.88.207",
            "unblock_traffic",
            "192.168.88.207",
            None,
        ),
    ]

    for text, exp_intent, exp_target, exp_rate in cases:
        res = parse_intent(text)
        assert res["intent"] == exp_intent, f"Intent mismatch for '{text}': got {res['intent']}, expected {exp_intent}"
        assert res["entities"]["target"] == exp_target, f"Target mismatch: got {res['entities']['target']}, expected {exp_target}"
        if exp_rate is not None:
            assert res["entities"]["rate"] == exp_rate, f"Rate mismatch: got {res['entities']['rate']}, expected {exp_rate}"
        assert res["policy"]["is_valid"], f"Policy invalid for '{text}': {res['policy']['error']}"
        assert res["confidence"] > 0.0, f"Confidence zero or invalid for '{text}'"

    print("      OK: 8 variasi kalimat unseen berhasil diparsing ke 4 intent.")


def test_entity_missing_errors():
    print("[2/5] Testing missing entity error handling...")
    # Kasus 1: Missing IP pada limit
    res_no_ip = parse_intent("Batasi bandwidth jadi 2 Mbps")
    assert res_no_ip["entities"]["target"] is None
    assert not res_no_ip["policy"]["is_valid"]
    assert "Target IP cannot be empty" in res_no_ip["policy"]["error"]

    # Kasus 2: Missing Rate pada limit
    res_no_rate = parse_intent("Batasi bandwidth 192.168.88.50")
    assert res_no_rate["entities"]["rate"] is None
    assert not res_no_rate["policy"]["is_valid"]
    assert "Parameter rate wajib diisi" in res_no_rate["policy"]["error"]

    # Kasus 3: Missing IP pada block
    res_block_no_ip = parse_intent("Blokir koneksi internet")
    assert res_block_no_ip["entities"]["target"] is None
    assert not res_block_no_ip["policy"]["is_valid"]

    print("      OK: Validasi kegagalan parsing saat entitas IP/Rate absen terverifikasi.")


def test_anti_lockout_via_nlp():
    print("[3/5] Testing anti-lockout safety via natural language...")
    res = parse_intent("Blokir internet 192.168.88.1")
    assert res["intent"] == "block_traffic"
    assert res["entities"]["target"] == "192.168.88.1"
    assert not res["policy"]["is_valid"]
    assert "Anti-lockout" in res["policy"]["error"]
    print("      OK: Proteksi anti-lockout tertahan di level NLP policy.")


def test_nlp_latency():
    print("[4/5] Testing NLP processing latency (< 5 ms)...")
    sample_text = "Batasi bandwidth IP 192.168.88.50 jadi 2 Mbps"
    # Warmup
    for _ in range(5):
        parse_intent(sample_text)
    latencies = []
    for _ in range(50):
        t0 = time.perf_counter()
        res = parse_intent(sample_text)
        elapsed = (time.perf_counter() - t0) * 1000.0
        latencies.append(elapsed)

    avg_ms = sum(latencies) / len(latencies)
    max_ms = max(latencies)
    assert avg_ms < 5.0, f"Rata-rata latensi >= 5 ms ({avg_ms:.2f} ms)"
    assert max_ms < 5.0, f"Maksimum latensi >= 5 ms ({max_ms:.2f} ms)"
    print(f"      OK: Rata-rata latensi {avg_ms:.3f} ms, Maksimum {max_ms:.3f} ms (< 5 ms).")


def test_live_router_nlp_execution():
    print("[5/5] Testing live router execution & clean rollback...")
    with MikroTikAdapter() as adapter:
        # Pre-cleanup
        adapter.remove_bandwidth_limit(DUMMY_IP)
        adapter.remove_firewall_block(DUMMY_IP)

        # 1. NLP -> Limit Bandwidth
        p_limit = parse_intent(f"Batasi bandwidth IP {DUMMY_IP} jadi 2 Mbps")
        assert p_limit["policy"]["is_valid"]
        res_limit = execute_policy(p_limit["policy"], adapter=adapter)
        assert res_limit["status"] == "success"
        queues = adapter.get_bandwidth_limits()
        assert any(q.get("target", "").split("/")[0] == DUMMY_IP for q in queues)
        print("      OK: Penerapan limit_bandwidth via teks sukses di router.")

        # 2. NLP -> Block Traffic
        p_block = parse_intent(f"Blokir trafik data dari host {DUMMY_IP}")
        assert p_block["policy"]["is_valid"]
        res_block = execute_policy(p_block["policy"], adapter=adapter)
        assert res_block["status"] == "success"
        fws = adapter.get_firewall_blocks()
        assert any(f.get("src-address", "").split("/")[0] == DUMMY_IP for f in fws)
        print("      OK: Penerapan block_traffic via teks sukses di router.")

        # 3. Clean Rollback -> Remove Limit
        p_unlimit = parse_intent(f"Cabut limit bandwidth untuk {DUMMY_IP}")
        assert p_unlimit["policy"]["is_valid"]
        res_unlimit = execute_policy(p_unlimit["policy"], adapter=adapter)
        assert res_unlimit["status"] == "success"

        # 4. Clean Rollback -> Unblock Traffic
        p_unblock = parse_intent(f"Buka blokir firewall {DUMMY_IP}")
        assert p_unblock["policy"]["is_valid"]
        res_unblock = execute_policy(p_unblock["policy"], adapter=adapter)
        assert res_unblock["status"] == "success"

        # 5. Verifikasi router bersih total
        rem_q = [q for q in adapter.get_bandwidth_limits() if q.get("target", "").split("/")[0] == DUMMY_IP]
        rem_fw = [f for f in adapter.get_firewall_blocks() if f.get("src-address", "").split("/")[0] == DUMMY_IP]
        assert len(rem_q) == 0, "Sisa queue masih ada setelah rollback"
        assert len(rem_fw) == 0, "Sisa firewall drop masih ada setelah rollback"
        print("      OK: Clean rollback tuntas, router kembali bersih.")


def run_all_tests():
    test_unseen_prompts()
    test_entity_missing_errors()
    test_anti_lockout_via_nlp()
    test_nlp_latency()
    test_live_router_nlp_execution()
    print("\nSEMUA PENGUJIAN FASE 3 SUKSES 100%!")


if __name__ == "__main__":
    run_all_tests()
