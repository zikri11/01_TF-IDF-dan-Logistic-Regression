import json
from collections import Counter
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "dataset_intent.json"

new_samples = {
    "limit_bandwidth": [
        "bisa tolong batasi kecepatan komputer 10.0.0.12 jadi 1mbps",
        "alokasikan bandwidth untuk pc 192.168.88.60 sebesar 2 mega",
        "tolong limitasi transfer rate host 10.0.0.15 ke 512k",
        "pangkas kecepatan internet client 192.168.88.45 jadi 256kbps",
        "kecilkan bandwidth laptop 10.0.0.22 sebesar 1m",
        "atur batasan data untuk host 192.168.88.75 jadi 3 Mbps",
        "tolong cekik kecepatan download upload 10.0.0.30 ke 4mb",
        "batasi pemakaian data user 192.168.88.95 di 5mbps",
        "kasih limitasi kecepatan internet 10.0.0.40 jadi 512 kbps",
        "setel batas transfer rate 192.168.88.105 sebesar 2mbit",
        "tolong batasi eth 2 jadi 4mb",
        "kasih limit lan 3 sebesar 10mbps",
        "atur kecepatan jalur 1 ke 2 mega",
        "batasi transfer data iface 4 jadi 1m",
        "tolong batasi colokan 2 sebesar 512k",
        "set batas bandwidth kabel lan 3 jadi 3mb",
        "pangkas kecepatan int 1 ke 2mbps",
        "batasi penggunaan internet port lan 4 jadi 5 mega",
        "bisa limit kecepatan link 1 jadi 4 Mbps",
        "atur alokasi bandwidth port eth 3 di 2mbps",
    ],
    "remove_limit": [
        "kembalikan kecepatan semula komputer 10.0.0.12",
        "bebaskan transfer rate untuk host 192.168.88.60",
        "tolong lepaskan batasan bandwidth client 10.0.0.15",
        "normalkan transfer data untuk laptop 192.168.88.45",
        "hilangkan limitasi kecepatan internet 10.0.0.22",
        "cabut pengaturan batas data host 192.168.88.75",
        "reset batasan qos client 10.0.0.30 ke semula",
        "unlimit penggunaan bandwidth untuk 192.168.88.95",
        "hapus pembatasan transfer rate perangkat 10.0.0.40",
        "tolong hilangkan aturan pembatasan 192.168.88.105",
        "kembalikan speed normal untuk eth 2",
        "bebaskan limit bandwidth lan 3",
        "cabut pembatasan kecepatan jalur 1",
        "lepaskan batasan transfer data iface 4",
        "normalkan kecepatan pada colokan 2",
        "hapus limitasi qos kabel lan 3",
        "unlimit batasan internet int 1",
        "reset kecepatan port lan 4 ke semula",
        "hilangkan batas bandwidth link 1",
        "cabut limitasi data port eth 3",
    ],
    "block_traffic": [
        "cegat seluruh lalu lintas data dari host 10.0.0.12",
        "isolasi komunikasi jaringan komputer 192.168.88.60",
        "tolak semua paket data dari 10.0.0.15",
        "putus akses internet untuk perangkat 192.168.88.45",
        "hentikan koneksi keluar masuk laptop 10.0.0.22",
        "cegat paket internet dari user 192.168.88.75",
        "jatuhkan semua trafik komunikasi 10.0.0.30",
        "blokir akses komunikasi client 192.168.88.95",
        "tutup koneksi internet dari host 10.0.0.40",
        "tolak akses jaringan komputer 192.168.88.105",
        "blokir port 80 pada lan 3",
        "tutup akses port 443 di eth 2",
        "blokir port 22 untuk iface 4",
        "cegat port 53 pada jalur 1",
        "blokir akses web http untuk 10.0.0.12",
        "tutup koneksi https port 443 client 192.168.88.60",
        "blokir port ssh pada komputer 10.0.0.15",
        "tolak paket dns port 53 untuk 192.168.88.45",
        "blokir port 8080 pada colokan 2",
        "tutup port 80 kabel lan 3",
    ],
    "unblock_traffic": [
        "buka kembali isolasi jaringan komputer 10.0.0.12",
        "izinkan lalu lintas data dari host 192.168.88.60",
        "lepaskan pencegatan paket untuk 10.0.0.15",
        "pulihkan koneksi internet perangkat 192.168.88.45",
        "bolehkan kembali akses komunikasi 10.0.0.22",
        "buka blokir koneksi keluar masuk 192.168.88.75",
        "izinkan paket data dari komputer 10.0.0.30",
        "lepaskan isolasi trafik untuk user 192.168.88.95",
        "pulihkan akses komunikasi host 10.0.0.40",
        "buka kembali aturan tolak paket 192.168.88.105",
        "buka blokir port 80 pada lan 3",
        "izinkan kembali port 443 di eth 2",
        "buka akses port 22 untuk iface 4",
        "lepaskan blokir port 53 pada jalur 1",
        "buka blokir layanan web http untuk 10.0.0.12",
        "pulihkan akses https port 443 client 192.168.88.60",
        "buka blokir port ssh pada komputer 10.0.0.15",
        "izinkan paket dns port 53 untuk 192.168.88.45",
        "buka kembali port 8080 pada colokan 2",
        "lepaskan blokir port 80 kabel lan 3",
    ],
    "enable_interface": [
        "hidupkan port eth 3",
        "nyalakan lan 4 mikrotik",
        "aktifkan int 1 router",
        "tolong hidupkan iface 3",
        "nyalakan colokan 4",
        "aktifkan jalur kabel 3",
        "hidupkan link 1",
        "tolong aktifkan port lan 4",
        "nyalakan antarmuka eth 3",
        "aktifkan sambungan lan 4",
        "hidupkan kembali ethernet 3",
        "nyalakan kembali iface 4",
        "tolong aktifkan colokan 1",
        "buka koneksi port eth 4",
        "aktifkan antarmuka kabel lan 3",
        "hidupkan koneksi int 3",
        "nyalakan jalur port 4",
        "aktifkan interfaces eth 1",
        "hidupkan link kabel 3",
        "nyalakan port lan 1",
    ],
    "disable_interface": [
        "matikan port eth 3",
        "padamkan lan 4 mikrotik",
        "nonaktifkan int 1 router",
        "tolong matikan iface 3",
        "putuskan colokan 4",
        "matikan jalur kabel 3",
        "tutup link 1",
        "tolong nonaktifkan port lan 4",
        "padamkan antarmuka eth 3",
        "matikan sambungan lan 4",
        "putus koneksi ethernet 3",
        "nonaktifkan kembali iface 4",
        "tolong matikan colokan 1",
        "tutup koneksi port eth 4",
        "padamkan antarmuka kabel lan 3",
        "matikan koneksi int 3",
        "putus jalur port 4",
        "nonaktifkan interfaces eth 1",
        "padamkan link kabel 3",
        "matikan port lan 1",
    ],
    "enable_nat": [
        "tolong nyalakan kembali nat masquerade",
        "aktifkan konfigurasi masquerade internet",
        "pasang aturan nat masquerade untuk wan",
        "buat aturan masquerade pada interface ether1",
        "hidupkan fungsi nat masquerade router",
        "tolong aktifkan masquerade pada eth 1",
        "nyalakan fitur nat internet wan",
        "pasang nat masquerade di jalur 1",
        "aktifkan masquerade untuk koneksi publik",
        "buat konfigurasi nat pada ether1",
        "hidupkan masquerade firewall internet",
        "aktifkan rule nat masquerade eth1",
        "pasang aturan masquerade internet publik",
        "tolong hidupkan kembali nat internet",
        "aktifkan fitur masquerade jaringan wan",
        "nyalakan kembali aturan nat masquerade",
        "pasang konfigurasi nat untuk port 1",
        "aktifkan fungsi berbagi internet masquerade",
        "buat aturan nat masquerade gateway",
        "hidupkan aturan masquerade koneksi luar",
    ],
    "disable_nat": [
        "tolong matikan kembali nat masquerade",
        "nonaktifkan konfigurasi masquerade internet",
        "cabut aturan nat masquerade untuk wan",
        "hapus aturan masquerade pada interface ether1",
        "padamkan fungsi nat masquerade router",
        "tolong nonaktifkan masquerade pada eth 1",
        "tutup fitur nat internet wan",
        "cabut nat masquerade di jalur 1",
        "hilangkan masquerade untuk koneksi publik",
        "hapus konfigurasi nat pada ether1",
        "padamkan masquerade firewall internet",
        "matikan rule nat masquerade eth1",
        "cabut aturan masquerade internet publik",
        "tolong matikan kembali nat internet",
        "nonaktifkan fitur masquerade jaringan wan",
        "tutup kembali aturan nat masquerade",
        "cabut konfigurasi nat untuk port 1",
        "hilangkan fungsi berbagi internet masquerade",
        "hapus aturan nat masquerade gateway",
        "padamkan aturan masquerade koneksi luar",
    ],
    "get_interface_ip": [
        "bisa tolong periksa ip pada eth 2",
        "inspeksi status ip lan 3",
        "lihat alamat ip di int 4",
        "tampilkan informasi ip iface 1",
        "cek konfigurasi ip colokan 2",
        "periksa alamat ip kabel lan 3",
        "lihat status ip link 4",
        "cek ip port lan 1",
        "inspeksi ip pada port eth 2",
        "tampilkan ip address jalur kabel 3",
        "cek ip eth 1 dan lan 3",
        "periksa ip colokan 2 dan iface 4",
        "tampilkan ip int 3 dan link 1",
        "lihat ip kabel lan 4 dan port 2",
        "cek status ip di seluruh antarmuka",
        "tampilkan seluruh ip address router",
        "periksa daftar ip semua interface",
        "lihat telemetri ip port 3",
        "inspeksi status ip dan link ether4",
        "tampilkan info ip address interface ether1",
    ],
    "add_ip_address": [
        "tolong pasangkan ip 10.20.10.1/24 di eth 3",
        "masukkan alamat ip 172.16.80.1 pada lan 4",
        "beri ip 192.168.140.1/24 untuk int 1",
        "konfigurasikan ip 10.30.20.1 di iface 3",
        "tambahkan alamat ip 172.20.50.1/24 ke colokan 4",
        "pasang ip baru 192.168.150.1 pada kabel lan 3",
        "input ip 10.40.1.1/24 di link 1",
        "tetapkan ip 172.16.90.1 untuk port lan 4",
        "konfigurasi alamat ip 192.168.160.1/24 pada port eth 3",
        "tambahkan ip 10.50.20.1 ke jalur kabel 4",
        "pasang ip 172.20.60.1/24 di eth 1",
        "masukkan ip 192.168.170.1 pada lan 3",
        "beri alamat ip 10.60.1.1/24 untuk int 4",
        "konfigurasikan ip baru 172.16.100.1 di iface 1",
        "tolong tambahkan ip 192.168.180.1/24 ke colokan 3",
        "pasangkan ip 10.70.10.1 pada kabel lan 4",
        "input alamat ip 172.20.70.1/24 di link 3",
        "tetapkan ip baru 192.168.190.1 untuk port lan 1",
        "konfigurasi ip 10.80.1.1/24 pada port eth 4",
        "tambahkan alamat ip baru 172.16.110.1 di jalur kabel 3",
    ],
    "update_ip_address": [
        "tolong ganti ip eth 3 jadi 10.20.10.1/24",
        "ubah alamat ip pada lan 4 ke 172.16.80.1",
        "tukar ip int 1 dengan 192.168.140.1/24",
        "update konfigurasi ip di iface 3 jadi 10.30.20.1",
        "gantikan ip colokan 4 menjadi 172.20.50.1/24",
        "setel ulang ip kabel lan 3 jadi 192.168.150.1",
        "replace alamat ip link 1 dengan 10.40.1.1/24",
        "pindahkan ip port lan 4 jadi 172.16.90.1",
        "ganti ip address port eth 3 ke 192.168.160.1/24",
        "ubah ip jalur kabel 4 jadi 10.50.20.1",
        "tolong update ip eth 1 ke 172.20.60.1/24",
        "ganti alamat ip lan 3 menjadi 192.168.170.1",
        "tukar ip int 4 dengan 10.60.1.1/24",
        "set ulang ip di iface 1 jadi 172.16.100.1",
        "replace ip colokan 3 dengan 192.168.180.1/24",
        "ubah konfigurasi ip kabel lan 4 ke 10.70.10.1",
        "pindahkan alamat ip link 3 jadi 172.20.70.1/24",
        "gantikan ip port lan 1 menjadi 192.168.190.1",
        "setel ulang ip port eth 4 ke 10.80.1.1/24",
        "update alamat ip jalur kabel 3 jadi 172.16.110.1",
    ],
}


def expand_dataset():
    print("=" * 65)
    print("  FASE 1 & 2: INJEKSI & VALIDASI DATASET (330 -> 550 SAMPEL)")
    print("=" * 65)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    initial_total = len(dataset)
    print(f"[*] Jumlah sampel awal: {initial_total}")

    existing_texts = {x["text"].strip().lower() for x in dataset}

    appended_count = 0
    for intent, items in new_samples.items():
        assert len(items) == 20, f"Kelas '{intent}' harus memiliki 20 sampel baru, didapat {len(items)}"
        for text in items:
            t_clean = text.strip()
            assert t_clean.lower() not in existing_texts, f"Duplikasi terdeteksi: '{t_clean}'"
            dataset.append({
                "text": t_clean,
                "intent": intent,
            })
            existing_texts.add(t_clean.lower())
            appended_count += 1

    print(f"[+] Berhasil menyusun & menambahkan: {appended_count} sampel baru.")

    final_total = len(dataset)
    assert final_total == 550, f"Total akhir harus 550, didapat: {final_total}"

    counts = Counter(x["intent"] for x in dataset)
    assert len(counts) == 11, f"Jumlah kelas harus 11, didapat: {len(counts)}"

    for intent, count in counts.items():
        assert count == 50, f"Kelas {intent} harus tepat 50 sampel, didapat {count}"

    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"[+] File dataset_intent.json berhasil disimpan dengan {final_total} sampel.")
    print("\nDistribusi 11 Kelas Intent Terverifikasi:")
    for intent, count in sorted(counts.items()):
        print(f"  - {intent:<20}: {count} sampel")

    print("=" * 65)
    print("  FASE 1 & 2 SUKSES 100% (ZERO CLASS IMBALANCE & ZERO DUPLICATES)")
    print("=" * 65)


if __name__ == "__main__":
    expand_dataset()
