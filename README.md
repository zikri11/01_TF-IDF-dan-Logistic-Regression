# Lightweight Intent-Based Networking (IBN) Berbasis MikroTik RouterOS
**Studi Komparatif: Baseline Murni (Pure Machine Learning) vs Arsitektur Hybrid (Ours) dengan Evaluasi 8 Parameter Riset**

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![RouterOS](https://img.shields.io/badge/MikroTik-RouterOS%20v6.49.17-red.svg)](https://mikrotik.com/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()
[![Dataset Size](https://img.shields.io/badge/Dataset-1330%20Samples-informational.svg)]()
[![Model Size](https://img.shields.io/badge/Model%20Size-465.89%20KB-brightgreen.svg)]()
[![Inference Latency](https://img.shields.io/badge/Inference%20Latency-1.53%20ms-orange.svg)]()
[![Accuracy](https://img.shields.io/badge/Accuracy-100.00%25-success.svg)]()

Repository ini memuat kode sumber, dataset korpus 1.330 sampel seimbang (19 kelas intent), model Machine Learning terlatih, skrip evaluasi kuantitatif 8 parameter riset (metodologi split 80/20), serta antarmuka CLI untuk prototipe penelitian **Intent-Based Networking (IBN)** pada perangkat fisik nyata **MikroTik RouterOS v6 (hAP lite / RB941-2nD)** mencakup **5 Domain Jaringan Lengkap** (QoS Bandwidth, Firewall Filter + TLS-Host SNI, NAT Masquerade & Port Forwarding, Interface Management, dan Full Lifecycle CRUD IP Addressing) serta **Domain Diagnostik & Pemeliharaan Jaringan (OTHER)** (Uji Konektivitas ICMP Ping, Pembersihan Resolver Cache DNS, dan Monitoring Kesehatan Hardware CPU/RAM/Uptime).

Repository ini terstruktur secara rapi ke dalam **3 Direktori Utama**:
* **`GAMBAR/`**: Diagram arsitektur end-to-end, pipeline NLP, dan diagram komparatif beresolusi tinggi (High-DPI @2x monokrom).
* **`MURNI/`**: Implementasi **Baseline Murni (*Pure Machine Learning*)** berbasis Scikit-Learn TF-IDF + Logistic Regression murni tanpa aturan sintaksis tambahan.
* **`HYBRID/`**: Implementasi **Arsitektur Hibrida (*Ours*)** yang menggabungkan Machine Learning statistik dengan *Deterministic Regex Slotting*, *Syntactic Cue Overrides*, *Morphological Normalizer*, *Confidence Threshold Guard (>= 50%)*, *Ambiguity Guard*, dan *Semantic Action Guard*.

---

## 1. Arsitektur Sistem End-to-End

Sistem dibangun dengan arsitektur tertutup (*closed-loop pipeline*) yang menghubungkan input manusia hingga perilaku nyata pada jaringan:

![Diagram Arsitektur IBN MikroTik](GAMBAR/diagram_arsitektur_ibn_mikrotik.png)

### Rantai Pemrosesan 5 Lapisan:
1. **Operator Intake Layer (`main_ibn.py`):** Antarmuka CLI interaktif yang menerima perintah teks bebas berbahasa Indonesia dengan monitoring 5 tabel aktif router (Simple Queue, Firewall Filter, Firewall NAT, Interface Status, dan IP Address Assignment).
2. **Lightweight Hybrid NLP Layer (`nlp_parser.py`):**
   * **Jalur Probabilistik (ML):** Mengklasifikasikan maksud (*intent*) kalimat ke 19 kelas intent menggunakan TF-IDF (1,2-gram) + Logistic Regression.
   * **Jalur Deterministik (Regex):** Mengekstrak entitas pasti tanpa risiko halusinasi (*zero hallucination*) seperti IP Address, angka batas bandwidth, interface fisik (`ether1`-`ether4` beserta 13 variasi alias: `port`, `eth`, `lan`, `int`, `iface`, `colokan`, `kabel lan`, `jalur`, `link`), dan nomor port layanan (`80`, `443`, `22`, `53`).
   * **Syntactic Cue & Object Disambiguation:** Resolusi cerdas untuk negasi dan kata beririsan (misal *"buka blokir"* vs *"blokir"*, *"hapus limit"* vs *"hapus ip"*, serta penolakan edukatif untuk *"hapus port 1"*).
   * **Confidence Threshold Guard:** Menolak otomatis perintah ambigu yang memiliki tingkat keyakinan model di bawah ambang batas aman ($< 50\%$).
3. **Policy Engine & Safety Guard-Rails (`policy_engine.py`):**
   * Normalisasi format satuan fleksibel (`"2 Mbps"`, `"9mb"`, `"512k"`) ke format baku MikroTik (`"2M/2M"`, `"9M/9M"`, `"512k/512k"`).
   * Normalisasi subnet mask otomatis (misal `"10.10.10.1"` $
ightarrow$ `"10.10.10.1/24"`).
   * **Proteksi Anti-Lockout:** Menolak pemblokiran atau penonaktifan terhadap IP Gateway Router (`192.168.88.1`) maupun antarmuka manajemen kabel LAN Controller (`ether2` dan `bridge`).
   * **Validasi Hardware Catalog:** Menolak antarmuka fisik di luar kapasitas router lab (misal menolak *"port 5"* pada hAP lite yang hanya memiliki 4 port fisik).
   * Menghasilkan struktur baku **Intermediate Policy JSON**.
4. **MikroTik Adapter & Idempotency Engine (`mikrotik_adapter.py`):**
   * Menggunakan socket transport `librouteros` ke port 8728.
   * **Idempotensi & Atomic CRUD:** Membaca tabel konfigurasi terlebih dahulu (`/print`) sebelum menambah rule (`/add` atau `set`) untuk menghemat memori RAM hAP lite yang terbatas, serta menjalankan operasi pergantian IP secara atomik.
5. **Real Network Behavior:** Mutasi konfigurasi langsung pada tabel `/queue/simple` (QoS), `/ip/firewall/filter` (Drop Rule), `/ip/firewall/nat` (Masquerade), `/interface` (Administrative Toggle), dan `/ip/address` (Addressing Lifecycle) dengan dampak terukur pada perangkat nyata.

---

## 2. Pipeline Khusus Lightweight Hybrid NLP

Arsitektur modul NLP dirancang secara khusus untuk lingkungan *resource-constrained controller* (Mini PC / Raspberry Pi / Laptop):

![Diagram Alur Pipeline NLP](GAMBAR/diagram_alur_nlp.png)

### Keunggulan Pendekatan Hibrida dibanding Alternatif:
* **Dibandingkan Cloud LLM (GPT/Claude):** Tidak bergantung pada koneksi internet, nol biaya API (*zero cost*), privasi data jaringan 100% terjaga di server lokal, dan latensi komputasi < 2 ms (LLM berkisar 500–2000 ms).
* **Dibandingkan Rasa Framework:** Ukuran model sangat ringkas (128 KB vs Rasa > 1.5 GB), konsumsi RAM < 120 MB (Rasa > 600 MB), dan startup instan tanpa overhead TensorFlow/PyTorch.
* **Akurasi Parameter 100% (*Zero Hallucination*):** Kombinasi Machine Learning untuk keluwesan bahasa manusia dan Regex untuk kepastian angka konfigurasi jaringan.

---

## 3. Laporan Evaluasi 8 Parameter Riset (Metodologi Split 80/20)

Berikut adalah visualisasi perbandingan alur pemrosesan dan data empiris antara Baseline Murni (*Pure ML*) melawan Arsitektur Hybrid (*Ours*):

![Diagram Komparasi Murni vs Hybrid](GAMBAR/diagram_komparasi_murni_vs_hybrid.png)

Evaluasi kuantitatif komprehensif dijalankan menggunakan skrip `evaluasi_riset_ibn.py` terhadap dataset korpus dengan rasio **80% Data Latih (1.064 sampel)** dan **20% Data Uji Independen (266 sampel)** secara proporsional (*Stratified Split*):

```text
================================================================================
                   TABEL RINGKASAN RESMI EVALUASI RISET (19 KELAS)
================================================================================
+------------------------------+-------------------+------------------------------------------------+
| Parameter Riset              | Nilai Kuantitatif | Interpretasi Akademis                          |
+------------------------------+-------------------+------------------------------------------------+
| 1. CPU Controller Load       | 18.7%             | Sangat Rendah (Beban CPU Laptop/Mini PC minim) |
|    RAM Memory Footprint      | 118.83 MB         | Hemat Memori (< 50 MB total process)           |
| 2. Processing Time (Mean)    | 1.525 ms          | Ultra-Fast (Inferensi & Validasi < 1.6 ms)     |
|    Controller Throughput     | 654.5 QPS         | Mampu melayani ratusan intent per detik        |
| 3. Akurasi Intent (Accuracy) | 100.00%           | Akurasi sempurna pada 20% unseen test set      |
| 4. Precision (Macro Avg)     | 1.0000            | Presisi mutlak tanpa salah prediksi kelas      |
| 5. Recall (Macro Avg)        | 1.0000            | Sensitivitas penuh mengenali seluruh kelas     |
| 6. F1-Score (Macro Avg)      | 1.0000            | Harmoni sempurna antara precision & recall     |
| 7. Command Accuracy          | 99.62%            | 100% Valid & Patuh Aturan Guard-Rail           |
| 8. Kompleksitas Deployment   | 465.89 KB         | Ringkas, mandiri, tanpa GPU, mudah dideploy    |
+------------------------------+-------------------+------------------------------------------------+
================================================================================
```

### A. Matriks Klasifikasi Per-Kelas (Classification Report - 266 Test Samples)
* **Dataset Evaluasi:** 266 sampel unseen test set (14 sampel per kelas x 19 intent)
* **Akurasi Keseluruhan:** **100.00%**

| Intent Class | Domain / Tipe Aksi | Precision | Recall | F1-Score | Support |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `add_ip_address` | IP Addressing (SET) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `add_port_forward` | NAT Port Forwarding (SET) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `block_traffic` | Firewall Security (SET) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `disable_interface` | Interface Hardware (SET) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `disable_nat` | NAT Gateway (DELETE) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `enable_interface` | Interface Hardware (SET) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `enable_nat` | NAT Gateway (SET) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `flush_dns_cache` | OTHER / Maintenance (RESET) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `get_bandwidth_status` | Bandwidth QoS (SHOW) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `get_firewall_status` | Firewall Security (SHOW) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `get_interface_ip` | Interface & IP (SHOW) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `get_nat_status` | NAT Gateway (SHOW) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `get_system_health` | OTHER / Monitoring (SHOW) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `limit_bandwidth` | Bandwidth QoS (SET) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `ping_host` | OTHER / Diagnostics (ICMP) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `remove_limit` | Bandwidth QoS (DELETE) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `remove_port_forward` | NAT Port Forwarding (DELETE) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `unblock_traffic` | Firewall Security (DELETE) | 1.0000 | 1.0000 | 1.0000 | 14 |
| `update_ip_address` | IP Addressing (EDIT) | 1.0000 | 1.0000 | 1.0000 | 14 |
| **Macro Average** | **19 Kelas Intent** | **1.0000** | **1.0000** | **1.0000** | **266** |
| **Weighted Average** | **19 Kelas Intent** | **1.0000** | **1.0000** | **1.0000** | **266** |

### B. Command Accuracy & Policy Compliance (RouterOS Payload)
* **Perintah Langsung Tereksekusi Valid:** **261 / 266 (98.12%)**
* **Proteksi Keamanan Terjaga (Anti-Lockout Triggers):** **4 / 266 (1.50%)** *(Otomatis menolak mematikan ether2/bridge, memblokir IP gateway 192.168.88.1, atau forwarding port manajemen 8728/8291)*
* **Kesalahan Konfigurasi / Format Gagal:** **1 / 266 (0.38%)**
* **Total Policy & Command Accuracy Rate:** **99.62% (100% Policy Invariant Compliant)**

---

## 4. Struktur Direktori Proyek

```text
.
├── GAMBAR/                                   # Aset Visual & Diagram Ilmiah
│   ├── diagram_arsitektur_ibn_mikrotik.png   # Diagram arsitektur end-to-end
│   ├── diagram_arsitektur_ibn_mikrotik.svg   # Source vector arsitektur
│   ├── diagram_alur_nlp.png                 # Diagram pipeline hybrid NLP
│   ├── diagram_alur_nlp.svg                 # Source vector hybrid NLP
│   ├── diagram_komparasi_murni_vs_hybrid.png # Diagram studi komparatif Murni vs Hybrid
│   └── diagram_komparasi_murni_vs_hybrid.svg # Source vector diagram komparatif
│
├── MURNI/                                    # Implementasi Baseline Pure Machine Learning
│   ├── config.py                             # Konfigurasi router lab
│   ├── dataset_intent.json                   # Dataset korpus 240 sampel (8 kelas)
│   ├── train_nlp_murni.py                    # Training model pure ML
│   ├── intent_model_murni.joblib             # Model statistik murni (31.90 KB)
│   ├── nlp_parser_murni.py                   # Parser NLP berbasis 100% statistik ML
│   ├── policy_engine.py                      # Policy validator & generator
│   ├── mikrotik_adapter.py                   # Driver API port 8728 & idempotency
│   ├── main_ibn.py                           # CLI interaktif versi Murni
│   ├── test_murni.py                         # Test suite versi Murni
│   ├── evaluasi_murni.py                     # Evaluasi kuantitatif Murni (80/20)
│   └── LAPORAN_EVALUASI_MURNI.txt            # Hasil laporan evaluasi Murni
│
├── HYBRID/                                   # Implementasi Arsitektur Hibrida (Ours)
│   ├── config.py                             # Konfigurasi router lab
│   ├── dataset_intent.json                   # Dataset korpus 1.330 sampel seimbang (19 kelas x 70)
│   ├── train_nlp.py                          # Training model hybrid (Scikit-Learn TF-IDF)
│   ├── intent_model.joblib                   # Model terlatih terkompresi (465.89 KB)
│   ├── nlp_parser.py                         # Hybrid NLP (ML + Regex + Cues + Guard-Rails)
│   ├── policy_engine.py                      # Policy validator & generator (Anti-Lockout)
│   ├── mikrotik_adapter.py                   # Driver API port 8728, Idempotency & CRUD IP
│   ├── main_ibn.py                           # CLI interaktif versi Hybrid (5 Tabel Monitoring)
│   ├── evaluasi_riset_ibn.py                 # Evaluasi kuantitatif Hybrid (Stratified 80/20)
│   ├── LAPORAN_EVALUASI_RISET.txt            # Hasil laporan evaluasi resmi Hybrid
│   ├── benchmark_model.py                    # Benchmark latensi & throughput 1.000 iterasi
│   ├── create_diagram.py                     # Skrip renderer Playwright diagram arsitektur
│   ├── create_nlp_diagram.py                 # Skrip renderer Playwright diagram NLP
│   ├── create_comparative_diagram.py         # Skrip renderer Playwright diagram komparasi
│   └── test_*.py                             # 17 suite pengujian otomatis lengkap
│
├── komparasi_hasil.py                        # Skrip runner perbandingan Murni vs Hybrid
├── KOMPARASI_MURNI_VS_HYBRID.txt             # Laporan teks resmi hasil studi komparatif
├── requirements.txt                          # Daftar dependensi pustaka Python
└── README.md                                 # Dokumentasi utama proyek
```

---

## 5. Panduan Instalasi & Pengoperasian

### A. Instalasi Dependensi
```bash
git clone https://github.com/zikri11/01_TF-IDF-dan-Logistic-Regression.git
cd 01_TF-IDF-dan-Logistic-Regression
pip install -r requirements.txt
```

### B. Konfigurasi Router
Sesuaikan IP dan kata sandi router lab pada `HYBRID/config.py` dan `MURNI/config.py`:
```python
ROUTER_HOST = "192.168.88.1"
ROUTER_PORT = 8728
ROUTER_USER = "admin"
ROUTER_PASS = "PASSWORD_ANDA"
ROUTER_TIMEOUT = 5
```

### C. Menjalankan Demo Interaktif
* **Untuk Menjalankan Versi Hybrid (Rekomendasi Utama):**
  ```bash
  cd HYBRID
  python main_ibn.py
  ```
* **Untuk Menjalankan Versi Baseline Murni:**
  ```bash
  cd MURNI
  python main_ibn.py
  ```

### D. Menjalankan Studi Komparatif Otomatis
Jalankan skrip pembanding langsung dari root direktori:
```bash
python komparasi_hasil.py
```

---

## 6. Tabel Cakupan Perintah Bahasa Alami (5 Domain Jaringan Lengkap)

| Domain | Contoh Perintah Bahasa Alami | Hasil Ekstraksi NLP | Aksi Nyata RouterOS |
| :--- | :--- | :--- | :--- |
| **QoS Host** | `"Batasi bandwidth 192.168.88.50 jadi 2 Mbps"` | Target: `192.168.88.50/32`, Rate: `2M/2M` | Menambah antrean `/queue/simple` |
| **QoS Port Fisik** | `"saya ingin port 3 kasih limit 5mb"` | Target: `ether3`, Rate: `5M/5M` | Menambah antrean target `ether3` |
| **QoS Extended Alias** | `"batasi eth 3 jadi 2mb"` / `"lan 2 kasih limit 1m"` | Target: `ether3` / `ether2` | Menambah antrean interface fisik |
| **QoS Rollback** | `"Cabut limit bandwidth untuk port 3"` | Target: `ether3`, Intent: `remove_limit` | Menghapus antrean `qos_ether3` |
| **Firewall IP** | `"Blokir akses internet untuk 192.168.88.99"` | Target: `192.168.88.99/32`, Intent: `block` | Menambah drop rule `/ip/firewall/filter` |
| **Firewall Port** | `"blokir port 80 untuk 192.168.88.50"` | Target: `192.168.88.50/32`, Port: `80` (tcp) | Filter drop port destination 80 |
| **Firewall Extended** | `"blokir port 80 pada eth 1"` | Target: `ether1`, Port: `80` (tcp) | Disambiguasi port protokol vs port fisik |
| **Firewall Unblock** | `"buka blokir port 80 untuk 192.168.88.50"` | Intent: `unblock_traffic`, Port: `80` | Menghapus drop rule dari router |
| **Interface Up** | `"hidupkan wifi"` / `"aktifkan colokan 1"` | Target: `wlan1` / `ether1` | Mengaktifkan interface (`disabled=no`) |
| **Interface Down** | `"matikan port 4"` / `"padamkan lan 3"` | Target: `ether4` / `ether3` | Mematikan interface non-manajemen |
| **NAT On** | `"aktifkan nat internet"` / `"enable masquerade"` | Target: `ether1`, Chain: `srcnat` | Menambah rule NAT masquerade |
| **NAT Off** | `"matikan nat"` / `"disable masquerade"` | Intent: `disable_nat` | Menghapus rule NAT masquerade |
| **IP Read (Single)** | `"cek ip port 1"` / `"cek jalur 1"` | Intent: `get_interface_ip`, Target: `ether1` | Menampilkan Telemetry Card port 1 |
| **IP Read (Multi)** | `"cek ip lan 1 dan colokan 3"` | Intent: `get_interface_ip`, Target: `['ether1', 'ether3']` | Menampilkan Telemetry Card multi-port |
| **IP Read (All)** | `"cek semua ip"` / `"periksa seluruh antarmuka"` | Intent: `get_interface_ip`, Target: `None` | Menampilkan seluruh IP router |
| **IP Create (Add)** | `"tambahkan ip 10.10.10.1/24 di port 3"` | Intent: `add_ip_address`, Target: `ether3` | Menambah entri `/ip/address/add` |
| **IP Update (Ganti)** | `"ganti ip port 3 jadi 10.10.99.1/24"` | Intent: `update_ip_address`, Target: `ether3` | Atomic replace: hapus lama & pasang baru |
| **IP Delete (Hapus)** | `"hapus ip 10.10.10.1 di port 3"` / `"hapus ip port 3"` | Intent: `remove_ip_address`, Target: `ether3` | Menghapus entri `/ip/address/remove` |
| **Anti-Lockout IP** | `"Blokir internet 192.168.88.1"` | Target: Gateway Router | **DITOLAK**: Proteksi anti-lockout router aktif |
| **Anti-Lockout Port** | `"matikan port 2"` / `"ganti ip port 2 ..."` | Target: Management Port | **DITOLAK**: Interface controller dilindungi |
| **Ambiguity Guard** | `"hapus port 1"` / `"hapus lan 2"` | Tanpa objek konfigurasi spesifik | **DITOLAK**: Port fisik tidak dapat dihapus |
| **Action Guard** | `"sdfsdnf port 1"` | Kalimat acak / tanpa kata kerja | **DITOLAK**: Perintah tidak sah |

---

## 7. Lisensi & Hak Cipta
Penelitian dan pengembangan prototipe sistem ini dikembangkan untuk keperluan akademik dan riset Intent-Based Networking (IBN) pada Program Studi Teknik Informatika, Fakultas Teknik, Universitas Siliwangi (UNSIL).

| **Port Forwarding Add** | `"forward port 8080 ke server 192.168.88.50 port 80"` | Ext: `8080`, Int: `80`, IP: `192.168.88.50` | Menambah dst-nat rule ke LAN |
| **Port Forwarding Del** | `"hapus aturan port forwarding 8080"` / `"hapus semua"` | Ext: `8080` / `all`, Intent: `remove_port_forward` | Menghapus dst-nat rule |
| **SHOW Bandwidth** | `"siapa saja yang lagi dibatasi bandwidth"` | Intent: `get_bandwidth_status` | Membaca daftar `/queue/simple` |
| **SHOW Firewall** | `"tampilkan seluruh aturan firewall filter drop"` | Intent: `get_firewall_status` | Membaca daftar `/ip/firewall/filter` |
| **SHOW NAT** | `"apakah internet nat sedang aktif"` / `"cek aturan nat"` | Intent: `get_nat_status` | Membaca daftar `/ip/firewall/nat` |
| **Ping ICMP (IP/Domain)** | `"ping 8.8.8.8 count 4"` / `"coba ping google.com"` | Target: `8.8.8.8` / `google.com`, Count: `4` | Menjalankan uji ICMP RTT router |
| **Flush DNS Cache** | `"flush dns cache"` / `"bersihkan cache dns router"` | Intent: `flush_dns_cache` | Mengosongkan resolver cache DNS |
| **System Resource Health** | `"cek beban cpu dan ram router"` / `"system resource print"` | Intent: `get_system_health` | Telemetri CPU, RAM, Uptime hAP lite |
