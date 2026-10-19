"""
Curate Tahap 1: Injeksi Blokir Situs Web (TLS-Host) & Pembersihan Massal (Bulk Clean-up)
Menyuntikkan variasi baru ke dataset_intent.json dengan menjaga total 980 sampel (14 kelas x 70 sampel seimbang)
dan melatih ulang model TF-IDF Logistic Regression.
"""

import json
from collections import Counter
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATASET_PATH = Path(__file__).parent / "dataset_intent.json"
MODEL_PATH = Path(__file__).parent / "intent_model.joblib"

# New samples to inject into existing classes
NEW_SAMPLES_TAHAP1 = {
    "block_traffic": [
        "blokir akses situs youtube.com",
        "tutup akses domain tiktok.com untuk lab",
        "cekal website judi.online",
        "blokir web facebook.com pada jaringan",
        "jangan izinkan pengguna membuka instagram.com",
        "cegat akses situs kompas.com",
        "blokir domain judi.com",
    ],
    "unblock_traffic": [
        "buka blokir situs youtube.com",
        "izinkan kembali web tiktok.com",
        "lepas pencekalan domain kompas.com",
        "buka blokir website instagram.com",
        "buka semua pemblokiran internet di router",
        "hapus semua aturan blokir firewall",
        "bersihkan daftar drop rule firewall",
    ],
    "remove_limit": [
        "hapus semua antrean limit bandwidth",
        "bersihkan seluruh limit kecepatan",
        "normalkan bandwidth semua komputer di lab",
        "cabut semua pembatasan kecepatan router",
        "unlimit semua antrean bandwidth",
        "hapus seluruh aturan simple queue",
    ],
    "disable_nat": [
        "hapus semua konfigurasi nat router",
        "bersihkan seluruh aturan masquerade",
        "cabut semua konfigurasi nat wan",
        "reset aturan nat router",
    ],
}


def curate_and_retrain():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Total dataset awal: {len(data)} sampel.")

    # Injeksi dengan menggantikan sampel yang redundan pada kelas terkait
    # ponytail: replace last N repetitive samples in each target class
    curated_data = []
    
    # Kelompokkan data per intent
    from collections import defaultdict
    intent_items = defaultdict(list)
    for item in data:
        intent_items[item["intent"]].append(item["text"])

    for intent, items in intent_items.items():
        if intent in NEW_SAMPLES_TAHAP1:
            replacements = NEW_SAMPLES_TAHAP1[intent]
            n_replace = len(replacements)
            # Ambil item lama kecuali n_replace terakhir, lalu gabungkan dengan yang baru
            kept_items = items[:-n_replace]
            final_items = kept_items + replacements
            print(f"Class {intent:20}: replaced {n_replace} redundant items with new variations.")
            for t in final_items:
                curated_data.append({"text": t, "intent": intent})
        else:
            for t in items:
                curated_data.append({"text": t, "intent": intent})

    # Verifikasi total dan balance
    counts = Counter(item["intent"] for item in curated_data)
    for intent, count in counts.items():
        assert count == 70, f"Class {intent} has {count} samples, expected 70!"

    assert len(curated_data) == 980, f"Total samples {len(curated_data)} != 980!"
    print(f"Total dataset terverifikasi: {len(curated_data)} sampel (14 kelas seimbang x 70 sampel).")

    # Tulis ulang dataset
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(curated_data, f, indent=2, ensure_ascii=False)

    print("dataset_intent.json berhasil diperbarui!")

    # Retrain model
    texts = [item["text"] for item in curated_data]
    labels = [item["intent"] for item in curated_data]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(C=5.0, max_iter=1000, random_state=42)),
    ])
    pipeline.fit(texts, labels)
    joblib.dump(pipeline, MODEL_PATH, compress=6)
    print(f"Model berhasil dilatih ulang dan disimpan ke {MODEL_PATH.name} ({MODEL_PATH.stat().st_size / 1024:.2f} KB).")


if __name__ == "__main__":
    curate_and_retrain()
