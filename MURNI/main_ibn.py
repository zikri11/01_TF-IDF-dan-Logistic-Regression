import os
import sys
import time
from pathlib import Path
from config import ROUTER_HOST
from mikrotik_adapter import MikroTikAdapter
from nlp_parser_murni import parse_intent_murni, MODEL_PATH
from policy_engine import execute_policy

if sys.platform == "win32":
    os.system("")

COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))

    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    head = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    lines = [sep, head, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row)) + " |")
    lines.append(sep)
    return "\n".join(lines)


def print_banner(connected: bool):
    status_str = f"{COLOR_GREEN}Terhubung{COLOR_RESET}" if connected else f"{COLOR_RED}Terputus{COLOR_RESET}"
    model_kb = int(MODEL_PATH.stat().st_size / 1024) if MODEL_PATH.exists() else 31
    print("=" * 80)
    print(f"{COLOR_BOLD}{COLOR_CYAN}         SISTEM IBN MIKROTIK v6 (BASELINE VERSI MURNI - PURE ML){COLOR_RESET}")
    print(f" Router: {ROUTER_HOST} | Status: {status_str} | Model: Pure TF-IDF+LogReg ({model_kb} KB)")
    print(" (Catatan: Model murni tanpa syntactic cue overrides atau morphological join)")
    print("=" * 80)


def show_status(adapter: MikroTikAdapter):
    print(f"\n{COLOR_BOLD}{COLOR_CYAN}=== STATUS AKTIF ROUTER MIKROTIK ==={COLOR_RESET}")
    try:
        queues = adapter.get_bandwidth_limits()
        print(f"\n[1] Simple Queue Aktif ({len(queues)} rule):")
        if queues:
            rows = []
            for idx, q in enumerate(queues, 1):
                rows.append([
                    str(idx),
                    q.get(".id", "-"),
                    q.get("name", "-"),
                    q.get("target", "-"),
                    q.get("max-limit", "-"),
                ])
            print(format_table(["No", "ID", "Nama", "Target", "Max Limit"], rows))
        else:
            print("    (Tidak ada antrean Simple Queue aktif)")

        fws = adapter.get_firewall_blocks()
        print(f"\n[2] Firewall Filter Drop Aktif ({len(fws)} rule):")
        if fws:
            rows = []
            for idx, f in enumerate(fws, 1):
                rows.append([
                    str(idx),
                    f.get(".id", "-"),
                    f.get("chain", "-"),
                    f.get("src-address", "-"),
                    str(f.get("dst-port", "-")),
                    f.get("protocol", "-"),
                    f.get("action", "-"),
                    f.get("comment", "-"),
                ])
            print(format_table(["No", "ID", "Chain", "Src Address", "Dst Port", "Proto", "Action", "Comment"], rows))
        else:
            print("    (Tidak ada firewall filter drop rule aktif)")

        nats = adapter.get_nat_rules()
        print(f"\n[3] Firewall NAT Masquerade Aktif ({len(nats)} rule):")
        if nats:
            rows = []
            for idx, n in enumerate(nats, 1):
                status_str = "Disabled" if n.get("disabled") in (True, "true") else "Enabled"
                rows.append([
                    str(idx),
                    n.get(".id", "-"),
                    n.get("chain", "-"),
                    n.get("action", "-"),
                    n.get("out-interface") or n.get("out-interface-list") or "-",
                    n.get("comment", "-"),
                    status_str,
                ])
            print(format_table(["No", "ID", "Chain", "Action", "Out Interface", "Comment", "Status"], rows))
        else:
            print("    (Tidak ada NAT rule aktif)")

        ifaces = adapter.get_interface_states()
        print(f"\n[4] Interface Status Router ({len(ifaces)} interface):")
        if ifaces:
            rows = []
            for idx, i in enumerate(ifaces, 1):
                status_str = "DOWN / Disabled" if i.get("disabled") in (True, "true") else "UP / Active"
                running_str = "Yes" if i.get("running") in (True, "true") else "No"
                rows.append([
                    str(idx),
                    i.get(".id", "-"),
                    i.get("name", "-"),
                    i.get("type", "-"),
                    status_str,
                    running_str,
                ])
            print(format_table(["No", "ID", "Nama", "Tipe", "Status", "Running"], rows))
        else:
            print("    (Tidak ada interface terdeteksi)")
        print()
    except Exception as e:
        print(f"{COLOR_RED}Gagal mengambil status router: {e}{COLOR_RESET}\n")


def show_help():
    print(f"""
{COLOR_BOLD}{COLOR_CYAN}=== PANDUAN PENGGUNAAN SISTEM IBN (VERSI MURNI) ==={COLOR_RESET}
Sistem versi Murni mengandalkan 100% probabilitas statistik Machine Learning
(TF-IDF + Logistic Regression) tanpa bantuan aturan sintaksis penimpa.

{COLOR_BOLD}Contoh Perintah Alami:{COLOR_RESET}
 1. Batasi Bandwidth (limit_bandwidth):
    * "Batasi bandwidth 192.168.88.250 jadi 2 Mbps"
    * "Limit kecepatan internet user 192.168.88.100 ke 512 kbps"
    * "saya ingin port 3 kasih limit 5mb"

 2. Cabut Pembatasan (remove_limit):
    * "Cabut limit 192.168.88.250"
    * "Hapus pembatasan bandwidth untuk 192.168.88.100"

 3. Blokir Trafik (block_traffic):
    * "Blokir akses internet 192.168.88.250"
    * "blokir port 80 untuk 192.168.88.50"
    * "blokir port 443"

 4. Buka Blokir (unblock_traffic):
    * "Buka blokir 192.168.88.250"
    * "buka blokir port 80 untuk 192.168.88.50"

 5. Kontrol Interface Fisik:
    * "aktifkan interface ether3"
    * "matikan port 4"

 6. Kontrol NAT Masquerade:
    * "aktifkan fitur nat masquerade"
    * "matikan fitur nat masquerade"

{COLOR_BOLD}Perintah Sistem Khusus:{COLOR_RESET}
 * status / cek   : Menampilkan 4 tabel status router
 * bantuan / help : Menampilkan panduan contoh kalimat ini
 * clear / cls    : Membersihkan layar terminal
 * keluar / exit  : Keluar dari program
""")


def handle_input_intent(text: str, adapter: MikroTikAdapter):
    t_start = time.perf_counter()
    parsed = parse_intent_murni(text)
    policy = parsed.get("policy", {})

    print("-" * 80)
    print(f"{COLOR_BOLD}[1] Analisis NLP (Pure Machine Learning):{COLOR_RESET}")
    print(f"    Intent      : {COLOR_CYAN}{parsed['intent']}{COLOR_RESET}")
    print(f"    Keyakinan   : {parsed['confidence'] * 100:.2f}%")
    print(f"    Entitas IP  : {parsed['entities']['target'] or '-'}")
    if parsed['entities'].get('dst_port'):
        print(f"    Entitas Port: {parsed['entities']['dst_port']} ({parsed['entities'].get('protocol', 'tcp')})")
    print(f"    Entitas Rate: {parsed['entities']['rate'] or '-'}")
    print(f"    Latensi NLP : {parsed['processing_time_ms']:.2f} ms")

    print(f"\n{COLOR_BOLD}[2] Intermediate Policy:{COLOR_RESET}")
    is_valid = policy.get("is_valid", False)
    if is_valid:
        print(f"    Status      : {COLOR_GREEN}VALID{COLOR_RESET}")
        print(f"    Action      : {policy.get('action')}")
        print(f"    Target Net  : {policy.get('target') or '-'}")
        if policy.get('dst_port'):
            print(f"    Dst Port    : {policy.get('dst_port')} ({policy.get('protocol', 'tcp')})")
        if policy.get('out_interface'):
            print(f"    Out-Iface   : {policy.get('out_interface')}")
        print(f"    Rate Limit  : {policy.get('rate') or '-'}")
        print(f"    Rule Name   : {policy.get('name') or '-'}")
    else:
        print(f"    Status      : {COLOR_RED}INVALID / DITOLAK{COLOR_RESET}")
        print(f"    Alasan      : {COLOR_YELLOW}{policy.get('error', 'Parameter tidak sesuai')}{COLOR_RESET}")
        print(f"\n{COLOR_BOLD}[3] Eksekusi Router MikroTik:{COLOR_RESET}")
        print(f"    {COLOR_YELLOW}Dibatalkan: Kebijakan tidak memenuhi syarat validasi keamanan.{COLOR_RESET}")
        print("-" * 80 + "\n")
        return

    print(f"\n{COLOR_BOLD}[3] Eksekusi Router MikroTik:{COLOR_RESET}")
    exec_res = execute_policy(policy, adapter)
    total_latency_ms = (time.perf_counter() - t_start) * 1000.0

    if exec_res.get("status") == "success":
        res = exec_res.get("result")
        print(f"    Status      : {COLOR_GREEN}SUKSES{COLOR_RESET}")
        if isinstance(res, dict):
            print(f"    Aksi Router : {res.get('action', '-')}")
            if "id" in res:
                print(f"    Rule ID     : {res.get('id', '-')}")
            if "name" in res:
                print(f"    Interface   : {res.get('name')}")
            if "disabled" in res:
                print(f"    Disabled    : {res.get('disabled')}")
            if "out_interface" in res:
                print(f"    Out-Iface   : {res.get('out_interface')}")
            if "max_limit" in res:
                print(f"    Max Limit   : {res.get('max_limit')}")
            if res.get("dst_port"):
                print(f"    Dst Port    : {res.get('dst_port')} ({res.get('protocol', 'tcp')})")
            if "comment" in res:
                print(f"    Comment     : {res.get('comment')}")
        elif isinstance(res, int):
            action_label = "removed" if res > 0 else "noop (rule tidak ditemukan)"
            print(f"    Aksi Router : {action_label}")
            print(f"    Jml Dihapus : {res}")
        print(f"    Total Waktu : {total_latency_ms:.2f} ms")
    else:
        print(f"    Status      : {COLOR_RED}GAGAL{COLOR_RESET}")
        print(f"    Error       : {exec_res.get('error')}")
    print("-" * 80 + "\n")


def main():
    adapter = MikroTikAdapter()
    connected = False
    try:
        adapter.connect()
        connected = True
    except Exception as e:
        print(f"{COLOR_YELLOW}Peringatan: Gagal terhubung ke router ({e}){COLOR_RESET}")

    print_banner(connected)

    while True:
        try:
            prompt_str = f"{COLOR_BOLD}IBN-MURNI [ketik kalimat / \"status\" / \"bantuan\" / \"keluar\"]> {COLOR_RESET}"
            user_input = input(prompt_str).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{COLOR_CYAN}Terima kasih telah menggunakan Sistem IBN Versi Murni. Sampai jumpa!{COLOR_RESET}")
            break

        if not user_input:
            continue

        cmd_lower = user_input.lower()
        if cmd_lower in ("keluar", "exit", "q", "quit"):
            print(f"\n{COLOR_CYAN}Terima kasih telah menggunakan Sistem IBN Versi Murni. Sampai jumpa!{COLOR_RESET}")
            break
        elif cmd_lower in ("status", "cek"):
            show_status(adapter)
        elif cmd_lower in ("bantuan", "help"):
            show_help()
        elif cmd_lower in ("clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            print_banner(connected)
        else:
            handle_input_intent(user_input, adapter)

    adapter.close()


if __name__ == "__main__":
    main()
