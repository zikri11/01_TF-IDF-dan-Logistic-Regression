# Lightweight Intent-Based Networking (IBN) Berbasis MikroTik RouterOS
**Implementasi Hybrid NLP: Scikit-Learn TF-IDF & Logistic Regression dengan Deterministic Entity Extraction**

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![RouterOS](https://img.shields.io/badge/MikroTik-RouterOS%20v6.49.17-red.svg)](https://mikrotik.com/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()
[![Model Size](https://img.shields.io/badge/Model%20Size-35.37%20KB-brightgreen.svg)]()
[![Inference Latency](https://img.shields.io/badge/Inference%20Latency-%3C%201%20ms-orange.svg)]()

Repository ini memuat kode sumber, korpus dataset, model terlatih, mesin kebijakan (*policy engine*), serta antarmuka CLI untuk prototipe penelitian **Intent-Based Networking (IBN)** berbasis perangkat nyata **MikroTik RouterOS v6 (hAP lite / RB941-2nD)**.

Sistem ini memungkinkan administrator jaringan menyampaikan tujuan pengelolaan jaringan (*intent*) menggunakan kalimat bahasa alami berbahasa Indonesia. Sistem secara otomatis menerjemahkan teks tersebut menjadi representasi kebijakan agnostik vendor (*Intermediate Policy*), memvalidasi batas keamanan (*safety guard-rails*), dan menerapkannya secara langsung ke router fisik melalui **RouterOS Binary API (Port 8728)** dengan prinsip idempoten.

---

## 1. Arsitektur Sistem End-to-End

Sistem dibangun dengan arsitektur tertutup (*closed-loop pipeline*) yang menghubungkan input manusia hingga perilaku nyata pada jaringan:

![Diagram Arsitektur IBN MikroTik](GAMBAR/diagram_arsitektur_ibn_mikrotik.png)

### Rantai Pemrosesan 5 Lapisan:
1. **Operator Intake Layer (`main_ibn.py`):** Antarmuka CLI interaktif yang menerima perintah teks bebas berbahasa Indonesia.
2. **Lightweight Hybrid NLP Layer (`nlp_parser.py`):**
   * **Jalur Probabilistik (ML):** Mengklasifikasikan maksud (*intent*) kalimat menggunakan TF-IDF (1,2-gram) + Logistic Regression.
   * **Jalur Deterministik (Regex):** Mengekstrak entitas pasti tanpa risiko halusinasi (*zero hallucination*) seperti IP Address, angka batas bandwidth, interface fisik (`ether1`-`ether4`), dan nomor port layanan (`80`, `443`, `22`, `53`).
   * **Syntactic Cue Disambiguation:** Resolusi cerdas untuk kata beririsan (misal *"buka blokir"* vs *"blokir"*, serta *"port 3"* fisik vs *"port 80"* protokol).
3. **Policy Engine & Safety Guard-Rails (`policy_engine.py`):**
   * Normalisasi format satuan fleksibel (`"2 Mbps"`, `"9mb"`, `"512k"`) ke format baku MikroTik (`"2M/2M"`, `"9M/9M"`, `"512k/512k"`).
   * **Proteksi Anti-Lockout:** Menolak pemblokiran terhadap IP Gateway Router (`192.168.88.1`) maupun IP host Controller.
   * **Validasi Hardware Catalog:** Menolak antarmuka fisik di luar kapasitas router lab (misal menolak *"port 5"* pada hAP lite yang hanya memiliki 4 port fisik).
   * Menghasilkan struktur baku **Intermediate Policy JSON**.
4. **MikroTik Adapter & Idempotency Engine (`mikrotik_adapter.py`):**
   * Menggunakan socket transport `librouteros` ke port 8728.
   * **Idempotensi:** Membaca tabel konfigurasi terlebih dahulu (`/print`) sebelum menambah rule (`/add` atau `set`) untuk menghemat memori RAM hAP lite yang terbatas (sisa RAM bebas $\approx 8.4\text{ MB}$).
5. **Real Network Behavior:** Mutasi konfigurasi langsung pada tabel `/queue/simple` (QoS) dan `/ip/firewall/filter` (Drop Rule) dengan dampak terukur pada *throughput* dan *packet delivery*.

---

## 2. Pipeline Khusus Lightweight Hybrid NLP

Arsitektur modul NLP dirancang secara khusus untuk lingkungan *resource-constrained controller* (Mini PC / Raspberry Pi / Laptop):

![Diagram Alur Pipeline NLP](GAMBAR/diagram_alur_nlp.png)

### Keunggulan Pendekatan Hibrida dibanding Alternatif:
* **Dibandingkan Cloud LLM (GPT/Claude):** Tidak bergantung pada koneksi internet, nol biaya API (*zero cost*), dan latensi komputasi < 1 ms (LLM berkisar 500–2000 ms).
* **Dibandingkan Rasa Framework:** Ukuran model sangat ringkas (35.37 KB vs Rasa > 1.5 GB), konsumsi RAM < 15 MB (Rasa > 600 MB), dan startup instan tanpa overhead TensorFlow/PyTorch.
* **Akurasi Parameter 100%:** Kombinasi Machine Learning untuk keluwesan bahasa manusia dan Regex untuk kepastian angka konfigurasi jaringan.

---

## 3. Hasil Evaluasi & Tolok Ukur Kinerja (Benchmark)

Evaluasi dilakukan secara empiris menggunakan modul `benchmark_model.py` terhadap dataset korpus evaluasi (120 sampel seimbang):

### A. Matriks Klasifikasi (Classification Report)
* **Dataset:** 120 sampel (30 sampel per kelas intent)
* **Akurasi Keseluruhan:** **100.00%**

| Intent Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| `limit_bandwidth` | 1.0000 | 1.0000 | 1.0000 | 30 |
| `remove_limit` | 1.0000 | 1.0000 | 1.0000 | 30 |
| `block_traffic` | 1.0000 | 1.0000 | 1.0000 | 30 |
| `unblock_traffic` | 1.0000 | 1.0000 | 1.0000 | 30 |
| **Macro Average** | **1.0000** | **1.0000** | **1.0000** | **120** |

### B. Confusion Matrix
```text
True \ Pred          block_traffic  limit_bandwidth  remove_limit  unblock_traffic
block_traffic                   30                0             0                0
limit_bandwidth                  0               30             0                0
remove_limit                     0                0            30                0
unblock_traffic                  0                0             0               30
```

### C. Benchmark Latensi & Throughput (1,000 Iterasi)
* **Ukuran File Model (`intent_model.joblib`):** **35.37 KB**
* **Jumlah Fitur N-Gram Vocabulary:** 626 n-grams
* **Model Load Time:** ~92.5 ms (hanya sekali saat inisialisasi)
* **Cold Start Latency:** 1.162 ms
* **Rata-rata Latensi Inferensi (Mean):** **0.973 ms** (< 1 milidetik)
* **Median Latensi:** 0.896 ms
* **Persentil 95 (P95):** 1.589 ms
* **Persentil 99 (P99):** 1.749 ms
* **Single-Query Throughput:** **1,027.5 queries / detik**
* **Batch Inference Throughput:** **33,636 queries / detik**

---

## 4. Struktur Direktori Proyek

```text
.
├── GAMBAR/
│   ├── diagram_arsitektur_ibn_mikrotik.png   # Diagram arsitektur end-to-end
│   ├── diagram_arsitektur_ibn_mikrotik.svg   # Source vector diagram arsitektur
│   ├── diagram_alur_nlp.png                 # Diagram alur pipeline NLP
│   └── diagram_alur_nlp.svg                 # Source vector pipeline NLP
├── config.py                                 # Parameter koneksi RouterOS (IP, Port, Kredensial)
├── dataset_intent.json                       # Dataset korpus 120 kalimat latih
├── train_nlp.py                              # Skrip training Scikit-Learn pipeline
├── intent_model.joblib                       # Model terlatih (35.37 KB)
├── nlp_parser.py                             # Hybrid NLP extractor & disambiguator
├── policy_engine.py                          # Validator keamanan & normalisasi policy
├── mikrotik_adapter.py                       # Driver API RouterOS port 8728 & idempotency
├── main_ibn.py                               # Antarmuka CLI Interaktif utama
├── benchmark_model.py                        # Skrip benchmark latensi & metrik klasifikasi
├── create_diagram.py                         # Skrip renderer Playwright diagram arsitektur
├── create_nlp_diagram.py                     # Skrip renderer Playwright diagram NLP
├── test_fase1.py                             # Unit test adapter koneksi & router
├── test_fase2.py                             # Unit test policy engine & safety invariants
├── test_fase3.py                             # Integration test NLP unseen prompts
├── test_fase4.py                             # Test interaktif simulasi CLI subprocess
├── test_port_feature.py                      # Test fitur interface fisik & service port
├── requirements.txt                          # Daftar dependensi Python
└── README.md                                 # Dokumentasi utama proyek
```

---

## 5. Panduan Instalasi & Persiapan

### A. Prasyarat Lingkungan
* Python 3.10+ (Direkomendasikan Python 3.12)
* Perangkat MikroTik RouterOS v6 fisik atau Cloud Hosted Router (CHR)
* Port service `api` aktif pada port **8728** di MikroTik (`/ip service enable api`)

### B. Instalasi Dependensi
Clone repository dan pasang pustaka yang dibutuhkan:
```bash
git clone https://github.com/zikri11/01_TF-IDF-dan-Logistic-Regression.git
cd 01_TF-IDF-dan-Logistic-Regression
pip install -r requirements.txt
```

### C. Konfigurasi Koneksi Router
Buka file `config.py` dan sesuaikan parameter IP serta kredensial router lab Anda:
```python
ROUTER_HOST = "192.168.88.1"
ROUTER_PORT = 8728
ROUTER_USER = "admin"
ROUTER_PASS = "PASSWORD_ROUTER_ANDA"
ROUTER_TIMEOUT = 5
```

---

## 6. Cara Menjalankan Program

### A. Menjalankan Antarmuka Interaktif CLI
Jalankan program utama untuk memulai sesi IBN:
```bash
python main_ibn.py
```

Perintah bawaan yang tersedia di dalam prompt:
* `status` / `cek`: Menampilkan tabel antrean Simple Queue dan Firewall Drop aktif di router.
* `bantuan` / `help`: Menampilkan panduan contoh format kalimat alami.
* `clear` / `cls`: Membersihkan layar terminal.
* `keluar` / `exit`: Menutup program secara aman.

### B. Menjalankan Benchmark Kinerja Model
Untuk mengevaluasi performa model Machine Learning secara mandiri:
```bash
python benchmark_model.py
```

### C. Menjalankan Seluruh Automated Test Suites
Verifikasi integritas sistem end-to-end langsung ke router:
```bash
python test_fase1.py
python test_fase2.py
python test_fase3.py
python test_fase4.py
python test_port_feature.py
```

---

## 7. Tabel Contoh Kalimat Alami yang Didukung

| Domain | Contoh Kalimat Operator | Hasil Ekstraksi NLP | Aksi Eksekusi MikroTik |
| :--- | :--- | :--- | :--- |
| **QoS (Host IP)** | `"Batasi bandwidth 192.168.88.50 jadi 2 Mbps"` | Target: `192.168.88.50/32`, Rate: `2M/2M` | `/queue/simple/add name=qos_192.168.88.50 max-limit=2M/2M` |
| **QoS (Variasi Unit)** | `"bisa batasi jalur 192.168.21.21 jadi 9mb"` | Target: `192.168.21.21/32`, Rate: `9M/9M` | Normalisasi unit fleksibel `9mb` $\rightarrow$ `9M/9M` |
| **QoS (Port Fisik)** | `"saya ingin port 3 kasih limit 5mb"` | Target: `ether3`, Rate: `5M/5M` | `/queue/simple/add name=qos_ether3 target=ether3 max-limit=5M/5M` |
| **QoS (Rollback)** | `"Cabut limit bandwidth untuk port 3"` | Target: `ether3`, Intent: `remove_limit` | Menghapus antrean `qos_ether3` dari router |
| **Firewall (IP Drop)** | `"Blokir akses internet untuk 192.168.88.99"` | Target: `192.168.88.99/32`, Intent: `block` | `/ip/firewall/filter/add chain=forward action=drop src-address=...` |
| **Firewall (Port + IP)** | `"blokir port 80 untuk 192.168.88.50"` | Target: `192.168.88.50/32`, Port: `80` (tcp) | Filter drop forward spesifik IP dan port destination 80 |
| **Firewall (Global Drop)**| `"blokir port 443"` | Target: Global, Port: `443` (tcp) | Filter drop forward port destination 443 tanpa batasan IP |
| **Firewall (Alias Service)**| `"tutup akses ssh 192.168.88.50"` | Target: `192.168.88.50/32`, Port: `22` (tcp) | Mapping otomatis alias `ssh` $\rightarrow$ port 22 |
| **Firewall (Unblock)** | `"buka blokir port 80 untuk 192.168.88.50"`| Intent: `unblock_traffic`, Port: `80` | Menghapus rule drop yang terpasang |
| **Safety Invariant** | `"Blokir internet 192.168.88.1"` | Target: Gateway Router | **REJECTED**: Proteksi anti-lockout router aktif |
| **Hardware Catalog** | `"port 5 kasih limit 5mb"` | Target: `ether5` | **REJECTED**: Interface tidak tersedia pada fisik hAP lite |

---

## 8. Lisensi & Hak Cipta
Penelitian dan pengembangan prototipe sistem ini dikembangkan untuk keperluan akademik dan riset Intent-Based Networking (IBN) pada Program Studi Teknik Informatika, Fakultas Teknik, Universitas Siliwangi (UNSIL).
