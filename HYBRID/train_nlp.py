import json
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATASET_PATH = Path(__file__).parent / "dataset_intent.json"
MODEL_PATH = Path(__file__).parent / "intent_model.joblib"


def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(C=5.0, max_iter=1000, random_state=42)),
    ])


def main():
    print("=" * 60)
    print("  IBN NLP INTENT CLASSIFIER - TRAINING & EVALUASI")
    print("=" * 60)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = [item["text"] for item in data]
    labels = [item["intent"] for item in data]
    classes = sorted(list(set(labels)))

    print(f"[*] Total dataset : {len(texts)} sampel")
    print(f"[*] Jumlah kelas  : {len(classes)} ({', '.join(classes)})")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, stratify=labels, random_state=42
    )
    print(f"[*] Pembagian data: Train = {len(X_train)} (80%), Test = {len(X_test)} (20%)")

    eval_model = build_pipeline()
    eval_model.fit(X_train, y_train)
    y_pred = eval_model.predict(X_test)

    print("\n" + "-" * 60)
    print("  METRIK EVALUASI AKADEMIS (TEST SET)")
    print("-" * 60)
    print(classification_report(y_test, y_pred, digits=4))

    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    header = f"{'True \\ Pred':<18} " + " ".join(f"{c:>15}" for c in classes)
    print(header)
    for i, row in enumerate(cm):
        row_str = " ".join(f"{val:>15}" for val in row)
        print(f"{classes[i]:<18} {row_str}")

    print("\n" + "-" * 60)
    print("  FINAL TRAINING & SERIALISASI MODEL")
    print("-" * 60)
    final_model = build_pipeline()
    final_model.fit(texts, labels)

    joblib.dump(final_model, MODEL_PATH, compress=3)
    file_size_kb = MODEL_PATH.stat().st_size / 1024

    print(f"[+] Model tersimpan : {MODEL_PATH.name}")
    print(f"[+] Ukuran file     : {file_size_kb:.2f} KB (Lightweight Footprint)")
    print("=" * 60)


if __name__ == "__main__":
    main()
