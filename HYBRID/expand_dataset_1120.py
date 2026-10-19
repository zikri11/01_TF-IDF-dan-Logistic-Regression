"""
Dataset Expander: 980 -> 1,120 balanced samples (16 intent classes x 70 samples).
Adds 70 samples each for:
- add_port_forward
- remove_port_forward
Following NIT dataset prompt taxonomy (Technical, Colloquial, Descriptive).
"""

import json
from collections import Counter
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "dataset_intent.json"

new_samples_1120 = {
    "add_port_forward": [
        # Type 1: Technical (dst-nat, port forward, protocol, mapping)
        "forward port 8080 ke server 192.168.88.50 port 80",
        "konfigurasi dst-nat port 2222 diarahkan ke 192.168.88.99 port 22",
        "arahkan port eksternal 8443 ke 192.168.88.20 port 443 protocol tcp",
        "tambahkan aturan port forwarding 5353 ke 192.168.88.15 port 53 udp",
        "buat rule destination nat port 9000 ke host 10.10.10.5 port 9000",
        "forward port 8000 ke ip 192.168.88.35 port 80",
        "petakan port publik 3389 ke server rdp 192.168.88.40 port 3389",
        "konfigurasi port forwarding port 2121 ke ftp server 192.168.88.70 port 21",
        "teruskan trafik port 8088 ke komputer 10.10.20.15 port 8080",
        "atur dst-nat dari port 5000 ke 192.168.88.25 port 5000",
        "pasang port forwarding 80 ke server web 192.168.88.100 port 80",
        "tambahkan mapping port 4433 ke 192.168.88.115 port 443",
        "redirect port 10000 ke host 10.10.30.12 port 80",
        "buat aturan forward port 2200 ke ssh server 192.168.88.135 port 22",
        "forward port luar 8888 ke ip lokal 192.168.88.145 port 8080",
        "petakan port 6000 ke client 10.10.40.18 port 6000 protocol tcp",
        "konfigurasi redirect port 7000 ke host 192.168.88.155 port 7000",
        "tambahkan aturan forward port 9999 ke 10.10.50.25 port 9999",
        "buat pemetaan dst-nat port 4000 ke ip 192.168.88.165 port 4000",
        "forward port 1234 ke host 10.10.60.30 port 1234",
        # Type 2: Colloquial / Lab Slang (lempar, tembusin, arahkan, buka akses)
        "buka port 8080 lempar ke ip 192.168.88.50 port 80",
        "tembusin port 2222 ke server 192.168.88.99",
        "arahkan koneksi port 8443 ke web server lab 192.168.88.20",
        "buka akses port 5353 lempar ke 192.168.88.15",
        "teruskan port luar 9000 ke komputer 10.10.10.5",
        "lempar port 8000 ke laptop 192.168.88.35 port 80",
        "buka jalur port 3389 ke pc 192.168.88.40",
        "forwarding-in port 2121 ke server ftp 192.168.88.70",
        "salurkan port 8088 ke pc 10.10.20.15",
        "tolong arahkan port 5000 ke ip 192.168.88.25",
        "buka port 80 tembusin ke server 192.168.88.100",
        "lempar koneksi port 4433 ke host 192.168.88.115",
        "tolong forward port 10000 ke komputer 10.10.30.12",
        "arahkan trafik port 2200 ke laptop 192.168.88.135",
        "buka akses luar port 8888 ke 192.168.88.145",
        "tembuskan port 6000 ke client 10.10.40.18",
        "salurkan trafik luar port 7000 ke 192.168.88.155",
        "tolong buka port 9999 arahkan ke 10.10.50.25",
        "forward dong port 4000 ke komputer 192.168.88.165",
        "lempar port 1234 ke perangkat 10.10.60.30",
        # Type 3: Descriptive & Variational
        "untuk server 192.168.88.50 tolong forward port 8080",
        "bisa tolong teruskan port 2222 ke komputer 192.168.88.99",
        "tolong buatkan pemetaan port 8443 ke 192.168.88.20",
        "hubungkan port eksternal 5353 dengan internal 192.168.88.15",
        "saya ingin port 9000 diteruskan ke 10.10.10.5",
        "tolong sambungkan port 8000 dari luar ke ip 192.168.88.35",
        "berikan akses port 3389 dari luar ke host 192.168.88.40",
        "buat koneksi port 2121 agar mengarah ke 192.168.88.70",
        "ijinkan akses luar port 8088 masuk ke 10.10.20.15",
        "tolong setel port 5000 tembus ke 192.168.88.25",
        "hubungkan port 80 dari internet ke server lokal 192.168.88.100",
        "bisa tolong arahkan port 4433 ke 192.168.88.115",
        "saya butuh port 10000 diteruskan ke host 10.10.30.12",
        "tolong buka jalur luar port 2200 ke pc 192.168.88.135",
        "arahkan koneksi publik port 8888 ke perangkat 192.168.88.145",
        "berikan akses masuk port 6000 untuk 10.10.40.18",
        "buat aturan agar port 7000 diteruskan ke 192.168.88.155",
        "sambungkan port luar 9999 ke ip 10.10.50.25",
        "tolong hubungkan port 4000 ke komputer lab 192.168.88.165",
        "bisa teruskan port 1234 ke host 10.10.60.30",
        "forward port 8081 ke 192.168.88.51 port 81",
        "forward port 8082 ke 192.168.88.52 port 82",
        "forward port 8083 ke 192.168.88.53 port 83",
        "forward port 8084 ke 192.168.88.54 port 84",
        "forward port 8085 ke 192.168.88.55 port 85",
        "arahkan port 9001 ke 192.168.88.61",
        "arahkan port 9002 ke 192.168.88.62",
        "arahkan port 9003 ke 192.168.88.63",
        "arahkan port 9004 ke 192.168.88.64",
        "arahkan port 9005 ke 192.168.88.65"
    ],
    "remove_port_forward": [
        # Type 1: Technical (hapus dst-nat, cabut port forward, unforward)
        "hapus aturan port forwarding 8080",
        "cabut konfigurasi dst-nat port 2222",
        "hilangkan aturan port forward 8443",
        "hapus pemetaan port forwarding 5353",
        "cabut aturan destination nat port 9000",
        "hapus rule forward port 8000",
        "hilangkan mapping port publik 3389",
        "cabut aturan forwarding port 2121",
        "hapus konfigurasi dst-nat port 8088",
        "hilangkan pemetaan port 5000",
        "cabut aturan port forwarding 80",
        "hapus redirect port 4433",
        "hilangkan rule forward port 10000",
        "cabut pemetaan port 2200",
        "hapus konfigurasi forwarding port 8888",
        "hilangkan aturan dst-nat port 6000",
        "cabut mapping port 7000",
        "hapus aturan forward port 9999",
        "hilangkan aturan redirect port 4000",
        "cabut konfigurasi forward port 1234",
        # Type 2: Colloquial / Lab Slang (tutup forward, lepas lemparan, cut)
        "tutup akses port forwarding 8080",
        "jangan lempar port 2222 lagi",
        "cabut lemparan port 8443",
        "tutup pemetaan port 5353",
        "hentikan forwarding port 9000",
        "tutup jalur port 8000 ke server",
        "lepas forward port 3389 dong",
        "cut akses port forwarding 2121",
        "jangan teruskan port 8088 lagi",
        "tutup akses luar port 5000",
        "hapus forward port 80 ke server lab",
        "lepas pemetaan port 4433",
        "tutup forward port 10000",
        "cabut akses forward port 2200",
        "hentikan penerusan port 8888",
        "lepas jalur forward port 6000",
        "tutup akses forwarding port 7000",
        "cabut lemparan port luar 9999",
        "hapus jalur forward port 4000",
        "hentikan forward port 1234",
        # Type 3: Descriptive & Variational
        "batalkan aturan port forwarding untuk port 8080",
        "tolong batalkan pemetaan port 2222",
        "kembalikan port 8443 agar tidak di-forward",
        "normalkan kembali konfigurasi port 5353",
        "tolong batalkan penerusan port 9000",
        "jangan izinkan lagi forward port 8000",
        "batalkan akses publik untuk port 3389",
        "tolong cabut pembukaan port 2121",
        "kembalikan port 8088 ke kondisi default",
        "reset konfigurasi port forwarding 5000",
        "tolong batalkan forward port 80",
        "hapus aturan yang meneruskan port 4433",
        "jangan teruskan lagi koneksi port 10000",
        "batalkan konfigurasi forwarding port 2200",
        "tolong cabut penerusan port 8888",
        "hapus pemetaan masuk untuk port 6000",
        "batalkan aturan masuk port 7000",
        "tolong jangan forward lagi port 9999",
        "cabut aturan koneksi masuk port 4000",
        "batalkan penerusan trafik port 1234",
        "hapus aturan port forwarding 8081",
        "hapus aturan port forwarding 8082",
        "hapus aturan port forwarding 8083",
        "hapus aturan port forwarding 8084",
        "hapus aturan port forwarding 8085",
        "cabut forward port 9001",
        "cabut forward port 9002",
        "cabut forward port 9003",
        "cabut forward port 9004",
        "cabut forward port 9005"
    ]
}


def run_expansion():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Dataset awal: {len(dataset)} sampel.")

    for intent, samples in new_samples_1120.items():
        assert len(samples) == 70, f"{intent} harus tepat 70 sampel, dapat {len(samples)}"
        lower_samples = [s.lower().strip() for s in samples]
        assert len(set(lower_samples)) == 70, f"{intent} ada duplikasi internal!"

    existing_texts = {item["text"].lower().strip() for item in dataset}
    for intent, samples in new_samples_1120.items():
        for s in samples:
            assert s.lower().strip() not in existing_texts, f"Tabrakan dengan dataset lama: {s}"

    # ponytail: append sequentially to preserve order, upgrade path: random seed shuffle before training
    for intent, samples in new_samples_1120.items():
        for s in samples:
            dataset.append({"text": s, "intent": intent})

    print(f"Dataset baru setelah penambahan: {len(dataset)} sampel.")

    counts = Counter(item["intent"] for item in dataset)
    print("\nDistribusi Kelas Akhir (16 Kelas):")
    for intent, cnt in sorted(counts.items()):
        print(f"  {intent:22}: {cnt} sampel")
        assert cnt == 70, f"Inbalance: {intent} memiliki {cnt} sampel (wajib 70)"

    assert len(dataset) == 1120, f"Total sampel harus 1120, dapat {len(dataset)}"
    assert len(counts) == 16, f"Total kelas harus 16, dapat {len(counts)}"

    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"\nBerhasil memperbarui {DATASET_PATH} menjadi 1.120 sampel seimbang (16 kelas x 70 sampel)!")


if __name__ == "__main__":
    run_expansion()
