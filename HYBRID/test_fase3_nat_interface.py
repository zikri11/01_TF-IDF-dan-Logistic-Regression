from pathlib import Path
import time
from nlp_parser import parse_intent, MODEL_PATH, MODEL


def test_unseen_prompts_accuracy():
    print("[1/3] Testing accuracy on unseen prompts across 8 intent classes...")
    cases = [
        # (text, expected_intent, expected_target)
        (
            "Tolong pasang limit kecepatan client 10.0.0.5 ke 3 Mbps",
            "limit_bandwidth",
            "10.0.0.5/32",
        ),
        (
            "Batasin kecepatan internet user 192.168.88.201 hingga 512k",
            "limit_bandwidth",
            "192.168.88.201/32",
        ),
        (
            "Hilangkan batasan bandwidth untuk laptop 10.0.0.7",
            "remove_limit",
            "10.0.0.7/32",
        ),
        (
            "Cabut pembatasan kecepatan pada perangkat 192.168.88.203",
            "remove_limit",
            "192.168.88.203/32",
        ),
        (
            "Tutup akses komunikasi internet komputer 10.0.0.9",
            "block_traffic",
            "10.0.0.9/32",
        ),
        (
            "Blokir trafik data dari host 192.168.88.205",
            "block_traffic",
            "192.168.88.205/32",
        ),
        (
            "Buka kembali blokir firewall untuk 10.0.0.11",
            "unblock_traffic",
            "10.0.0.11/32",
        ),
        (
            "Pulihkan akses koneksi yang diblokir untuk 192.168.88.207",
            "unblock_traffic",
            "192.168.88.207/32",
        ),
        (
            "Aktifkan interface ether4",
            "enable_interface",
            "ether4",
        ),
        (
            "Hidupkan kembali port 3 mikrotik",
            "enable_interface",
            "ether3",
        ),
        (
            "Matikan interface ether4",
            "disable_interface",
            "ether4",
        ),
        (
            "Nonaktifkan port 3 mikrotik",
            "disable_interface",
            "ether3",
        ),
        (
            "Aktifkan fitur NAT masquerade untuk internet",
            "enable_nat",
            "ether1",
        ),
        (
            "Tolong nyalakan NAT masquerade pada ether1",
            "enable_nat",
            "ether1",
        ),
        (
            "Matikan fitur NAT masquerade untuk internet",
            "disable_nat",
            "ether1",
        ),
        (
            "Tolong cabut NAT masquerade pada ether1",
            "disable_nat",
            "ether1",
        ),
    ]

    for text, exp_intent, exp_target in cases:
        res = parse_intent(text)
        assert res["intent"] == exp_intent, (
            f"Intent mismatch for '{text}': got {res['intent']}, expected {exp_intent}"
        )
        assert res["policy"]["target"] == exp_target, (
            f"Target mismatch for '{text}': got {res['policy']['target']}, expected {exp_target}"
        )
        assert res["policy"]["is_valid"], (
            f"Policy invalid for '{text}': {res['policy'].get('error')}"
        )
        assert res["confidence"] > 0.0, f"Confidence zero or invalid for '{text}'"

    print(f"      OK: 16 unseen prompts berhasil diparsing akurat ke 8 kelas intent.")


def test_model_size():
    print("[2/3] Testing serialized model file size (< 60 KB)...")
    assert MODEL_PATH.exists(), f"Model file not found: {MODEL_PATH}"
    size_kb = MODEL_PATH.stat().st_size / 1024.0
    print(f"      Model file size: {size_kb:.2f} KB")
    assert size_kb < 60.0, f"Model size exceeds limit: {size_kb:.2f} KB >= 60.0 KB"
    print("      OK: Ukuran model memenuhi syarat ultra-ringan (< 60 KB).")


def test_prediction_latency():
    print("[3/3] Testing prediction latency (< 2 ms)...")
    sample_text = "Aktifkan interface ether4"

    # Warmup
    for _ in range(10):
        MODEL.predict([sample_text])
        parse_intent(sample_text)

    latencies_model = []
    latencies_parser = []
    for _ in range(100):
        t0 = time.perf_counter()
        MODEL.predict([sample_text])
        latencies_model.append((time.perf_counter() - t0) * 1000.0)

        t1 = time.perf_counter()
        parse_intent(sample_text)
        latencies_parser.append((time.perf_counter() - t1) * 1000.0)

    avg_model_ms = sum(latencies_model) / len(latencies_model)
    avg_parser_ms = sum(latencies_parser) / len(latencies_parser)
    max_model_ms = max(latencies_model)

    print(f"      Avg model latency : {avg_model_ms:.3f} ms (max: {max_model_ms:.3f} ms)")
    print(f"      Avg parser latency: {avg_parser_ms:.3f} ms")

    assert avg_model_ms < 2.0, f"Avg model latency >= 2 ms: {avg_model_ms:.3f} ms"
    assert avg_parser_ms < 2.0, f"Avg parser latency >= 2 ms: {avg_parser_ms:.3f} ms"
    print("      OK: Latensi prediksi terverifikasi ultra-cepat (< 2 ms).")


def run_all():
    test_unseen_prompts_accuracy()
    test_model_size()
    test_prediction_latency()
    print("\nSEMUA PENGUJIAN FASE 3 (NAT & INTERFACE NLP) SUKSES 100%!")


if __name__ == "__main__":
    run_all()
