"""
Dataset Expander: 770 -> 980 balanced samples (14 intent classes x 70 samples).
Adds 70 samples each for:
- get_bandwidth_status
- get_firewall_status
- get_nat_status
Following NIT dataset prompt taxonomy (Technical, Colloquial, Descriptive).
"""

import json
from collections import Counter
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "dataset_intent.json"

new_samples_980 = {
    "get_bandwidth_status": [
        # Type 1: Technical (Simple Queue, Max-Limit, QoS, Data Rate)
        "tampilkan seluruh antrean simple queue",
        "cek daftar aturan simple queue aktif",
        "lihat alokasi max limit simple queue",
        "periksa konfigurasi simple queue router",
        "tampilkan tabel pembatasan bandwidth",
        "cek parameter max-limit simple queue",
        "tampilkan antrean qos yang aktif di router",
        "periksa data rate simple queue",
        "tampilkan daftar pembatasan kecepatan qos",
        "inspeksi seluruh aturan simple queue",
        "cek limit bandwidth host 192.168.88.50",
        "periksa status antrean qos ip 192.168.88.20",
        "lihat aturan pembatasan kecepatan 192.168.88.35",
        "cek max-limit untuk target 192.168.88.40",
        "tampilkan alokasi bandwidth komputer 192.168.88.15",
        "periksa limit kecepatan host 192.168.88.70",
        "cek status qos target 192.168.88.25",
        "lihat antrean simple queue ip 10.10.10.5",
        "periksa batasan bandwidth client 10.10.20.15",
        "cek alokasi data rate host 172.16.1.10",
        "cek limit bandwidth port 3",
        "periksa pembatasan kecepatan ether3",
        "lihat alokasi bandwidth colokan lan 2",
        "tampilkan limit kecepatan kabel lan 4",
        "cek status antrean qos eth 1",
        "periksa kuota bandwidth jalur 2",
        "lihat aturan limit antarmuka iface 3",
        "cek limit kecepatan antarmuka int 2",
        "tampilkan status antrean port lan 1",
        "periksa batasan data link 3",
        # Type 2: Colloquial / Lab Slang (dicekik, kena limit, jatah inet)
        "siapa saja yang lagi dibatasi bandwidth",
        "siapa aja yang lagi dicekik kecepatannya",
        "lihat yang lagi dilimit dong",
        "cek komputer mana yang kena limit",
        "siapa yang kena cekik bandwidth di lab",
        "lihat daftar user yang dibatasi internetnya",
        "ada siapa aja di tabel limit bandwidth",
        "siapa saja klien yang kena simple queue",
        "cek daftar perangkat yang dibatasi",
        "lihat yang kecepatannya dipotong",
        "apakah 192.168.88.50 kena limit bandwidth",
        "laptop 192.168.88.20 lagi dilimit gak",
        "cek komputer 192.168.88.35 dapet kecepatan berapa",
        "komputer 192.168.88.40 lagi dicekik gak inetnya",
        "apakah ip 192.168.88.15 kena pembatasan kecepatan",
        "user 192.168.88.70 dibatasi berapa mega",
        "pc 192.168.88.25 internetnya dicekik gak",
        "apakah client 10.10.10.5 ada di daftar limit",
        "cek dong komputer 10.10.20.15 dapet jatah bandwidth berapa",
        "apakah host 172.16.1.10 dibatasi kecepatannya",
        "colokan 3 lagi kena limit gak",
        "port 2 internetnya dicekik gak sih",
        "cek lan 4 dapet bandwidth berapa",
        "apakah jalur 1 dibatasi kecepatannya",
        "colokan lan 3 kena aturan limit gak",
        "cek kecepatan kabel 2 sekarang berapa",
        "apakah eth 4 lagi dicekik bandwidth-nya",
        "lihat kuota kecepatan colokan 1 dong",
        "port lan 2 ada limitnya gak",
        "jalur kabel 3 dibatasi berapa mb",
        # Type 3: Descriptive & Interrogative
        "berapa batas kecepatan internet saat ini",
        "apakah ada pembatasan bandwidth yang sedang aktif",
        "tampilkan informasi antrean kecepatan jaringan",
        "lihat ringkasan limit bandwidth yang berjalan",
        "cek apakah ada komputer yang dibatasi koneksinya",
        "tampilkan daftar pengguna yang mengalami pembatasan",
        "bagaimana status alokasi bandwidth saat ini",
        "periksa apakah ada aturan qos yang berjalan di router",
        "tampilkan monitoring antrean pembatasan internet",
        "lihat rincian aturan bandwidth yang diterapkan"
    ],
    "get_firewall_status": [
        # Type 1: Technical (Filter Drop, Forward Chain, Port Protocol)
        "tampilkan seluruh aturan firewall filter drop",
        "cek daftar rule filter drop yang aktif",
        "lihat daftar rule pencekalan paket data",
        "periksa tabel filter drop chain forward",
        "tampilkan konfigurasi firewall filter yang aktif",
        "inspeksi seluruh aturan drop pada firewall",
        "cek rule pemblokiran akses internet di router",
        "tampilkan daftar filter firewall drop forward",
        "periksa status pencegahan trafik pada firewall",
        "lihat daftar blacklist firewall filter",
        "cek status firewall untuk ip 192.168.88.99",
        "apakah host 192.168.88.50 terdaftar di drop rule",
        "periksa status pencekalan komputer 192.168.88.20",
        "lihat aturan firewall untuk target 192.168.88.35",
        "cek apakah ip 192.168.88.40 diblokir firewall",
        "periksa status drop host 192.168.88.15",
        "tampilkan aturan firewall klien 192.168.88.70",
        "cek filter drop untuk pc 10.10.10.99",
        "lihat apakah client 10.10.20.50 terkena drop",
        "periksa pencekalan host 172.16.1.99",
        "cek status pemblokiran port 80",
        "apakah port 443 sedang ditutup firewall",
        "periksa apakah port 22 sedang diblokir",
        "lihat status pencegahan port 53 dns",
        "tampilkan aturan firewall untuk port 8080",
        "cek apakah port layanan http 80 di-drop",
        "periksa status pemblokiran port https 443",
        "lihat apakah port ssh 22 terbuka atau diblokir",
        "cek pencekalan port dns 53 pada firewall",
        "tampilkan status filter port web 80",
        # Type 2: Colloquial / Lab Slang (cut inet, kena blokir, diputus)
        "siapa saja yang lagi diblokir internetnya",
        "siapa yang kena blokir di lab",
        "lihat daftar komputer yang diblokir dong",
        "siapa aja yang gak bisa internetan",
        "cek siapa yang diputus koneksinya",
        "lihat orang-orang yang diblokir router",
        "ada siapa aja di daftar blokir internet",
        "cek komputer mana yang lagi di-drop",
        "siapa yang internetnya dimatikan firewall",
        "lihat user yang kena blokir hari ini",
        "komputer 192.168.88.99 lagi diblokir gak",
        "apakah pc 192.168.88.50 kena cut internet",
        "laptop 192.168.88.20 bisa internetan gak sekarang",
        "cek komputer 192.168.88.35 lagi kena blokir gak",
        "apakah perangkat 192.168.88.40 diputus jalurnya",
        "user 192.168.88.15 kena blokir firewall gak sih",
        "cek dong host 192.168.88.70 bisa browsing gak",
        "apakah pc 10.10.10.99 lagi di-drop router",
        "komputer 10.10.20.50 kena pencekalan gak",
        "cek apakah laptop 172.16.1.99 diblokir aksesnya",
        "port 80 lagi ditutup gak",
        "apakah web port 443 lagi dikunci",
        "cek port 22 lagi diblokir gak sih",
        "port 53 dns ditutup gak sama router",
        "apakah port 8080 bisa diakses sekarang",
        "cek browsing port 80 lagi dimatiin gak",
        "apakah port https 443 diblokir untuk lab",
        "port ssh 22 lagi kena blokir gak",
        "cek dong port 53 lagi di-drop gak",
        "port web 80 lagi aktif apa diblokir",
        # Type 3: Descriptive & Interrogative
        "apakah ada pemblokiran trafik yang aktif",
        "tampilkan ringkasan firewall drop saat ini",
        "bagaimana status pencekalan internet di router",
        "lihat daftar pencekalan akses jaringan yang berlaku",
        "apakah ada perangkat yang saat ini dilarang internetan",
        "periksa apakah ada aturan drop yang berjalan",
        "tampilkan informasi komputer yang dicekal",
        "lihat status proteksi firewall jaringan",
        "cek apakah ada port layanan yang sedang dinonaktifkan",
        "tampilkan seluruh entri blacklist jaringan saat ini"
    ],
    "get_nat_status": [
        # Type 1: Technical (NAT, Srcnat Masquerade, Dst-Nat, Port Forward)
        "tampilkan seluruh aturan nat yang aktif",
        "cek konfigurasi nat router",
        "lihat tabel firewall nat",
        "periksa status aturan srcnat masquerade",
        "tampilkan daftar rule nat masquerade",
        "inspeksi konfigurasi nat internet wan",
        "cek parameter out-interface pada nat masquerade",
        "tampilkan aturan nat chain srcnat",
        "periksa status masquerade pada ether1",
        "lihat konfigurasi nat sharing internet",
        "tampilkan daftar aturan port forwarding aktif",
        "cek konfigurasi dst-nat router",
        "lihat pemetaan port forwarding yang berjalan",
        "periksa aturan forwarding port publik ke server lokal",
        "tampilkan tabel destination nat aktif",
        "inspeksi rule port forwarding di firewall nat",
        "cek status redirect port pada nat",
        "lihat pemetaan virtual server pada nat",
        "periksa daftar forwarding port 8080",
        "tampilkan konfigurasi dst-nat port 2222",
        "cek aturan nat pada interface ether1",
        "lihat konfigurasi masquerade port eth 1",
        "periksa status nat untuk kabel lan 1",
        "apakah ada aturan nat pada colokan 1",
        "tampilkan konfigurasi sharing internet wan ether1",
        "cek rule nat masquerade jalur 1",
        "lihat status nat antarmuka iface 1",
        "periksa konfigurasi masquerade port lan 1",
        "cek aturan nat pada link 1",
        "tampilkan parameter masquerade antarmuka int 1",
        # Type 2: Colloquial / Lab Slang (sharing inet, nyala/mati, forward port)
        "apakah internet nat sedang aktif",
        "nat internet udah nyala belum sih",
        "cek status masquerade nat sekarang",
        "sharing internet udah jalan belum",
        "apakah masquerade wan lagi nyala",
        "koneksi nat internet aktif gak",
        "cek dong nat router lagi hidup gak",
        "apakah lab udah dapet sharing internet",
        "masquerade ether1 udah aktif belum",
        "status internet nat gimana sekarang",
        "cek port forwarding lagi jalan gak",
        "server lokal udah di-forward belum port-nya",
        "ada port forwarding apa aja yang aktif",
        "cek apakah port 8080 udah diarahkan ke server",
        "port 2222 udah diteruskan ke pc lokal belum",
        "lihat daftar port yang di-forward dong",
        "cek aturan forward port web server",
        "port forwarding ke server lab aktif gak",
        "apakah ada port luar yang diarahkan ke dalam",
        "lihat daftar mapping port sekarang",
        "colokan 1 lagi aktif nat-nya gak",
        "apakah jalur 1 udah dipasang masquerade",
        "port 1 udah nyambung nat internet belum",
        "cek sharing internet di kabel lan 1",
        "apakah eth 1 udah ada masquerade-nya",
        "lan 1 internet nat-nya jalan gak",
        "cek masquerade colokan kabel 1 dong",
        "apakah link wan 1 udah di-nat",
        "jalur internet port 1 aktif gak nat-nya",
        "colokan internet wan udah ada masquerade belum",
        # Type 3: Descriptive & Interrogative
        "apakah jaringan lokal sudah bisa mengakses internet via nat",
        "bagaimana status translasi alamat jaringan saat ini",
        "tampilkan ringkasan konfigurasi gateway internet",
        "periksa apakah fitur berbagi koneksi internet sedang berjalan",
        "lihat kondisi operasional masquerade gateway router",
        "tampilkan informasi alur translasi ip lokal ke publik",
        "apakah ada pemetaan port eksternal ke internal yang aktif",
        "lihat status keterhubungan gateway nat",
        "periksa apakah router mengizinkan akses internet keluar via masquerade",
        "tampilkan laporan status network address translation"
    ]
}


def run_expansion():
    # 1. Load current dataset
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Dataset awal: {len(dataset)} sampel.")

    # 2. Check each intent has exactly 70 unique samples
    for intent, samples in new_samples_980.items():
        assert len(samples) == 70, f"{intent} harus tepat 70 sampel, dapat {len(samples)}"
        lower_samples = [s.lower().strip() for s in samples]
        assert len(set(lower_samples)) == 70, f"{intent} ada duplikasi internal!"

    # 3. Check no collision with existing dataset
    existing_texts = {item["text"].lower().strip() for item in dataset}
    for intent, samples in new_samples_980.items():
        for s in samples:
            assert s.lower().strip() not in existing_texts, f"Tabrakan dengan dataset lama: {s}"

    # 4. Append new samples
    # ponytail: append sequentially to preserve order, upgrade path: random seed shuffle before training
    for intent, samples in new_samples_980.items():
        for s in samples:
            dataset.append({"text": s, "intent": intent})

    print(f"Dataset baru setelah penambahan: {len(dataset)} sampel.")

    # 5. Verify total count and class balance
    counts = Counter(item["intent"] for item in dataset)
    print("\nDistribusi Kelas Akhir (14 Kelas):")
    for intent, cnt in sorted(counts.items()):
        print(f"  {intent:22}: {cnt} sampel")
        assert cnt == 70, f"Inbalance: {intent} memiliki {cnt} sampel (wajib 70)"

    assert len(dataset) == 980, f"Total sampel harus 980, dapat {len(dataset)}"
    assert len(counts) == 14, f"Total kelas harus 14, dapat {len(counts)}"

    # 6. Write back to dataset_intent.json
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"\nBerhasil memperbarui {DATASET_PATH} menjadi 980 sampel seimbang!")


if __name__ == "__main__":
    run_expansion()
