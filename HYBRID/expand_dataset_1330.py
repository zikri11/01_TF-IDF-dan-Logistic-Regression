"""
Dataset Expander: 1,120 -> 1,330 balanced samples (19 intent classes x 70 samples).
Adds exactly 70 samples each for:
- ping_host (ICMP reachability & latency diagnostics)
- flush_dns_cache (DNS resolver cache clearing)
- get_system_health (Router CPU/RAM/Uptime hardware monitoring)
Following NIT dataset prompt taxonomy (Technical, Colloquial, Descriptive).
"""

import json
from collections import Counter
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "dataset_intent.json"

new_samples_1330 = {
    "ping_host": [
        # Type 1: Technical (ping, icmp, count, target IP/domain)
        "ping 8.8.8.8",
        "ping host 192.168.88.254",
        "ping google.com count 4",
        "ping ke ip 192.168.88.10",
        "jalankan tes ping ke gateway 192.168.88.1",
        "lakukan uji icmp ping ke 1.1.1.1",
        "ping server dns 8.8.4.4",
        "tes konektivitas ping ke cloudflare.com",
        "lakukan ping sebanyak 4 kali ke 192.168.1.1",
        "kirim paket icmp echo ke 192.168.88.50",
        "ping domain unsil.ac.id",
        "ping ip public 103.10.10.1",
        "tes konektivitas icmp ke 10.10.10.1",
        "ping host web 192.168.88.20",
        "lakukan perintah ping ke 8.8.8.8",
        "ping ke server 192.168.88.100",
        "kirim ping icmp ke gateway internet",
        "jalankan icmp check ke 1.1.1.1",
        "ping host server 192.168.88.30",
        "ping ke alamat 192.168.88.40",
        "tes ping ke domain github.com",
        "lakukan ping test ke host 192.168.88.60",
        "ping ip target 192.168.88.70",
        "kirim 4 paket ping ke 8.8.8.8",

        # Type 2: Colloquial (santai, gaul mahasiswa lab, cek nyambung)
        "coba ping ke 8.8.8.8 dong",
        "tes koneksi ke google.com",
        "cek apakah server 192.168.88.50 nyambung",
        "coba ping laptop 192.168.88.20",
        "tes ping ke server lab dong",
        "coba tes nyambung gak ke 1.1.1.1",
        "ping dulu ip 192.168.88.99",
        "tes koneksi internet ping 8.8.8.8",
        "coba ping gateway kampus",
        "cek latensi ping ke 8.8.4.4",
        "tes rtt ping ke server dns",
        "coba tembak ping ke 192.168.88.15",
        "tes ping ke server mikrotik",
        "coba ping ip temen 192.168.88.45",
        "pingin tau nyambung gak ke google",
        "coba pingin ke ip 192.168.88.33",
        "tes ping dong ke detik.com",
        "cek koneksi rtt ke 8.8.8.8",
        "coba ping alamat 192.168.88.12",
        "tes konektivitas jaringan ke 1.1.1.1",
        "coba ping ke server ubuntu",
        "tes apakah host 192.168.88.55 hidup",
        "ping dulu ke 192.168.88.254",

        # Type 3: Descriptive & Analytical (uji keterjangkauan, paket rtt, reachability)
        "uji keterjangkauan host 192.168.88.50 dengan icmp",
        "periksa respon jaringan dari host 8.8.8.8",
        "uji latency rtt ke server google.com",
        "cek status keterhubungan server 192.168.88.20 via ping",
        "lakukan pengukuran waktu respon paket ke 1.1.1.1",
        "evaluasi keterjangkauan ip 192.168.88.10 dengan ping",
        "uji apakah host 192.168.88.80 aktif di jaringan",
        "inspeksi packet loss ke gateway 192.168.88.1",
        "ukur rtt koneksi ke cloudflare 1.1.1.1",
        "uji reachability server database 192.168.88.40",
        "analisis waktu transmisi icmp ke 8.8.8.8",
        "periksa stabilitas ping ke ip server",
        "verifikasi respon icmp dari 192.168.88.200",
        "uji kelancaran paket ke domain unsil.ac.id",
        "ukur latency ping ke server pusat 192.168.88.250",
        "uji keterhubungan perangkat 192.168.88.15 via icmp echo",
        "periksa apakah ip 192.168.88.75 merespon paket",
        "cek kualitas koneksi rtt ke gateway mikrotik",
        "lakukan diagnosa keterjangkauan jaringan ke 8.8.8.8",
        "verifikasi keterhubungan rute ke 1.0.0.1",
        "uji performa paket icmp ke host lab",
        "periksa respon ping host 192.168.88.18",
        "evaluasi kestabilan latency ke server 192.168.88.22",
    ],

    "flush_dns_cache": [
        # Type 1: Technical (flush, dns cache, resolver, clear cache)
        "flush dns cache",
        "flush cache dns",
        "ip dns cache flush",
        "bersihkan dns cache",
        "bersihkan cache dns router",
        "hapus seluruh cache dns mikrotik",
        "kosongkan tabel cache dns",
        "clear dns cache",
        "lakukan flush pada resolver dns",
        "reset cache dns di router",
        "hapus rekaman cache dns",
        "bersihkan temporary record dns",
        "flush data resolver cache dns",
        "hapus entri cache dns mikrotik",
        "kosongkan memori rekaman dns",
        "jalankan pembersihan cache dns",
        "bersihkan riwayat cache domain dns",
        "flush seluruh rekaman dns",
        "hapus daftar cache dns yang tersimpan",
        "lakukan reset pada cache dns",
        "clear resolver dns cache sekarang",
        "bersihkan tabel resolver dns",
        "hapus riwayat query cache dns",
        "flush tabel ip dns cache",

        # Type 2: Colloquial (santai, gaul lab, reset domain, bersihin dns)
        "bersihin cache dns dong",
        "reset dns cache nya",
        "hapus cache domain di router",
        "tolong flush dns mikrotik",
        "bersihkan riwayat dns router",
        "buang semua cache dns",
        "kosongin cache dns mikrotik",
        "reset rekaman domain dns dong",
        "bersihin riwayat domain yang kesimpan",
        "flush dns nya sekarang ya",
        "hapus cache nama domain di router",
        "bersihkan data dns mikrotik",
        "refresh cache dns dong",
        "reset cache lookup domain",
        "tolong hapus seluruh rekaman dns",
        "bersihin cache resolver dns",
        "kosongkan cache pencarian domain",
        "hapus riwayat lookup dns",
        "reset penyimpanan cache dns",
        "buang rekaman ip domain di dns",
        "tolong bersihkan dns cache router",
        "flush cache alamat domain sekarang",
        "hapus sisa cache dns mikrotik",

        # Type 3: Descriptive & Analytical (pemeliharaan resolver, sinkronisasi record)
        "lakukan pembersihan total rekaman cache resolver dns",
        "reset memori penyimpanan riwayat domain dns",
        "kosongkan seluruh entri resolver pada ip dns cache",
        "hapus data cache nama domain untuk memperbarui record",
        "sinkronkan ulang resolusi domain dengan membersihkan cache dns",
        "lakukan operasi flush rekaman domain yang tersimpan di memori",
        "bersihkan riwayat entri dns routeros untuk mencegah stale ip",
        "segarkan kembali tabel resolusi nama domain via flush cache",
        "kosongkan tabel resolver dns agar memuat ip domain terbaru",
        "perbarui entri resolver dns dengan menghapus cache tersimpan",
        "lakukan reset berkala pada memori cache dns router",
        "hapus seluruh database cache resolver di mikrotik",
        "bersihkan cache translasi domain ke ip pada router",
        "perbarui cache dns mikrotik dengan membuang entri lama",
        "lakukan flush entri domain kadaluarsa di cache dns",
        "kosongkan memori resolver ip dns cache untuk troubleshooting",
        "bersihkan seluruh rekaman sementara domain pada router",
        "lakukan purges pada cache resolver dns mikrotik",
        "reset histori lookup ip dns cache sistem",
        "bersihkan buffer cache dns routeros",
        "lakukan tindakan flush database cache domain",
        "kosongkan riwayat resolusi host pada dns cache",
        "bersihkan seluruh rekaman ip dns resolver sekarang",
    ],

    "get_system_health": [
        # Type 1: Technical (system resource, cpu load, free memory, ram, uptime, board)
        "system resource print",
        "cek system resource router",
        "tampilkan system resource",
        "cek beban cpu router",
        "tampilkan sisa ram router",
        "cek kapasitas memori bebas",
        "lihat status uptime mikrotik",
        "tampilkan penggunaan cpu dan ram",
        "cek spesifikasi hardware router",
        "inspeksi resource hardware mikrotik",
        "lihat beban kerja prosesor mikrotik",
        "tampilkan informasi board name dan cpu",
        "cek persentase cpu load router",
        "lihat kapasitas free memory mikrotik",
        "tampilkan data resource perangkat keras",
        "cek kesehatan sistem router",
        "lihat informasi frekuensi cpu router",
        "tampilkan free hdd space mikrotik",
        "cek status kesehatan hardware mikrotik",
        "tampilkan parameter sistem resource",
        "lihat kondisi prosesor dan ram router",
        "cek arsitektur cpu dan versi routeros",
        "tampilkan telemetri hardware router",
        "lihat ringkasan sumber daya perangkat keras",

        # Type 2: Colloquial (santai, cek kondisi router, ngos-ngosan gak, ram sisa berapa)
        "cek kondisi router dong",
        "mikrotik lagi berat gak ya",
        "sisa ram router tinggal berapa",
        "router mikrotik udah nyala berapa lama",
        "cek beban cpu router sekarang",
        "cpu router lagi tinggi gak sih",
        "gimana kesehatan hardware mikrotik",
        "tampilkan sisa memori router dong",
        "cek performa hardware router",
        "apakah router lagi overload",
        "lihat kondisi memori ram mikrotik",
        "cek apakah cpu mikrotik lagi kepanasan",
        "lihat router udah aktif berapa hari",
        "ram mikrotik masih lega gak",
        "cek kesehatan mesin router",
        "gimana kondisi prosesor mikrotik saat ini",
        "apakah memori router mau habis",
        "cek status hardware mikrotik dong",
        "lihat spesifikasi dan beban router",
        "apakah cpu load router aman",
        "cek apakah router ngos-ngosan",
        "tampilkan info ram dan cpu router",
        "lihat sisa ruang penyimpanan mikrotik",

        # Type 3: Descriptive & Analytical (monitoring performa, audit beban sumber daya)
        "lakukan audit beban sumber daya cpu dan memori router",
        "pantau statistik kinerja hardware dan persentase utilisasi cpu",
        "analisis sisa kapasitas memori ram pada router hAP lite",
        "periksa waktu operasional uptime dan kestabilan perangkat router",
        "evaluasi pemakaian memori bebas dan beban prosesor perangkat keras",
        "inspeksi telemetri sumber daya sistem operasi routeros",
        "laporkan kondisi utilisasi prosesor dan ketersediaan memori sistem",
        "monitoring beban komputasi dan ruang penyimpanan router",
        "periksa metrik kesehatan sistem dan ketahanan hardware router",
        "analisis tingkat pembebanan prosesor mikrotik secara berkala",
        "tampilkan laporan diagnostik kesehatan sumber daya perangkat",
        "inspeksi rasio penggunaan memori ram terhadap total kapasitas",
        "evaluasi apakah router memerlukan optimasi sumber daya memori",
        "pantau telemetri hardware router untuk memastikan performa stabil",
        "lakukan verifikasi status operasional uptime dan cpu load",
        "periksa kapasitas penyimpanan disk dan ketersediaan memori utama",
        "laporkan statistik sumber daya perangkat keras mikrotik",
        "analisis kesehatan prosesor dalam menangani beban jaringan",
        "inspeksi ketersediaan memori fisik pada router hAP lite",
        "pantau integritas operasional dan performa hardware sistem",
        "evaluasi statistik beban kerja routeros dan durasi aktif",
        "periksa laporan kinerja komputasi dan sisa memori sistem",
        "lakukan diagnosa kesehatan perangkat keras router mikrotik",
    ],
}


def expand_dataset():
    print(f"Membaca dataset eksisting dari: {DATASET_PATH}")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    initial_count = len(data)
    initial_counts = Counter(item["intent"] for item in data)
    print(f"Total sampel awal: {initial_count} ({len(initial_counts)} kelas)")

    existing_texts = {item["text"].strip().lower() for item in data}

    added_count = 0
    for intent, sentences in new_samples_1330.items():
        print(f"\nMemproses kelas '{intent}' (target: 70 sampel unik)...")
        assert len(sentences) == 70, f"Jumlah sampel untuk {intent} harus tepat 70, didapat: {len(sentences)}"

        intent_added = 0
        for text in sentences:
            clean_text = text.strip()
            norm = clean_text.lower()
            if norm in existing_texts:
                print(f" [WARNING] Teks duplikat terdeteksi: '{clean_text}'")
                continue
            data.append({"text": clean_text, "intent": intent})
            existing_texts.add(norm)
            intent_added += 1
            added_count += 1

        print(f" Berhasil menambahkan {intent_added} sampel baru ke kelas '{intent}'.")

    final_count = len(data)
    final_counts = Counter(item["intent"] for item in data)
    print("\n" + "=" * 60)
    print(f"Total sampel akhir: {final_count} ({len(final_counts)} kelas)")
    print(f"Total sampel baru ditambahkan: {added_count}")
    print("=" * 60)

    # Verifikasi Keseimbangan Kelas (Zero Class Imbalance)
    print("\nDistribusi Per-Kelas:")
    for intent_name, count in sorted(final_counts.items()):
        print(f"  - {intent_name:<22}: {count} sampel")
        assert count == 70, f"Ketidakseimbangan kelas pada '{intent_name}': {count} != 70"

    assert final_count == 1330, f"Total dataset harus tepat 1.330 sampel, didapat: {final_count}"
    assert len(final_counts) == 19, f"Total kelas harus tepat 19 kelas, didapat: {len(final_counts)}"

    # Simpan kembali dataset
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nDataset 1.330 sampel berhasil disimpan ke: {DATASET_PATH}")
    print("STATUS: ZERO CLASS IMBALANCE TERPENUHI (19 KELAS x 70 SAMPEL = 1.330 SAMPEL)!")


if __name__ == "__main__":
    expand_dataset()
