import subprocess
import sys
from nlp_parser import parse_intent


def test_parsing_new_sentences():
    print("[1/2] Pengujian parsing NLP & ekstraksi entitas kalimat baru (Interface & NAT)...")

    cases = [
        # (text, expected_intent, expected_target, expected_valid)
        ("hidupkan wifi", "enable_interface", "wlan1", True),
        ("matikan wifi", "disable_interface", "wlan1", True),
        ("nyalakan port 4", "enable_interface", "ether4", True),
        ("matikan port 4", "disable_interface", "ether4", True),
        ("aktifkan nat internet", "enable_nat", "ether1", True),
        ("matikan nat internet", "disable_nat", "ether1", True),
        ("nonaktifkan port 3", "disable_interface", "ether3", True),
        ("hidupkan kembali port 3", "enable_interface", "ether3", True),
        ("pasang nat masquerade pada ether1", "enable_nat", "ether1", True),
        ("cabut nat masquerade pada ether1", "disable_nat", "ether1", True),
        ("matikan interface ether2", "disable_interface", "ether2", False),
        ("matikan port 2", "disable_interface", "ether2", False),
    ]

    for text, exp_intent, exp_target, exp_valid in cases:
        res = parse_intent(text)
        assert res["intent"] == exp_intent, (
            f"Intent mismatch for '{text}': got {res['intent']}, expected {exp_intent}"
        )
        assert res["entities"]["target"] == exp_target, (
            f"Target mismatch for '{text}': got {res['entities']['target']}, expected {exp_target}"
        )
        assert res["confidence"] == 1.0, (
            f"Confidence mismatch for '{text}': got {res['confidence']}, expected 1.0"
        )
        assert res["policy"]["is_valid"] == exp_valid, (
            f"Policy validity mismatch for '{text}': got {res['policy']['is_valid']}, expected {exp_valid}"
        )
        if not exp_valid:
            assert "Anti-lockout" in res["policy"].get("error", ""), (
                f"Pesan anti-lockout tidak muncul untuk '{text}': {res['policy'].get('error')}"
            )

    print("      OK: Semua 12 variasi kalimat Interface & NAT berhasil diparsing akurat (conf=1.0).")


def test_main_cli_simulation():
    print("[2/2] Menjalankan simulasi interaktif main_ibn.py via subprocess...")

    test_commands = [
        "help",
        "status",
        "nyalakan port 4",
        "matikan port 4",
        "nyalakan port 4",
        "aktifkan nat internet",
        "matikan nat internet",
        "status",
        "keluar",
    ]

    proc = subprocess.Popen(
        [sys.executable, "main_ibn.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    stdout, stderr = proc.communicate(input="\n".join(test_commands) + "\n", timeout=60)

    assert proc.returncode == 0, f"Process exit code {proc.returncode}: {stderr}"
    assert "SISTEM IBN MIKROTIK v6" in stdout, "Banner IBN tidak ditemukan di stdout"
    assert "PANDUAN PENGGUNAAN SISTEM IBN" in stdout, "Help menu tidak tampil"
    assert "Kontrol Interface" in stdout, "Panduan Interface tidak ditemukan di help"
    assert "NAT Masquerade" in stdout, "Panduan NAT tidak ditemukan di help"

    # Verifikasi 4 tabel status
    assert "[1] Simple Queue Aktif" in stdout, "Tabel 1 (Simple Queue) tidak tampil"
    assert "[2] Firewall Filter Drop Aktif" in stdout, "Tabel 2 (Firewall Filter) tidak tampil"
    assert "[3] Firewall NAT Masquerade Aktif" in stdout, "Tabel 3 (NAT) tidak tampil"
    assert "[4] Interface Status Router" in stdout, "Tabel 4 (Interface) tidak tampil"
    assert "Out-Interface" in stdout, "Header Out-Interface pada Tabel 3 tidak ditemukan"
    assert "Running" in stdout, "Header Running pada Tabel 4 tidak ditemukan"

    # Verifikasi eksekusi aksi interface & NAT
    assert "enable_interface" in stdout, "Intent enable_interface tidak tercatat"
    assert "disable_interface" in stdout, "Intent disable_interface tidak tercatat"
    assert "enable_nat" in stdout, "Intent enable_nat tidak tercatat"
    assert "disable_nat" in stdout, "Intent disable_nat tidak tercatat"
    assert "Interface   : ether4" in stdout, "Informasi respons Interface tidak tampil"
    assert "Out-Iface   : ether1" in stdout, "Informasi respons NAT tidak tampil"
    assert "SUKSES" in stdout, "Status eksekusi SUKSES tidak ditemukan"
    assert "Terima kasih telah menggunakan Sistem IBN MikroTik" in stdout, "Pesan keluar tidak tampil"

    print("      OK: Banner, help 6 domain, status 4 tabel, eksekusi Interface & NAT, serta exit sukses.")


def run_all():
    test_parsing_new_sentences()
    test_main_cli_simulation()
    print("\nSEMUA PENGUJIAN FASE 4 (PARSER & CLI INTERFACE + NAT) SUKSES 100%!")


if __name__ == "__main__":
    run_all()
