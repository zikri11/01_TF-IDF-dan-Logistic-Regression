import json
import time
from pathlib import Path
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

MODEL_PATH = Path(__file__).parent / "intent_model.joblib"
DATASET_PATH = Path(__file__).parent / "dataset_intent.json"


def run_benchmark(iterations: int = 1000):
    print("=" * 65)
    print("      BENCHMARK MODEL NLP INTENT CLASSIFIER (IBN)")
    print("=" * 65)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file tidak ditemukan di {MODEL_PATH}")

    model_size_kb = MODEL_PATH.stat().st_size / 1024
    t_load_start = time.perf_counter()
    model = joblib.load(MODEL_PATH)
    load_time_ms = (time.perf_counter() - t_load_start) * 1000

    tfidf = model.named_steps.get("tfidf")
    vocab_size = len(tfidf.vocabulary_) if tfidf else 0
    classes = list(model.classes_)

    print(f"[*] Lokasi Model       : {MODEL_PATH}")
    print(f"[*] Ukuran File        : {model_size_kb:.2f} KB")
    print(f"[*] Waktu Load Model   : {load_time_ms:.2f} ms")
    print(f"[*] Jumlah Kosakata    : {vocab_size} n-grams")
    print(f"[*] Daftar Kelas ({len(classes)}) : {', '.join(classes)}")

    if not DATASET_PATH.exists():
        print(f"\n[!] Dataset {DATASET_PATH.name} tidak ditemukan, lewati evaluasi metrik.")
        texts, labels = [], []
    else:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        texts = [d["text"] for d in data]
        labels = [d["intent"] for d in data]

    if texts:
        print("\n" + "-" * 65)
        print("  1. EVALUASI AKURASI & METRIK KLASIFIKASI")
        print("-" * 65)
        preds = model.predict(texts)
        acc = accuracy_score(labels, preds)
        print(f"Total Sampel Evaluasi : {len(texts)}")
        print(f"Akurasi Keseluruhan   : {acc * 100:.2f}%\n")
        print(classification_report(labels, preds, digits=4))

        print("Confusion Matrix:")
        cm = confusion_matrix(labels, preds, labels=classes)
        header = f"{'True \\ Pred':<18} " + " ".join(f"{c:>15}" for c in classes)
        print(header)
        for i, row in enumerate(cm):
            row_str = " ".join(f"{val:>15}" for val in row)
            print(f"{classes[i]:<18} {row_str}")

    print("\n" + "-" * 65)
    print("  2. PENGUJIAN LATENSI & THROUGHPUT (INFERENCE SPEED)")
    print("-" * 65)

    sample_query = "Batasi bandwidth IP 192.168.88.50 menjadi 2 Mbps"
    test_queries = texts[:100] if texts else [sample_query]

    # Cold start
    t0 = time.perf_counter()
    _ = model.predict([sample_query])
    cold_start_ms = (time.perf_counter() - t0) * 1000

    # Single-sample inference latency benchmark
    latencies = []
    for i in range(iterations):
        q = test_queries[i % len(test_queries)]
        t_start = time.perf_counter()
        _ = model.predict_proba([q])
        latencies.append((time.perf_counter() - t_start) * 1000)

    latencies = np.array(latencies)
    mean_lat = np.mean(latencies)
    median_lat = np.median(latencies)
    p95_lat = np.percentile(latencies, 95)
    p99_lat = np.percentile(latencies, 99)
    min_lat = np.min(latencies)
    max_lat = np.max(latencies)
    qps = 1000.0 / mean_lat if mean_lat > 0 else 0

    print(f"Jumlah Iterasi   : {iterations:,} kali")
    print(f"Cold Start       : {cold_start_ms:.3f} ms")
    print(f"Latency Mean     : {mean_lat:.3f} ms")
    print(f"Latency Median   : {median_lat:.3f} ms")
    print(f"Latency Min / Max: {min_lat:.3f} ms / {max_lat:.3f} ms")
    print(f"Latency P95      : {p95_lat:.3f} ms")
    print(f"Latency P99      : {p99_lat:.3f} ms")
    print(f"Throughput (QPS) : {qps:.1f} queries/detik")

    if texts:
        t_batch_start = time.perf_counter()
        _ = model.predict(texts)
        batch_total_ms = (time.perf_counter() - t_batch_start) * 1000
        batch_qps = len(texts) / (batch_total_ms / 1000.0)
        print(f"\nBatch Inference  : {len(texts)} sampel dalam {batch_total_ms:.2f} ms ({batch_qps:.1f} QPS)")

    print("=" * 65)


if __name__ == "__main__":
    run_benchmark()
