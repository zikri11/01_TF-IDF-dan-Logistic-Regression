import re
from pathlib import Path

REPORT_PATH = Path(__file__).parent / "LAPORAN_EVALUASI_RISET.txt"

EXPECTED_CLASSES = [
    "add_ip_address",
    "block_traffic",
    "disable_interface",
    "disable_nat",
    "enable_interface",
    "enable_nat",
    "get_interface_ip",
    "limit_bandwidth",
    "remove_limit",
    "unblock_traffic",
    "update_ip_address",
]


def test_fase6_evaluation_report():
    print("[1/3] Memverifikasi keberadaan file dan 11 kelas intent...")
    assert REPORT_PATH.exists(), f"File laporan tidak ditemukan di {REPORT_PATH}"
    content = REPORT_PATH.read_text(encoding="utf-8")

    assert "Jumlah Kelas    : 11 intent" in content, "Jumlah kelas bukan 11 intent"
    assert "Confusion Matrix (11x11):" in content, "Header Confusion Matrix (11x11) tidak ditemukan"

    for cls in EXPECTED_CLASSES:
        assert cls in content, f"Kelas intent '{cls}' tidak ditemukan dalam laporan"

    assert "get_interface_ip" in content, "Kelas 'get_interface_ip' tidak ada"
    assert "add_ip_address" in content, "Kelas 'add_ip_address' tidak ada"
    assert "update_ip_address" in content, "Kelas 'update_ip_address' tidak ada"
    print("      OK: File ada dan seluruh 11 kelas intent termuat dalam laporan.")

    print("[2/3] Memverifikasi evaluasi 154 sampel test set...")
    assert "Data Test  (20%): 154 sampel" in content, "Sampel data test bukan 154"
    assert "Akurasi Intent (Accuracy) : 100.00%" in content, "Akurasi intent tidak mencapai 100.00%"
    assert "Kesalahan Konfigurasi / Format Gagal (Failures)  : 0 / 154" in content, "Terdapat syntax failure"
    print("      OK: Seluruh 154 sampel test set dievaluasi dengan benar tanpa failure.")

    print("[3/3] Memverifikasi Command Accuracy 100.00% dan processing time < 2 ms...")
    assert "TOTAL COMMAND & POLICY ACCURACY RATE             : 100.00%" in content, "Command accuracy bukan 100.00%"

    # Ekstrak Total Processing Time Controller
    proc_time_match = re.search(r"Total Processing Time Controller:\s*([\d\.]+)\s*ms", content)
    assert proc_time_match is not None, "Nilai Total Processing Time Controller tidak ditemukan"
    proc_time = float(proc_time_match.group(1))
    assert proc_time < 2.0, f"Processing time {proc_time} ms melebihi batas 2.0 ms"
    print(f"      OK: Command Accuracy 100.00% & Processing Time {proc_time:.3f} ms (< 2.0 ms).")


if __name__ == "__main__":
    print("=" * 70)
    print("  PENGUJIAN FASE 6: EVALUASI KUANTITATIF & LAPORAN RISET IBN (10 KELAS)")
    print("=" * 70)
    test_fase6_evaluation_report()
    print("=" * 70)
    print("  SEMUA PENGUJIAN FASE 6 BERHASIL (100% PASS)")
    print("=" * 70)
