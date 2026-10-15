import time
from nlp_parser import parse_intent


def test_get_interface_ip():
    print("[1/4] Menguji parsing get_interface_ip (single, multi, global)...")

    # Single target
    for text in ["cek ip port 1", "cek jalur 1"]:
        res = parse_intent(text)
        assert res["intent"] == "get_interface_ip", f"Intent mismatch for '{text}': {res['intent']}"
        assert res["confidence"] == 1.0, f"Confidence mismatch for '{text}': {res['confidence']}"
        assert res["entities"]["target"] == "ether1", f"Entities target mismatch for '{text}': {res['entities']['target']}"
        assert res["policy"]["target"] == "ether1", f"Policy target mismatch for '{text}': {res['policy']['target']}"
        assert res["policy"]["is_valid"] is True, f"Policy invalid for '{text}': {res['policy']['error']}"

    # Multi target
    res_multi = parse_intent("cek ip port 1 dan port 3")
    assert res_multi["intent"] == "get_interface_ip", f"Intent mismatch: {res_multi['intent']}"
    assert res_multi["confidence"] == 1.0, f"Confidence mismatch: {res_multi['confidence']}"
    assert res_multi["entities"]["target"] == ["ether1", "ether3"], f"Entities target mismatch: {res_multi['entities']['target']}"
    assert res_multi["policy"]["target"] == ["ether1", "ether3"], f"Policy target mismatch: {res_multi['policy']['target']}"
    assert res_multi["policy"]["is_valid"] is True, f"Policy invalid: {res_multi['policy']['error']}"

    # Global target
    for text in ["cek semua ip", "cek seluruh ip"]:
        res_global = parse_intent(text)
        assert res_global["intent"] == "get_interface_ip", f"Intent mismatch: {res_global['intent']}"
        assert res_global["confidence"] == 1.0, f"Confidence mismatch: {res_global['confidence']}"
        assert res_global["entities"]["target"] is None, f"Entities target mismatch: {res_global['entities']['target']}"
        assert res_global["policy"]["target"] is None, f"Policy target mismatch: {res_global['policy']['target']}"
        assert res_global["policy"]["is_valid"] is True, f"Policy invalid: {res_global['policy']['error']}"

    print("      OK: Single ('ether1'), Multi (['ether1', 'ether3']), dan Global (None) terverifikasi valid.")


def test_add_ip_address():
    print("[2/4] Menguji parsing add_ip_address (CIDR penuh, auto prefix, normalisasi imbuhan)...")

    # CIDR penuh
    res1 = parse_intent("tambahkan ip 192.168.10.1/24 di port 3")
    assert res1["intent"] == "add_ip_address", f"Intent mismatch: {res1['intent']}"
    assert res1["confidence"] == 1.0, f"Confidence mismatch: {res1['confidence']}"
    assert res1["entities"]["target"] == "ether3", f"Target mismatch: {res1['entities']['target']}"
    assert res1["policy"]["target"] == "ether3", f"Policy target mismatch: {res1['policy']['target']}"
    assert res1["policy"]["address"] == "192.168.10.1/24", f"Policy address mismatch: {res1['policy']['address']}"
    assert res1["policy"]["is_valid"] is True, f"Policy invalid: {res1['policy']['error']}"

    # Auto prefix /24
    res2 = parse_intent("pasang ip 10.10.10.1 pada ether4")
    assert res2["intent"] == "add_ip_address", f"Intent mismatch: {res2['intent']}"
    assert res2["confidence"] == 1.0, f"Confidence mismatch: {res2['confidence']}"
    assert res2["entities"]["target"] == "ether4", f"Target mismatch: {res2['entities']['target']}"
    assert res2["policy"]["target"] == "ether4", f"Policy target mismatch: {res2['policy']['target']}"
    assert res2["policy"]["address"] == "10.10.10.1/24", f"Policy address mismatch: {res2['policy']['address']}"
    assert res2["policy"]["is_valid"] is True, f"Policy invalid: {res2['policy']['error']}"

    # Variasi normalisasi imbuhan terpisah ('tambah kan', 'pasang kan', 'masuk kan', 'beri kan')
    variations = [
        ("tambah kan ip 192.168.20.1/24 di port 2", "ether2", "192.168.20.1/24"),
        ("pasang kan ip 172.16.1.1/24 di jalur 3", "ether3", "172.16.1.1/24"),
        ("masuk kan ip 192.168.50.1/24 ke port 4", "ether4", "192.168.50.1/24"),
        ("beri kan ip 192.168.30.1 di jalur 3", "ether3", "192.168.30.1/24"),
    ]
    for prompt, exp_tgt, exp_addr in variations:
        res = parse_intent(prompt)
        assert res["intent"] == "add_ip_address", f"Intent mismatch for '{prompt}': {res['intent']}"
        assert res["policy"]["target"] == exp_tgt, f"Target mismatch for '{prompt}': {res['policy']['target']}"
        assert res["policy"]["address"] == exp_addr, f"Address mismatch for '{prompt}': {res['policy']['address']}"
        assert res["policy"]["is_valid"] is True, f"Policy invalid for '{prompt}': {res['policy']['error']}"

    print("      OK: CIDR penuh, auto prefix /24, dan normalisasi imbuhan terverifikasi valid.")


def test_anti_lockout_and_action_guard():
    print("[3/4] Menguji proteksi anti-lockout & penolakan kata aksi sampah (action guard)...")

    # Anti-lockout guard pada IP router manajemen (192.168.88.1)
    res_lockout = parse_intent("pasang ip 192.168.88.1 di port 3")
    assert res_lockout["intent"] == "add_ip_address", f"Intent mismatch: {res_lockout['intent']}"
    assert res_lockout["policy"]["is_valid"] is False, "Anti-lockout seharusnya menolak konfigurasi IP manajemen"
    assert "Anti-lockout" in res_lockout["policy"].get("error", ""), f"Pesan anti-lockout hilang: {res_lockout['policy'].get('error')}"

    # Action guard rejection pada gibberish
    res_gibberish = parse_intent("sdfsdnf port 1")
    assert res_gibberish["intent"] == "unknown", f"Intent seharusnya unknown, got: {res_gibberish['intent']}"
    assert res_gibberish["policy"]["is_valid"] is False, "Policy seharusnya invalid untuk teks gibberish"

    print("      OK: Proteksi Anti-lockout (192.168.88.1) dan Action Guard ('sdfsdnf port 1') aktif.")


def test_parsing_latency():
    print("[4/4] Menguji latensi pemrosesan parsing NLP (< 2 ms)...")

    test_prompts = [
        "cek ip port 1",
        "cek ip port 1 dan port 3",
        "cek semua ip",
        "tambahkan ip 192.168.10.1/24 di port 3",
        "pasang ip 10.10.10.1 pada ether4",
    ]

    # Warmup
    for p in test_prompts:
        parse_intent(p)

    n_iterations = 200
    t0 = time.perf_counter()
    for _ in range(n_iterations):
        for p in test_prompts:
            parse_intent(p)
    total_calls = n_iterations * len(test_prompts)
    elapsed_total = time.perf_counter() - t0
    avg_latency_ms = (elapsed_total / total_calls) * 1000.0

    assert avg_latency_ms < 2.0, f"Rata-rata latensi parsing melebihi 2 ms: {avg_latency_ms:.4f} ms"
    print(f"      OK: Rata-rata latensi parsing = {avg_latency_ms:.4f} ms (< 2 ms pada {total_calls} evaluasi).")


if __name__ == "__main__":
    print("=" * 65)
    print("  PENGUJIAN FASE 4: PARSER MULTI-TARGET & IP TELEMETRY")
    print("=" * 65)
    test_get_interface_ip()
    test_add_ip_address()
    test_anti_lockout_and_action_guard()
    test_parsing_latency()
    print("=" * 65)
    print("  SEMUA PENGUJIAN FASE 4 IP & TELEMETRY BERHASIL (100% PASS)")
    print("=" * 65)
