import subprocess
import sys

TEST_COMMANDS = [
    "help",
    "status",
    "Batasi bandwidth 192.168.88.250 jadi 2 Mbps",
    "status",
    "Cabut limit 192.168.88.250",
    "status",
    "keluar",
]


def run_test():
    print("[1/2] Menjalankan simulasi interaktif main_ibn.py via subprocess...")
    proc = subprocess.Popen(
        [sys.executable, "main_ibn.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    stdout, stderr = proc.communicate(input="\n".join(TEST_COMMANDS) + "\n")

    assert proc.returncode == 0, f"Process exited with error code {proc.returncode}: {stderr}"
    assert "SISTEM IBN MIKROTIK v6" in stdout, "Banner IBN tidak ditemukan di stdout"
    assert "PANDUAN PENGGUNAAN SISTEM IBN" in stdout, "Help menu tidak tampil"
    assert "STATUS AKTIF ROUTER MIKROTIK" in stdout, "Command status tidak berjalan"
    assert "limit_bandwidth" in stdout, "Intent limit_bandwidth tidak terpanggil"
    assert "qos_192.168.88.250" in stdout, "Policy name qos_192.168.88.250 tidak ditemukan"
    assert "remove_limit" in stdout, "Intent remove_limit tidak terpanggil"
    assert "Terima kasih telah menggunakan Sistem IBN MikroTik" in stdout, "Pesan exit tidak tampil"

    print("[2/2] Validasi respons teks & alur eksekusi...")
    print("      * Banner & Status Koneksi: OK")
    print("      * Perintah 'help' & panduan: OK")
    print("      * Perintah 'status' (Tabel Queue & FW): OK")
    print("      * Eksekusi Kalimat Alami (Limit Bandwidth): OK")
    print("      * Eksekusi Kalimat Alami (Cabut Limit): OK")
    print("      * Terminasi Anggun 'keluar': OK")
    print("\nSEMUA PENGUJIAN FASE 4 SUKSES 100%!")


if __name__ == "__main__":
    run_test()
