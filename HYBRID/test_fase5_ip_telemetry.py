import io
import subprocess
import sys
from contextlib import redirect_stdout
from mikrotik_adapter import MikroTikAdapter
from main_ibn import handle_input_intent, show_status, show_help


def test_handle_input_intent_single_ip(adapter: MikroTikAdapter):
    print("[1/6] Menguji handle_input_intent 'cek ip port 1'...")
    buf = io.StringIO()
    with redirect_stdout(buf):
        handle_input_intent("cek ip port 1", adapter)
    output = buf.getvalue()

    assert "get_interface_ip" in output, "Intent get_interface_ip tidak ditemukan"
    assert "Entitas Iface: ether1" in output, "Entitas Iface ether1 tidak tampil di Panel 1"
    assert "Interface   : ether1" in output, "Interface ether1 tidak tampil di Panel 2"
    assert "SUKSES" in output, "Status SUKSES tidak ditemukan di Panel 3"
    assert "IP Address Terpasang" in output, "Header table card IP tidak ditemukan di Panel 3"
    assert "ether1" in output, "Data ether1 tidak ditemukan di table card"
    assert ("Connected (Up)" in output or "Unplugged (Down)" in output), "Link status tidak valid"
    print("      OK: Telemetry single interface ('ether1') terformat dengan benar.")


def test_handle_input_intent_multi_ip(adapter: MikroTikAdapter):
    print("[2/6] Menguji handle_input_intent 'cek ip port 1 dan port 3'...")
    buf = io.StringIO()
    with redirect_stdout(buf):
        handle_input_intent("cek ip port 1 dan port 3", adapter)
    output = buf.getvalue()

    assert "get_interface_ip" in output, "Intent get_interface_ip tidak ditemukan"
    assert "Entitas Iface: ether1, ether3" in output, "Entitas Iface multi tidak tampil di Panel 1"
    assert "Interface   : ether1, ether3" in output, "Interface multi tidak tampil di Panel 2"
    assert "SUKSES" in output, "Status SUKSES tidak ditemukan di Panel 3"
    assert "ether1" in output and "ether3" in output, "ether1 dan ether3 harus ada di table card"
    print("      OK: Telemetry multi interface ('ether1, ether3') terformat dengan benar.")


def test_handle_input_intent_all_ip(adapter: MikroTikAdapter):
    print("[3/6] Menguji handle_input_intent 'cek semua ip'...")
    buf = io.StringIO()
    with redirect_stdout(buf):
        handle_input_intent("cek semua ip", adapter)
    output = buf.getvalue()

    assert "get_interface_ip" in output, "Intent get_interface_ip tidak ditemukan"
    assert "SUKSES" in output, "Status SUKSES tidak ditemukan di Panel 3"
    assert "IP Address Terpasang" in output, "Header table card IP tidak ditemukan di Panel 3"
    assert "ether1" in output and "ether2" in output, "Seluruh interface router harus tampil di table card"
    print("      OK: Telemetry seluruh interface router terformat dengan benar.")


def test_handle_input_intent_add_and_rollback(adapter: MikroTikAdapter):
    print("[4/6] Menguji handle_input_intent 'tambahkan ip 10.10.10.1/24 di port 3' & rollback...")
    # Pre-cleanup
    adapter.remove_ip_address("10.10.10.1/24", "ether3")

    # 1. Tambah IP
    buf = io.StringIO()
    with redirect_stdout(buf):
        handle_input_intent("tambahkan ip 10.10.10.1/24 di port 3", adapter)
    output = buf.getvalue()

    assert "add_ip_address" in output, "Intent add_ip_address tidak ditemukan"
    assert "Entitas Addr: 10.10.10.1/24" in output, "Entitas Addr tidak tampil di Panel 1"
    assert "Entitas Iface: ether3" in output, "Entitas Iface tidak tampil di Panel 1"
    assert "IP Address  : 10.10.10.1/24" in output, "IP Address tidak tampil di Panel 2"
    assert "Interface   : ether3" in output, "Interface tidak tampil di Panel 2"
    assert "Aksi Router : added" in output, "Aksi Router 'added' tidak tampil di Panel 3"
    assert "Rule ID     :" in output, "Rule ID tidak tampil di Panel 3"
    assert "Interface   : ether3" in output, "Interface tidak tampil di Panel 3"
    assert "Alamat IP   : 10.10.10.1/24" in output, "Alamat IP tidak tampil di Panel 3"
    assert "Comment     : IBN_IP" in output, "Comment tidak tampil di Panel 3"
    assert "SUKSES" in output, "Status SUKSES tidak ditemukan"

    # 2. Uji Idempotensi (noop)
    buf_noop = io.StringIO()
    with redirect_stdout(buf_noop):
        handle_input_intent("tambahkan ip 10.10.10.1/24 di port 3", adapter)
    output_noop = buf_noop.getvalue()
    assert "Aksi Router : noop" in output_noop, "Aksi Router 'noop' tidak tampil saat duplikasi"

    # 3. Rollback remove_ip_address
    res_rem = adapter.remove_ip_address("10.10.10.1/24", "ether3")
    assert res_rem.get("action") == "removed", f"Rollback gagal: {res_rem}"
    remaining = adapter.get_ip_addresses("ether3")
    assert not any("10.10.10.1" in r.get("address", "") for r in remaining), "IP belum terhapus sempurna"

    print("      OK: Penambahan IP, respons Panel 1/2/3, idempotensi (noop), dan rollback sukses.")


def test_show_status_and_help(adapter: MikroTikAdapter):
    print("[5/6] Menguji show_status (5 tabel) dan show_help (seksi 7 & 8)...")

    # show_status
    buf_status = io.StringIO()
    with redirect_stdout(buf_status):
        show_status(adapter)
    out_status = buf_status.getvalue()

    assert "[1] Simple Queue Aktif" in out_status, "Tabel 1 tidak tampil"
    assert "[2] Firewall Filter Drop Aktif" in out_status, "Tabel 2 tidak tampil"
    assert "[3] Firewall NAT Masquerade Aktif" in out_status, "Tabel 3 tidak tampil"
    assert "[4] Interface Status Router" in out_status, "Tabel 4 tidak tampil"
    assert "[5] IP Address Assignment Router" in out_status, "Tabel 5 tidak tampil"
    for col in ["No", "ID", "Interface", "Address / Subnet", "Network", "Status"]:
        assert col in out_status, f"Kolom '{col}' tidak ditemukan di tabel 5"

    # show_help
    buf_help = io.StringIO()
    with redirect_stdout(buf_help):
        show_help()
    out_help = buf_help.getvalue()

    assert "7. Cek / Inspeksi IP Interface (get_interface_ip):" in out_help, "Seksi 7 help tidak ada"
    assert "8. Penambahan IP Address (add_ip_address):" in out_help, "Seksi 8 help tidak ada"
    assert "cek ip port 1" in out_help, "Contoh 'cek ip port 1' tidak ada di help"
    assert "cek jalur 1" in out_help, "Contoh 'cek jalur 1' tidak ada di help"
    assert "cek ip port 1 dan port 3" in out_help, "Contoh 'cek ip port 1 dan port 3' tidak ada di help"
    assert "cek semua ip" in out_help, "Contoh 'cek semua ip' tidak ada di help"
    assert "tambahkan ip 192.168.10.1/24 di port 3" in out_help, "Contoh tambah ip port 3 tidak ada di help"
    assert "pasang ip 10.10.10.1 pada ether4" in out_help, "Contoh pasang ip ether4 tidak ada di help"

    print("      OK: show_status memuat 5 tabel lengkap & show_help memuat seksi 7 & 8.")


def test_interactive_cli_simulation():
    print("[6/6] Menjalankan simulasi interaktif main_ibn.py via subprocess...")
    test_inputs = [
        "help",
        "status",
        "cek ip port 1",
        "cek ip port 1 dan port 3",
        "cek semua ip",
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
    stdout, stderr = proc.communicate(input="\n".join(test_inputs) + "\n", timeout=60)
    assert proc.returncode == 0, f"Process return code {proc.returncode}: {stderr}"
    assert "[5] IP Address Assignment Router" in stdout, "Tabel 5 tidak tampil di CLI status"
    assert "7. Cek / Inspeksi IP Interface" in stdout, "Seksi 7 help tidak ada di CLI help"
    assert "8. Penambahan IP Address" in stdout, "Seksi 8 help tidak ada di CLI help"
    assert "IP Address Terpasang" in stdout, "Table card telemetry tidak ada di CLI"
    assert "Terima kasih telah menggunakan Sistem IBN MikroTik" in stdout, "Exit pesan tidak ada"
    print("      OK: CLI interaktif main_ibn.py sukses end-to-end.")


if __name__ == "__main__":
    print("=" * 70)
    print("  PENGUJIAN FASE 5: TAMPILAN TELEMETRY CLI INTERAKTIF IP ADDRESS")
    print("=" * 70)
    with MikroTikAdapter() as adapter:
        test_handle_input_intent_single_ip(adapter)
        test_handle_input_intent_multi_ip(adapter)
        test_handle_input_intent_all_ip(adapter)
        test_handle_input_intent_add_and_rollback(adapter)
        test_show_status_and_help(adapter)
    test_interactive_cli_simulation()
    print("=" * 70)
    print("  SEMUA PENGUJIAN FASE 5 BERHASIL (100% PASS)")
    print("=" * 70)
