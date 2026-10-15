import os
import sys
import time
from pathlib import Path
from config import ROUTER_HOST
from mikrotik_adapter import MikroTikAdapter
from nlp_parser import parse_intent, MODEL_PATH
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
    model_kb = int(MODEL_PATH.stat().st_size / 1024) if MODEL_PATH.exists() else 35
    print("=" * 80)
    print(f"{COLOR_BOLD}{COLOR_CYAN}                SISTEM IBN MIKROTIK v6 (INTENT-BASED NETWORKING){COLOR_RESET}")
    print(f" Router: {ROUTER_HOST} | Status: {status_str} | Model: Lightweight TF-IDF ({model_kb} KB)")
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
                status_str = "Disabled" if n.get("disabled") in (True, "true") else "Aktif"
                rows.append([
                    str(idx),
                    n.get(".id", "-"),
                    n.get("chain", "-"),
                    n.get("action", "-"),
                    n.get("out-interface") or n.get("out-interface-list") or "-",
                    n.get("comment", "-"),
                    status_str,
                ])
            print(format_table(["No", "ID", "Chain", "Action", "Out-Interface", "Comment", "Status"], rows))
        else:
            print("    (Tidak ada NAT rule aktif)")

        ifaces = adapter.get_interface_states()
        print(f"\n[4] Interface Status Router ({len(ifaces)} interface):")
        if ifaces:
            rows = []
            for idx, i in enumerate(ifaces, 1):
                status_str = "Disabled" if i.get("disabled") in (True, "true") else "Aktif"
                running_str = "yes" if i.get("running") in (True, "true") else "no"
                rows.append([
                    str(idx),
                    i.get(".id", "-"),
                    i.get("name", "-"),
                    i.get("type", "-"),
                    status_str,
                    running_str,
                ])
            print(format_table(["No", "ID", "Name", "Type", "Status", "Running"], rows))
        else:
            print("    (Tidak ada interface terdeteksi)")

        ip_addrs = adapter.get_ip_addresses()
        print(f"\n[5] IP Address Assignment Router ({len(ip_addrs)} address):")
        if ip_addrs:
            rows = []
            for idx, a in enumerate(ip_addrs, 1):
                status_str = "Disabled" if a.get("disabled") in (True, "true") else "Aktif"
                rows.append([
                    str(idx),
                    a.get(".id", "-"),
                    a.get("interface") or a.get("actual-interface") or "-",
                    a.get("address", "-"),
                    a.get("network", "-"),
                    status_str,
                ])
            print(format_table(["No", "ID", "Interface", "Address / Subnet", "Network", "Status"], rows))
        else:
            print("    (Tidak ada IP address terdaftar)")
        print()
    except Exception as e:
        print(f"{COLOR_RED}Gagal mengambil status router: {e}{COLOR_RESET}\n")


def show_help():
    print(f"""
{COLOR_BOLD}{COLOR_CYAN}=== PANDUAN PENGGUNAAN SISTEM IBN ==={COLOR_RESET}
Sistem menerima kalimat perintah bahasa alami (Bahasa Indonesia) untuk
konfigurasi otomatis QoS (Simple Queue), Firewall, Interface, dan NAT MikroTik.

{COLOR_BOLD}Contoh Perintah Alami:{COLOR_RESET}
 1. Batasi Bandwidth (limit_bandwidth):
    * "Batasi bandwidth 192.168.88.250 jadi 2 Mbps"
    * "Limit kecepatan internet user 192.168.88.100 ke 512 kbps"
    * "saya ingin port 3 kasih limit 5mb"

 2. Cabut Pembatasan (remove_limit):
    * "Cabut limit 192.168.88.250"
    * "Hapus pembatasan bandwidth untuk port 3"
    * "Hilangkan batasan kecepatan client 192.168.88.200"

 3. Blokir Trafik (block_traffic):
    * "Blokir akses internet 192.168.88.250"
    * "blokir port 80 untuk 192.168.88.50"
    * "blokir port 443"

 4. Buka Blokir (unblock_traffic):
    * "Buka blokir 192.168.88.250"
    * "buka blokir port 80 untuk 192.168.88.50"
    * "buka blokir port 443"

 5. Kontrol Interface (enable_interface / disable_interface):
    * "hidupkan wifi" / "matikan wifi"
    * "nyalakan port 4" / "matikan port 4"
    * (Catatan: port 2 & bridge dilindungi proteksi anti-lockout)

 6. Kontrol NAT Masquerade (enable_nat / disable_nat):
    * "aktifkan nat internet" / "matikan nat internet"
    * "nyalakan NAT masquerade pada ether1"
    * "cabut NAT masquerade pada ether1"

 7. Cek / Inspeksi IP Interface (get_interface_ip):
    * "cek ip port 1" / "cek jalur 1"
    * "cek ip port 1 dan port 3"
    * "cek semua ip"

 8. Penambahan IP Address (add_ip_address):
    * "tambahkan ip 192.168.10.1/24 di port 3"
    * "pasang ip 10.10.10.1 pada ether4"

 9. Pengubahan IP Address (update_ip_address):
    * "ganti ip port 3 jadi 10.10.10.1/24"
    * "ubah ip di ether4 ke 172.16.1.1"

 10. Aturan Penghapusan Spesifik (Safety Object Guard):
    * Wajib menyebut objek spesifik: 'hapus limit port 1', 'hapus ip 10.10.10.1', 'buka blokir port 80'
    * (Catatan: Perintah ambigu seperti 'hapus port 1' otomatis ditolak demi keamanan router)

{COLOR_BOLD}Perintah Sistem Khusus:{COLOR_RESET}
 * status / cek   : Menampilkan Simple Queue, Firewall, NAT, Interface, & IP Address aktif di router
 * bantuan / help : Menampilkan panduan contoh kalimat ini
 * clear / cls    : Membersihkan layar terminal
 * keluar / exit  : Keluar dari program
""")


def handle_input_intent(text: str, adapter: MikroTikAdapter):
    t_start = time.perf_counter()
    parsed = parse_intent(text)
    policy = parsed.get("policy", {})

    intent_str = parsed['intent']
    intent_color = COLOR_CYAN if intent_str != "unknown" else COLOR_YELLOW
    conf_pct = parsed['confidence'] * 100
    conf_color = COLOR_GREEN if conf_pct >= 50.0 else COLOR_RED
    conf_note = "" if conf_pct >= 50.0 else f" {COLOR_RED}(Di bawah ambang batas 50%){COLOR_RESET}"

    print("-" * 80)
    print(f"{COLOR_BOLD}[1] Analisis NLP:{COLOR_RESET}")
    print(f"    Intent      : {intent_color}{intent_str}{COLOR_RESET}")
    print(f"    Keyakinan   : {conf_color}{conf_pct:.2f}%{COLOR_RESET}{conf_note}")
    print(f"    Entitas IP  : {parsed['entities']['target'] or '-'}")
    if parsed['entities'].get('dst_port'):
        print(f"    Entitas Port: {parsed['entities']['dst_port']} ({parsed['entities'].get('protocol', 'tcp')})")
    print(f"    Entitas Rate: {parsed['entities']['rate'] or '-'}")
    if parsed['entities'].get('address'):
        print(f"    Entitas Addr: {parsed['entities']['address']}")
    if parsed['entities'].get('interface'):
        iface_ent = parsed['entities']['interface']
        iface_ent_str = ", ".join(iface_ent) if isinstance(iface_ent, list) else str(iface_ent)
        print(f"    Entitas Iface: {iface_ent_str}")
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
        if policy.get('address'):
            print(f"    IP Address  : {policy.get('address')}")
        if policy.get('interface'):
            iface_pol = policy.get('interface')
            iface_pol_str = ", ".join(iface_pol) if isinstance(iface_pol, list) else str(iface_pol)
            print(f"    Interface   : {iface_pol_str}")
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
        intent = parsed.get("intent")
        if intent == "get_interface_ip" and isinstance(res, list):
            rows = []
            for idx, item in enumerate(res, 1):
                link_status = "Connected (Up)" if item.get("running") else "Unplugged (Down)"
                ips_list = item.get("ips", [])
                ip_str = ", ".join(ips_list) if ips_list else "(Kosong / Tidak Ada IP)"
                rows.append([
                    str(idx),
                    item.get("name", "-"),
                    item.get("type", "-"),
                    item.get("mac", "-"),
                    link_status,
                    ip_str,
                ])
            print(format_table(["No", "Interface", "Tipe", "MAC Address", "Link Status", "IP Address Terpasang"], rows))
        elif intent == "add_ip_address" and isinstance(res, dict):
            print(f"    Aksi Router : {res.get('action', '-')}")
            print(f"    Rule ID     : {res.get('id', '-')}")
            print(f"    Interface   : {res.get('interface', '-')}")
            print(f"    Alamat IP   : {res.get('address', '-')}")
            print(f"    Comment     : {res.get('comment', '-')}")
        elif intent == "update_ip_address" and isinstance(res, dict):
            print(f"    Aksi Router : {res.get('action', '-')}")
            print(f"    Interface   : {res.get('interface', '-')}")
            old_ip = res.get('old_address') or "(Tidak ada IP sebelumnya)"
            print(f"    IP Lama     : {old_ip}")
            print(f"    IP Baru     : {res.get('new_address', '-')}")
            print(f"    Rule ID     : {res.get('id', '-')}")
            print(f"    Comment     : {res.get('comment', '-')}")
        elif isinstance(res, dict):
            print(f"    Aksi Router : {res.get('action', '-')}")
            if "id" in res:
                print(f"    Rule ID     : {res.get('id', '-')}")
            if "name" in res:
                print(f"    Interface   : {res.get('name')}")
            if "interface" in res:
                print(f"    Interface   : {res.get('interface')}")
            if "address" in res:
                print(f"    Alamat IP   : {res.get('address')}")
            if "count" in res:
                print(f"    Jml Dihapus : {res.get('count')}")
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
            prompt_str = f"{COLOR_BOLD}IBN [ketik kalimat / \"status\" / \"bantuan\" / \"keluar\"]> {COLOR_RESET}"
            user_input = input(prompt_str).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{COLOR_CYAN}Terima kasih telah menggunakan Sistem IBN MikroTik. Sampai jumpa!{COLOR_RESET}")
            break

        if not user_input:
            continue

        cmd_lower = user_input.lower()
        if cmd_lower in ("keluar", "exit", "q", "quit"):
            print(f"\n{COLOR_CYAN}Terima kasih telah menggunakan Sistem IBN MikroTik. Sampai jumpa!{COLOR_RESET}")
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
