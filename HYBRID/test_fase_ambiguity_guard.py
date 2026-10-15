from nlp_parser import parse_intent, CONFIDENCE_THRESHOLD


def test_ambiguous_port_deletion():
    print("[1/4] Testing ambiguous physical port deletion rejection...")
    cases = [
        "hapus port 1",
        "hapus lan 2",
        "hapus eth 3",
        "cabut colokan 4",
        "hilangkan jalur 1",
        "buang int 2",
        "hapus iface 3",
        "delete kabel lan 4",
    ]

    for text in cases:
        res = parse_intent(text)
        assert res["intent"] == "unknown", f"Harusnya intent unknown untuk '{text}', got: {res['intent']}"
        assert not res["policy"]["is_valid"], f"Harusnya policy tidak valid untuk '{text}'"
        assert "Port fisik" in res["policy"]["error"], f"Pesan error tidak edukatif untuk '{text}': {res['policy']['error']}"
        assert "tidak dapat dihapus dari hardware router" in res["policy"]["error"]

    print("      OK: Seluruh perintah hapus port fisik ditolak edukatif dan aman.")


def test_ambiguous_general_deletion():
    print("[2/4] Testing ambiguous deletion without specific object...")
    cases = [
        ("hapus 192.168.88.50", "Harap tentukan konfigurasi untuk 192.168.88.50 yang ingin dihapus"),
        ("hapus", "Harap sebutkan konfigurasi spesifik yang ingin dihapus"),
        ("tolong bersihkan", "Harap sebutkan konfigurasi spesifik yang ingin dihapus"),
    ]

    for text, exp_msg in cases:
        res = parse_intent(text)
        assert res["intent"] == "unknown", f"Harusnya intent unknown untuk '{text}', got: {res['intent']}"
        assert not res["policy"]["is_valid"], f"Harusnya policy tidak valid untuk '{text}'"
        assert exp_msg in res["policy"]["error"], f"Pesan error tidak sesuai: {res['policy']['error']}"

    print("      OK: Hapus IP tanpa objek & hapus tanpa konteks ditolak secara presisi.")


def test_specific_deletion_routing():
    print("[3/4] Testing specific deletion commands (must succeed with conf=1.0)...")
    cases = [
        ("hapus limit port 1", "remove_limit", "ether1"),
        ("cabut limit kecepatan eth 2", "remove_limit", "ether2"),
        ("hapus ip 192.168.10.1 di port 3", "remove_ip_address", "ether3"),
        ("hapus ip pada lan 4", "remove_ip_address", "ether4"),
        ("hapus blokir port 80", "unblock_traffic", None),
        ("cabut blokir untuk 192.168.88.50", "unblock_traffic", "192.168.88.50/32"),
        ("cabut nat ether1", "disable_nat", "ether1"),
        ("matikan port 1", "disable_interface", "ether1"),
    ]

    for text, exp_intent, exp_target in cases:
        res = parse_intent(text)
        assert res["intent"] == exp_intent, f"Intent mismatch for '{text}': got {res['intent']}, expected {exp_intent}"
        assert res["confidence"] == 1.0, f"Confidence not 1.0 for '{text}': {res['confidence']}"
        assert res["policy"]["is_valid"], f"Policy invalid for '{text}': {res['policy'].get('error')}"
        if exp_target:
            assert res["policy"]["target"] == exp_target, f"Target mismatch for '{text}': {res['policy']['target']}"

    print("      OK: Seluruh penghapusan spesifik berhasil diarahkan ke intent yang benar (100% confidence).")


def test_confidence_threshold_guard():
    print("[4/4] Testing confidence threshold guard (< 50% must be rejected)...")
    assert CONFIDENCE_THRESHOLD == 0.50, f"Confidence threshold mismatch: {CONFIDENCE_THRESHOLD}"

    # Kalimat dengan confidence rendah harus ditolak
    res = parse_intent("hapus port 1")
    assert res["intent"] == "unknown"
    assert not res["policy"]["is_valid"]

    print("      OK: Confidence threshold guard terverifikasi aktif (ambang batas 50%).")


def main():
    print("=" * 70)
    print("  PENGUJIAN AMBIGUITY & CONFIDENCE THRESHOLD GUARD")
    print("=" * 70)
    test_ambiguous_port_deletion()
    test_ambiguous_general_deletion()
    test_specific_deletion_routing()
    test_confidence_threshold_guard()
    print("=" * 70)
    print("  SEMUA PENGUJIAN AMBIGUITY GUARD BERHASIL 100%!")
    print("=" * 70)


if __name__ == "__main__":
    main()
