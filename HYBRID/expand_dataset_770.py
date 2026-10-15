import json
from collections import Counter
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "dataset_intent.json"

new_samples_770 = {
    "limit_bandwidth": [
        "atur batas kecepatan transfer ip 10.10.20.5 menjadi 512 kbps",
        "tolong pangkas pemakaian internet 192.168.88.115 jadi 1mbps",
        "batasi alokasi bandwidth eth 1 di 3 mega",
        "tolong cekik kecepatan download komputer 10.10.30.12 jadi 256k",
        "alokasikan bandwidth internet host 192.168.88.135 sebesar 4mbps",
        "kecilkan alokasi data client 10.10.40.18 jadi 1mbit",
        "bisa tolong batasi transfer rate perangkat 192.168.88.145 ke 2mb",
        "setel batas maksimal bandwidth pc 10.10.50.25 sebesar 5 mega",
        "pangkas kecepatan koneksi user 192.168.88.155 jadi 512k",
        "batasi penggunaan data laptop 10.10.60.30 maksimal 3mbps",
        "tolong atur batas bandwidth lan 2 jadi 2 mega",
        "batasi kecepatan transfer iface 3 ke 1mbps",
        "pangkas alokasi data colokan 1 jadi 512k",
        "atur batas kecepatan kabel lan 4 sebesar 4mb",
        "tolong limitasi transfer data int 2 ke 2mbit",
        "batasi pemakaian bandwidth link 3 jadi 3 mega",
        "kecilkan kecepatan port lan 1 jadi 1mbps",
        "setel batas kecepatan internet port eth 4 sebesar 512 kbps",
        "bisa batasi alokasi data jalur 2 jadi 2mbps",
        "alokasikan bandwidth antarmuka eth 3 di 4 mega",
    ],
    "remove_limit": [
        "cabut pembatasan kecepatan pada komputer 10.10.20.5",
        "kembalikan kecepatan internet host 192.168.88.115 seperti semula",
        "hapus simple queue pembatasan eth 1",
        "unlimit bandwidth kabel lan 2",
        "tolong bebaskan transfer rate client 10.10.30.12",
        "normalkan kembali pemakaian data pc 192.168.88.135",
        "lepaskan batasan kecepatan unduh host 10.10.40.18",
        "hilangkan pengaturan pembatasan data user 192.168.88.145",
        "reset limitasi bandwidth perangkat 10.10.50.25 ke normal",
        "cabut aturan pembatas kecepatan laptop 192.168.88.155",
        "unlimit transfer data untuk laptop 10.10.60.30",
        "tolong kembalikan kecepatan semula lan 2",
        "bebaskan aturan bandwidth iface 3",
        "cabut limitasi kecepatan pada colokan 1",
        "normalkan batasan transfer data kabel lan 4",
        "hilangkan pembatasan bandwidth int 2",
        "lepaskan limitasi internet link 3",
        "reset batas transfer rate port lan 1 ke normal",
        "kembalikan kecepatan penuh port eth 4",
        "cabut aturan simple queue jalur 2",
    ],
    "block_traffic": [
        "blokir seluruh akses internet dari host 10.10.20.5",
        "tutup komunikasi data komputer 192.168.88.115",
        "cegat port 443 pada eth 1",
        "blokir port 80 untuk lan 2",
        "tolak lalu lintas paket data dari 10.10.30.12",
        "putus akses komunikasi internet client 192.168.88.135",
        "isolasi koneksi jaringan komputer 10.10.40.18",
        "hentikan lalu lintas keluar masuk pc 192.168.88.145",
        "jatuhkan semua paket internet perangkat 10.10.50.25",
        "tutup akses keluar masuk data host 192.168.88.155",
        "cegat komunikasi data laptop 10.10.60.30",
        "blokir port 22 pada iface 3",
        "tutup koneksi port 53 di colokan 1",
        "cegat port 8080 untuk kabel lan 4",
        "tolak akses port 80 pada int 2",
        "blokir port 443 untuk link 3",
        "tutup port 22 di port lan 1",
        "cegat port 53 kabel port eth 4",
        "blokir akses web port 80 pada jalur 2",
        "tutup akses layanan https port 443 antarmuka eth 3",
    ],
    "unblock_traffic": [
        "buka kembali blokir internet komputer 10.10.20.5",
        "izinkan kembali lalu lintas data host 192.168.88.115",
        "lepas pencegatan port 443 pada eth 1",
        "buka aturan drop port 80 untuk lan 2",
        "pulihkan akses komunikasi untuk 10.10.30.12",
        "bolehkan lagi paket data dari client 192.168.88.135",
        "lepaskan isolasi jaringan komputer 10.10.40.18",
        "buka kembali koneksi keluar masuk pc 192.168.88.145",
        "pulihkan komunikasi internet perangkat 10.10.50.25",
        "izinkan akses jaringan untuk host 192.168.88.155",
        "buka blokir komunikasi data laptop 10.10.60.30",
        "izinkan kembali port 22 pada iface 3",
        "buka akses port 53 di colokan 1",
        "lepas pencegatan port 8080 untuk kabel lan 4",
        "pulihkan koneksi port 80 pada int 2",
        "izinkan lalu lintas port 443 untuk link 3",
        "buka blokir port 22 di port lan 1",
        "lepas blokir port 53 kabel port eth 4",
        "pulihkan akses web port 80 pada jalur 2",
        "izinkan layanan https port 443 antarmuka eth 3",
    ],
    "enable_interface": [
        "tolong nyalakan interface port 1",
        "hidupkan kembali antarmuka eth 2",
        "aktifkan colokan kabel lan 3",
        "nyalakan link antarmuka iface 4",
        "aktifkan port int 2",
        "hidupkan jalur koneksi port lan 3",
        "nyalakan sambungan port eth 1",
        "tolong aktifkan interface colokan 2",
        "hidupkan antarmuka kabel lan 1",
        "nyalakan kembali koneksi link 2",
        "aktifkan kembali jalur port 3",
        "hidupkan antarmuka port eth 2",
        "tolong nyalakan sambungan int 4",
        "aktifkan koneksi jaringan iface 2",
        "hidupkan kembali colokan kabel 1",
        "nyalakan antarmuka link 4",
        "tolong aktifkan sambungan port lan 2",
        "hidupkan koneksi interface eth 4",
        "nyalakan kembali antarmuka lan 1",
        "aktifkan jalur sambungan port 2",
    ],
    "disable_interface": [
        "matikan antarmuka interface port 1",
        "padamkan colokan eth 2",
        "nonaktifkan jalur kabel lan 3",
        "tutup sambungan link iface 4",
        "matikan port int 2",
        "putuskan jalur koneksi port lan 3",
        "padamkan sambungan port eth 1",
        "tolong matikan interface colokan 2",
        "nonaktifkan antarmuka kabel lan 1",
        "tutup kembali koneksi link 2",
        "matikan kembali jalur port 3",
        "padamkan antarmuka port eth 2",
        "tolong matikan sambungan int 4",
        "nonaktifkan koneksi jaringan iface 2",
        "padamkan kembali colokan kabel 1",
        "tutup antarmuka link 4",
        "tolong nonaktifkan sambungan port lan 2",
        "matikan koneksi interface eth 4",
        "padamkan kembali antarmuka lan 1",
        "putus jalur sambungan port 2",
    ],
    "enable_nat": [
        "aktifkan kembali fitur nat masquerade router",
        "tolong nyalakan fungsi berbagi internet masquerade",
        "pasang aturan masquerade pada antarmuka wan",
        "buat konfigurasi nat masquerade untuk ether1",
        "hidupkan kembali rule nat masquerade internet",
        "nyalakan fungsi gateway nat masquerade",
        "pasang aturan berbagi koneksi internet masquerade",
        "tolong aktifkan fitur masquerade pada ether1",
        "buat rule nat masquerade untuk jaringan publik",
        "hidupkan kembali konfigurasi masquerade wan",
        "nyalakan aturan firewall nat masquerade",
        "pasang konfigurasi masquerade pada antarmuka ether1",
        "aktifkan kembali fungsi nat internet publik",
        "tolong hidupkan fitur sharing internet masquerade",
        "buat konfigurasi masquerade gateway internet",
        "nyalakan kembali rule nat masquerade ether1",
        "pasang aturan nat masquerade untuk port wan",
        "aktifkan fungsi translasi alamat masquerade",
        "hidupkan aturan masquerade jaringan luar",
        "tolong nyalakan konfigurasi nat gateway wan",
    ],
    "disable_nat": [
        "matikan kembali fitur nat masquerade router",
        "tolong cabut fungsi berbagi internet masquerade",
        "hapus aturan masquerade pada antarmuka wan",
        "nonaktifkan konfigurasi nat masquerade untuk ether1",
        "padamkan kembali rule nat masquerade internet",
        "tutup fungsi gateway nat masquerade",
        "cabut aturan berbagi koneksi internet masquerade",
        "tolong nonaktifkan fitur masquerade pada ether1",
        "hapus rule nat masquerade untuk jaringan publik",
        "padamkan kembali konfigurasi masquerade wan",
        "tutup aturan firewall nat masquerade",
        "cabut konfigurasi masquerade pada antarmuka ether1",
        "matikan kembali fungsi nat internet publik",
        "tolong padamkan fitur sharing internet masquerade",
        "hapus konfigurasi masquerade gateway internet",
        "tutup kembali rule nat masquerade ether1",
        "cabut aturan nat masquerade untuk port wan",
        "hilangkan fungsi translasi alamat masquerade",
        "padamkan aturan masquerade jaringan luar",
        "tolong matikan konfigurasi nat gateway wan",
    ],
    "get_interface_ip": [
        "cek konfigurasi ip pada port lan 1",
        "lihat alamat ip yang terpasang di eth 2",
        "inspeksi status ip dan koneksi lan 3",
        "tampilkan informasi ip di int 4",
        "periksa telemetri ip colokan 1",
        "cek alamat ip antarmuka iface 2",
        "lihat status konfigurasi ip kabel lan 3",
        "inspeksi informasi ip address link 4",
        "tampilkan status ip pada port eth 1",
        "periksa alamat ip jalur 2",
        "cek ip pada antarmuka port 3",
        "lihat telemetri ip colokan 4",
        "inspeksi ip address interface eth 2",
        "tampilkan informasi ip di lan 1",
        "periksa status ip int 3",
        "cek konfigurasi ip address kabel lan 2",
        "lihat alamat ip port lan 3",
        "inspeksi telemetri ip link 2",
        "tampilkan status ip jalur 4",
        "periksa konfigurasi ip antarmuka iface 3",
    ],
    "add_ip_address": [
        "tambahkan alamat ip 10.50.10.1/24 di port 1",
        "pasang ip baru 172.16.120.1 pada eth 2",
        "masukkan ip 192.168.200.1/24 ke lan 3",
        "konfigurasikan ip 10.60.20.1 di int 4",
        "beri ip 172.20.80.1/24 pada colokan 1",
        "input alamat ip 192.168.210.1 di iface 2",
        "tetapkan ip baru 10.70.30.1/24 untuk kabel lan 3",
        "pasangkan ip 172.16.130.1 pada link 4",
        "tambahkan ip address 192.168.220.1/24 ke port lan 1",
        "konfigurasi ip baru 10.80.40.1 di port eth 2",
        "pasang alamat ip 172.20.90.1/24 pada jalur 3",
        "masukkan ip baru 192.168.230.1 ke antarmuka eth 4",
        "beri alamat ip 10.90.50.1/24 di colokan 2",
        "konfigurasikan ip 172.16.140.1 pada kabel lan 1",
        "input ip baru 192.168.240.1/24 untuk int 3",
        "tetapkan alamat ip 10.100.10.1 di iface 4",
        "pasangkan ip 172.20.100.1/24 pada port lan 2",
        "tambahkan konfigurasi ip 192.168.250.1 di link 3",
        "pasang ip baru 10.110.20.1/24 ke jalur 4",
        "konfigurasi alamat ip 172.16.150.1 pada antarmuka lan 1",
    ],
    "update_ip_address": [
        "ganti ip pada port 1 jadi 10.50.10.1/24",
        "ubah alamat ip eth 2 ke 172.16.120.1",
        "tukar ip di lan 3 dengan 192.168.200.1/24",
        "update konfigurasi ip int 4 jadi 10.60.20.1",
        "replace ip colokan 1 dengan 172.20.80.1/24",
        "setel ulang alamat ip iface 2 ke 192.168.210.1",
        "pindahkan ip kabel lan 3 jadi 10.70.30.1/24",
        "gantikan ip pada link 4 menjadi 172.16.130.1",
        "ubah konfigurasi ip port lan 1 ke 192.168.220.1/24",
        "tukar alamat ip di port eth 2 dengan 10.80.40.1",
        "ganti ip jalur 3 jadi 172.20.90.1/24",
        "update ip antarmuka eth 4 ke 192.168.230.1",
        "replace alamat ip colokan 2 dengan 10.90.50.1/24",
        "setel ulang konfigurasi ip kabel lan 1 jadi 172.16.140.1",
        "ubah ip pada int 3 ke 192.168.240.1/24",
        "pindahkan alamat ip iface 4 jadi 10.100.10.1",
        "gantikan ip port lan 2 menjadi 172.20.100.1/24",
        "tukar konfigurasi ip di link 3 dengan 192.168.250.1",
        "ganti alamat ip jalur 4 jadi 10.110.20.1/24",
        "update ip antarmuka lan 1 ke 172.16.150.1",
    ],
}


def expand_dataset_to_770():
    print("=" * 70)
    print("  FASE 1 & 2: INJEKSI & VALIDASI DATASET (550 -> 770 SAMPEL)")
    print("=" * 70)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    initial_total = len(dataset)
    print(f"[*] Jumlah sampel awal: {initial_total}")
    assert initial_total == 550, f"Harusnya 550 sampel awal, didapat {initial_total}"

    existing_texts = {x["text"].strip().lower() for x in dataset}

    appended_count = 0
    for intent, items in new_samples_770.items():
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
    assert final_total == 770, f"Total akhir harus 770, didapat: {final_total}"

    counts = Counter(x["intent"] for x in dataset)
    assert len(counts) == 11, f"Jumlah kelas harus 11, didapat: {len(counts)}"

    for intent, count in counts.items():
        assert count == 70, f"Kelas {intent} harus tepat 70 sampel, didapat {count}"

    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"[+] File dataset_intent.json berhasil disimpan dengan {final_total} sampel.")
    print("\nDistribusi 11 Kelas Intent Terverifikasi:")
    for intent, count in sorted(counts.items()):
        print(f"  - {intent:<20}: {count} sampel")

    print("=" * 70)
    print("  FASE 1 & 2 SUKSES 100% (770 SAMPEL, ZERO IMBALANCE & ZERO DUPLICATES)")
    print("=" * 70)


if __name__ == "__main__":
    expand_dataset_to_770()
