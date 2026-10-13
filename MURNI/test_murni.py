import subprocess
import sys
from pathlib import Path
import joblib
from nlp_parser_murni import parse_intent_murni, MODEL_PATH
from policy_engine import build_network_policy


def test_murni_model():
    print("[1/3] Testing Pure ML Model Artifact...")
    assert MODEL_PATH.exists(), f"Model {MODEL_PATH} tidak ditemukan!"
    model = joblib.load(MODEL_PATH)
    classes = list(model.classes_)
    assert len(classes) == 8, f"Expected 8 classes, got {len(classes)}"
    size_kb = MODEL_PATH.stat().st_size / 1024
    print(f"      OK: Model Murni termuat ({size_kb:.2f} KB), 8 kelas: {', '.join(classes)}")


def test_murni_parser():
    print("[2/3] Testing Pure ML Intent Parsing...")
    cases = [
        ("Batasi bandwidth IP 192.168.88.50 jadi 2 Mbps", "limit_bandwidth"),
        ("Blokir akses internet untuk 192.168.88.99", "block_traffic"),
        ("Aktifkan interface ether3", "enable_interface"),
        ("Matikan port 4", "disable_interface"),
        ("Enable masquerade ether1", "enable_nat"),
        ("Disable masquerade", "disable_nat"),
    ]
    for prompt, expected in cases:
        res = parse_intent_murni(prompt)
        assert res["intent"] == expected, f"Failed for '{prompt}': got {res['intent']}, expected {expected}"
        assert res["policy"]["is_valid"] is True
        print(f"      OK: '{prompt:<45}' -> {res['intent']} ({res['confidence']*100:.1f}%)")


def test_murni_cli_subprocess():
    print("[3/3] Testing Pure ML CLI (main_ibn.py) via subprocess...")
    proc = subprocess.Popen(
        [sys.executable, "main_ibn.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    stdout, stderr = proc.communicate(input="help\nkeluar\n", timeout=30)
    assert proc.returncode == 0
    assert "SISTEM IBN MIKROTIK v6 (BASELINE VERSI MURNI - PURE ML)" in stdout
    assert "PANDUAN PENGGUNAAN SISTEM IBN (VERSI MURNI)" in stdout
    assert "Terima kasih telah menggunakan Sistem IBN Versi Murni" in stdout
    print("      OK: CLI interaktif Versi Murni berjalan mulus tanpa error.")


if __name__ == "__main__":
    print("=" * 65)
    print("        VERIFIKASI INTEGRITAS PIPELINE VERSI MURNI")
    print("=" * 65)
    test_murni_model()
    test_murni_parser()
    test_murni_cli_subprocess()
    print("\nSEMUA PENGUJIAN VERSI MURNI SUKSES 100%!")
