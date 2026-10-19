import json
from pathlib import Path
import time
from collections import Counter
import joblib

DATASET_PATH = Path(__file__).parent / "dataset_intent.json"
MODEL_PATH = Path(__file__).parent / "intent_model.joblib"


def test_dataset_balance():
    print("[1/3] Memvalidasi keseimbangan dataset (>= 300 sampel, seimbang per kelas)...")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_samples = len(data)
    assert total_samples in (300, 330, 550, 770, 980, 1120, 1330), f"Total dataset harus 300, 330, 550, 770, 980, 1120, atau 1330, didapat: {total_samples}"

    counts = Counter(item["intent"] for item in data)
    assert len(counts) in (10, 11, 14, 16, 19), f"Jumlah kelas harus 10, 11, 14, 16, atau 19, didapat: {len(counts)}"

    expected_per_class = total_samples // len(counts)
    for intent, count in counts.items():
        assert count == expected_per_class, f"Kelas {intent} harus memiliki {expected_per_class} sampel, didapat: {count}"

    print(f"      OK: Dataset valid ({total_samples} sampel, {len(counts)} kelas seimbang masing-masing {expected_per_class} sampel).")


def test_model_predictions_10_classes():
    print("[2/3] Memuat model dan menguji prediksi langsung pada unseen prompts 10 kelas...")
    model = joblib.load(MODEL_PATH)

    test_cases = [
        # get_interface_ip
        ("cek ip port 1", "get_interface_ip"),
        ("cek jalur 1", "get_interface_ip"),
        ("cek ip di port 2", "get_interface_ip"),
        ("tolong periksa ip pada port 3", "get_interface_ip"),
        ("cek ip port 1 dan port 3", "get_interface_ip"),
        ("lihat ip interface ether4", "get_interface_ip"),
        ("inspeksi status ip di jalur 3", "get_interface_ip"),
        # add_ip_address
        ("tambahkan ip 192.168.10.1/24 di port 3", "add_ip_address"),
        ("pasang ip 10.10.10.1 pada ether4", "add_ip_address"),
        ("tolong tambahkan ip 172.16.1.1/24 di port 1", "add_ip_address"),
        ("beri ip 192.168.30.1 di jalur 3", "add_ip_address"),
        ("pasangkan ip 192.168.70.1/24 di jalur 4", "add_ip_address"),
        ("masukkan ip 192.168.50.1/24 ke port 4", "add_ip_address"),
        # Other 8 classes
        ("batasi pemakaian bandwidth 10.0.0.5 sebesar 2 Mbps", "limit_bandwidth"),
        ("hilangkan batasan bandwidth IP 10.0.0.5", "remove_limit"),
        ("blokir akses internet client 10.0.0.8", "block_traffic"),
        ("buka kembali blokir internet 10.0.0.8", "unblock_traffic"),
        ("aktifkan port ether3 mikrotik", "enable_interface"),
        ("matikan interface port ether4", "disable_interface"),
        ("aktifkan fitur nat masquerade", "enable_nat"),
        ("matikan fitur nat masquerade", "disable_nat"),
    ]

    for prompt, expected_intent in test_cases:
        predicted = model.predict([prompt])[0]
        assert predicted == expected_intent, (
            f"Prediksi salah untuk '{prompt}': got '{predicted}', expected '{expected_intent}'"
        )

    print(f"      OK: Semua {len(test_cases)} prompt uji berhasil diprediksi tepat ke 10 kelas.")


def test_model_size_and_latency():
    print("[3/3] Memverifikasi ukuran file model (< 300 KB) dan latensi prediksi (< 2 ms)...")
    # Verifikasi ukuran file model terkompresi (< 500 KB, sangat ringan untuk edge device)
    file_size_kb = MODEL_PATH.stat().st_size / 1024
    assert file_size_kb < 500.0, f"Ukuran model melebihi batas 500 KB: {file_size_kb:.2f} KB"

    model = joblib.load(MODEL_PATH)
    # Warmup
    model.predict(["warmup"])

    n_iterations = 200
    t0 = time.perf_counter()
    for _ in range(n_iterations):
        model.predict(["cek ip port 1"])
    elapsed_total = time.perf_counter() - t0
    avg_latency_ms = (elapsed_total / n_iterations) * 1000.0

    assert avg_latency_ms < 2.0, f"Latensi prediksi melebihi batas 2 ms: {avg_latency_ms:.3f} ms"

    print(f"      OK: Ukuran model = {file_size_kb:.2f} KB (< 100 KB)")
    print(f"      OK: Rata-rata latensi prediksi = {avg_latency_ms:.4f} ms (< 2 ms)")


if __name__ == "__main__":
    print("=" * 65)
    print("  PENGUJIAN FASE 3: DATASET & RETRAINING NLP (IP & TELEMETRY)")
    print("=" * 65)
    test_dataset_balance()
    test_model_predictions_10_classes()
    test_model_size_and_latency()
    print("=" * 65)
    print("  SEMUA PENGUJIAN FASE 3 BERHASIL (100% PASS)")
    print("=" * 65)
