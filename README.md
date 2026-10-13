# Lightweight Intent-Based Networking (IBN) Berbasis MikroTik RouterOS
**Studi Komparatif: Baseline Murni (Pure Machine Learning) vs Arsitektur Hybrid (Ours) dengan Evaluasi 8 Parameter Riset**

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![RouterOS](https://img.shields.io/badge/MikroTik-RouterOS%20v6.49.17-red.svg)](https://mikrotik.com/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()
[![Model Size](https://img.shields.io/badge/Model%20Size-31.90%20KB-brightgreen.svg)]()
[![Inference Latency](https://img.shields.io/badge/Inference%20Latency-%3C%201%20ms-orange.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Comparative%20Study-purple.svg)]()

Repository ini memuat kode sumber, dataset korpus 240 sampel (8 kelas intent), model Machine Learning terlatih, skrip evaluasi kuantitatif 8 parameter riset (metodologi split 80/20), serta antarmuka CLI untuk prototipe penelitian **Intent-Based Networking (IBN)** pada perangkat fisik nyata **MikroTik RouterOS v6 (hAP lite / RB941-2nD)**.

Repository ini terstruktur secara rapi ke dalam **3 Direktori Utama**:
* **`GAMBAR/`**: Diagram arsitektur end-to-end dan pipeline NLP beresolusi tinggi (High-DPI @2x monokrom).
* **`MURNI/`**: Implementasi **Baseline Murni (*Pure Machine Learning*)** berbasis Scikit-Learn TF-IDF + Logistic Regression murni tanpa aturan sintaksis tambahan.
* **`HYBRID/`**: Implementasi **Arsitektur Hibrida (*Ours*)** yang menggabungkan Machine Learning statistik dengan *Deterministic Regex Slotting*, *Syntactic Cue Overrides*, *Morphological Normalizer*, dan *Semantic Action Guard*.

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

## 3. Laporan Evaluasi 8 Parameter Riset (Metodologi Split 80/20)

Berikut adalah visualisasi perbandingan alur pemrosesan dan data empiris antara Baseline Murni (*Pure ML*) melawan Arsitektur Hybrid (*Ours*):

![Diagram Komparasi Murni vs Hybrid](GAMBAR/diagram_komparasi_murni_vs_hybrid.png)

Evaluasi kuantitatif komprehensif dijalankan menggunakan skrip `evaluasi_riset_ibn.py` terhadap dataset korpus dengan rasio **80% Data Latih (192 sampel)** dan **20% Data Uji Independen (48 sampel)** secara proporsional (*Stratified Split*):

```text
================================================================================
                   TABEL RINGKASAN RESMI EVALUASI RISET
================================================================================
+------------------------------+-------------------+------------------------------------------------+
| Parameter Riset              | Nilai Kuantitatif | Interpretasi Akademis                          |
+------------------------------+-------------------+------------------------------------------------+
| 1. CPU Controller Load       | 17.1%             | Sangat Rendah (Beban CPU Laptop/Mini PC minim) |
|    RAM Memory Footprint      | 116.25 MB         | Hemat Memori (Overhead model hanya 0.73 MB)    |
| 2. Processing Time (Mean)    | 0.958 ms          | Ultra-Fast (Inferensi & Validasi < 1.5 ms)     |
|    Controller Throughput     | 1,042.3 QPS       | Mampu melayani ribuan kueri per detik          |
| 3. Akurasi Intent (Accuracy) | 100.00%           | Akurasi sempurna pada 20% unseen test set      |
| 4. Precision (Macro Avg)     | 1.0000            | Presisi tinggi tanpa salah prediksi kelas      |
| 5. Recall (Macro Avg)        | 1.0000            | Sensitivitas tinggi mengenali seluruh kelas    |
| 6. F1-Score (Macro Avg)      | 1.0000            | Harmoni sempurna antara precision & recall     |
| 7. Command Accuracy          | 100.00%           | 100% Valid & Patuh Aturan Guard-Rail           |
| 8. Kompleksitas Deployment   | 31.90 KB          | Ringkas, mandiri, tanpa GPU, mudah dideploy    |
+------------------------------+-------------------+------------------------------------------------+
```

### A. Matriks Klasifikasi Per-Kelas (Classification Report)
* **Dataset Evaluasi:** 48 sampel unseen test set (6 sampel per kelas)
* **Akurasi Keseluruhan:** **100.00%**

| Intent Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| `block_traffic` | 1.0000 | 1.0000 | 1.0000 | 6 |
| `disable_interface` | 1.0000 | 1.0000 | 1.0000 | 6 |
| `disable_nat` | 1.0000 | 1.0000 | 1.0000 | 6 |
| `enable_interface` | 1.0000 | 1.0000 | 1.0000 | 6 |
| `enable_nat` | 1.0000 | 1.0000 | 1.0000 | 6 |
| `limit_bandwidth` | 1.0000 | 1.0000 | 1.0000 | 6 |
| `remove_limit` | 1.0000 | 1.0000 | 1.0000 | 6 |
| `unblock_traffic` | 1.0000 | 1.0000 | 1.0000 | 6 |
| **Macro Average** | **1.0000** | **1.0000** | **1.0000** | **48** |

### B. Confusion Matrix (8x8)
```text
True \ Pred          block  dis_if  dis_nat  en_if  en_nat  lim_bw  rem_lim  unblock
block_traffic          6      0        0       0       0       0       0        0
disable_interface      0      6        0       0       0       0       0        0
disable_nat            0      0        6       0       0       0       0        0
enable_interface       0      0        0       6       0       0       0        0
enable_nat             0      0        0       0       6       0       0        0
limit_bandwidth        0      0        0       0       0       6       0        0
remove_limit           0      0        0       0       0       0       6        0
unblock_traffic        0      0        0       0       0       0       0        6
```

### C. Command Accuracy & Policy Compliance
* **Perintah Langsung Tereksekusi Valid:** **46 / 48 (95.83%)**
* **Proteksi Keamanan Aktif (Anti-Lockout Triggers):** **2 / 48 (4.17%)** *(Menolak mematikan ether2)*
* **Kesalahan Konfigurasi / Format Gagal:** **0 / 48 (0.00%)**
* **Total Policy & Command Accuracy Rate:** **100.00%**

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
│   ├── dataset_intent.json                   # Dataset korpus 240 sampel (8 kelas)
│   ├── train_nlp.py                          # Training model hybrid
│   ├── intent_model.joblib                   # Model terlatih (31.90 KB)
│   ├── nlp_parser.py                         # Hybrid NLP (ML + Regex + Cues + Action Guard)
│   ├── policy_engine.py                      # Policy validator & generator
│   ├── mikrotik_adapter.py                   # Driver API port 8728 & idempotency
│   ├── main_ibn.py                           # CLI interaktif versi Hybrid (4 Tabel)
│   ├── evaluasi_riset_ibn.py                 # Evaluasi kuantitatif Hybrid (80/20)
│   ├── LAPORAN_EVALUASI_RISET.txt            # Hasil laporan evaluasi Hybrid
│   ├── benchmark_model.py                    # Benchmark latensi & throughput 1.000 iterasi
│   ├── create_diagram.py                     # Skrip renderer Playwright diagram arsitektur
│   ├── create_nlp_diagram.py                 # Skrip renderer Playwright diagram NLP
│   └── test_*.py                             # 8 suite pengujian otomatis lengkap
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

## 6. Tabel Cakupan Perintah Bahasa Alami (4 Domain Jaringan)

| Domain | Contoh Perintah Bahasa Alami | Hasil Ekstraksi NLP | Aksi Nyata RouterOS |
| :--- | :--- | :--- | :--- |
| **QoS Host** | `"Batasi bandwidth 192.168.88.50 jadi 2 Mbps"` | Target: `192.168.88.50/32`, Rate: `2M/2M` | Menambah antrean `/queue/simple` |
| **QoS Port Fisik** | `"saya ingin port 3 kasih limit 5mb"` | Target: `ether3`, Rate: `5M/5M` | Menambah antrean target `ether3` |
| **QoS Rollback** | `"Cabut limit bandwidth untuk port 3"` | Target: `ether3`, Intent: `remove_limit` | Menghapus antrean `qos_ether3` |
| **Firewall IP** | `"Blokir akses internet untuk 192.168.88.99"` | Target: `192.168.88.99/32`, Intent: `block` | Menambah drop rule `/ip/firewall/filter` |
| **Firewall Port** | `"blokir port 80 untuk 192.168.88.50"` | Target: `192.168.88.50/32`, Port: `80` (tcp) | Filter drop port destination 80 |
| **Firewall Global**| `"blokir port 443"` | Target: Global, Port: `443` (tcp) | Filter drop port 443 seluruh trafik |
| **Firewall Unblock**| `"buka blokir port 80 untuk 192.168.88.50"`| Intent: `unblock_traffic`, Port: `80` | Menghapus drop rule dari router |
| **Interface Up** | `"hidupkan wifi"` / `"aktif kan port 1"` | Target: `wlan1` / `ether1` | Mengaktifkan interface (`disabled=no`) |
| **Interface Down** | `"matikan port 4"` / `"matikan wifi"` | Target: `ether4` / `wlan1` | Mematikan interface non-manajemen |
| **NAT On** | `"aktifkan nat internet"` / `"enable masquerade"` | Target: `ether1`, Chain: `srcnat` | Menambah rule NAT masquerade |
| **NAT Off** | `"matikan nat"` / `"disable masquerade"` | Intent: `disable_nat` | Menghapus rule NAT masquerade |
| **Anti-Lockout IP** | `"Blokir internet 192.168.88.1"` | Target: Gateway Router | **DITOLAK**: Proteksi anti-lockout router aktif |
| **Anti-Lockout Port**| `"matikan port 2"` | Target: Management Port | **DITOLAK**: Interface controller dilindungi |
| **Action Guard** | `"sdfsdnf port 1"` | Kalimat acak / tanpa kata kerja | **DITOLAK**: Perintah tidak sah |

---

## 7. Lisensi & Hak Cipta
Penelitian dan pengembangan prototipe sistem ini dikembangkan untuk keperluan akademik dan riset Intent-Based Networking (IBN) pada Program Studi Teknik Informatika, Fakultas Teknik, Universitas Siliwangi (UNSIL).
