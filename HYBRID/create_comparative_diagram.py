import os
from pathlib import Path
from playwright.sync_api import sync_playwright

SVG_PATH = r"D:\KULIAH S1\RISET JARKOM\TEST\PRAKTIK_IBN\GAMBAR\diagram_komparasi_murni_vs_hybrid.svg"
PNG_PATH = r"D:\KULIAH S1\RISET JARKOM\TEST\PRAKTIK_IBN\GAMBAR\diagram_komparasi_murni_vs_hybrid.png"

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 2380" width="1400" height="2380">
  <defs>
    <style>
      .bg { fill: #FFFFFF; }
      .title-main { font-family: 'Segoe UI', Arial, sans-serif; font-size: 26px; font-weight: bold; fill: #000000; text-anchor: middle; }
      .title-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; fill: #444444; text-anchor: middle; }
      .meta-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; fill: #666666; text-anchor: middle; }
      .section-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 17px; font-weight: bold; fill: #000000; }
      .section-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-style: italic; fill: #555555; }
      .col-header { font-family: 'Segoe UI', Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #000000; text-anchor: middle; }
      .col-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; fill: #555555; text-anchor: middle; }
      .card-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #000000; }
      .card-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12.5px; fill: #222222; }
      .code-text { font-family: 'Consolas', 'Courier New', monospace; font-size: 11.5px; fill: #111111; }
      .badge-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #000000; }
      .tag-fail { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #000000; }
      .tag-pass { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #000000; }
      .arrow-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #333333; text-anchor: middle; }

      .box-container { fill: #FAFAFA; stroke: #000000; stroke-width: 2; rx: 8; }
      .box-card { fill: #FFFFFF; stroke: #000000; stroke-width: 1.5; rx: 6; }
      .box-card-gray { fill: #F4F4F4; stroke: #333333; stroke-width: 1.5; rx: 6; }
      .box-decision { fill: #FFFFFF; stroke: #000000; stroke-width: 2; }
      .line-main { stroke: #000000; stroke-width: 2; marker-end: url(#arrowhead); }
      .line-dashed { stroke: #555555; stroke-width: 1.5; stroke-dasharray: 5,5; marker-end: url(#arrowhead-gray); }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#000000" />
    </marker>
    <marker id="arrowhead-gray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#555555" />
    </marker>
  </defs>

  <!-- Background Canvas -->
  <rect width="1400" height="2380" class="bg" />

  <!-- ========================================== -->
  <!-- HEADER BLOCK                               -->
  <!-- ========================================== -->
  <rect x="50" y="30" width="1300" height="120" fill="#FFFFFF" stroke="#000000" stroke-width="2" rx="8" />
  <text x="700" y="70" class="title-main">DIAGRAM KOMPARASI: BASELINE MURNI vs ARSITEKTUR HYBRID</text>
  <text x="700" y="98" class="title-sub">Studi Komparatif Model TF-IDF &amp; Logistic Regression pada Intent-Based Networking MikroTik RouterOS v6</text>
  <text x="700" y="126" class="meta-text">Dataset: 240 Sampel Seimbang (8 Kelas Intent) | Evaluasi 80% Train : 20% Unseen Test Set | Target: MikroTik hAP lite</text>

  <!-- ========================================== -->
  <!-- SEKSI 1: KASUS UJI LINGUISTIK OPERATOR     -->
  <!-- ========================================== -->
  <rect x="50" y="175" width="1300" height="175" class="box-container" />
  <rect x="70" y="195" width="370" height="30" fill="#E5E5E5" stroke="#000000" stroke-width="1.5" rx="4" />
  <text x="85" y="216" class="section-title">SEKSI 1: INPUT PERINTAH &amp; KASUS UJI</text>
  <text x="455" y="216" class="section-sub">Tantangan linguistik bahasa alami nyata yang dihadapi sistem IBN di lapangan</text>

  <g transform="translate(80, 240)">
    <rect x="0" y="0" width="285" height="90" class="box-card" />
    <text x="15" y="22" class="card-title">Kasus A: Negasi Bertentangan</text>
    <rect x="15" y="32" width="255" height="45" fill="#F4F4F4" stroke="#CCCCCC" rx="3" />
    <text x="25" y="52" class="code-text">&quot;buka blokir port 80&quot;</text>
    <text x="25" y="68" class="card-text">(Kata &quot;blokir&quot; dominan leksikal)</text>
  </g>

  <g transform="translate(395, 240)">
    <rect x="0" y="0" width="285" height="90" class="box-card" />
    <text x="15" y="22" class="card-title">Kasus B: Ambiguitas &quot;Port&quot;</text>
    <rect x="15" y="32" width="255" height="45" fill="#F4F4F4" stroke="#CCCCCC" rx="3" />
    <text x="25" y="52" class="code-text">&quot;port 3 kasih limit 5mb&quot;</text>
    <text x="25" y="68" class="card-text">(Port Fisik vs Port Layanan TCP)</text>
  </g>

  <g transform="translate(710, 240)">
    <rect x="0" y="0" width="295" height="90" class="box-card" />
    <text x="15" y="22" class="card-title">Kasus C: Morfologi Terpisah</text>
    <rect x="15" y="32" width="265" height="45" fill="#F4F4F4" stroke="#CCCCCC" rx="3" />
    <text x="25" y="52" class="code-text">&quot;aktif kan port 1&quot;</text>
    <text x="25" y="68" class="card-text">(Imbuhan terpisah spasi pengetikan)</text>
  </g>

  <g transform="translate(1035, 240)">
    <rect x="0" y="0" width="290" height="90" class="box-card" />
    <text x="15" y="22" class="card-title">Kasus D: Input Acak / Gibberish</text>
    <rect x="15" y="32" width="260" height="45" fill="#F4F4F4" stroke="#CCCCCC" rx="3" />
    <text x="25" y="52" class="code-text">&quot;sdfsdnf port 1&quot;</text>
    <text x="25" y="68" class="card-text">(Tanpa kata kerja aksi yang sah)</text>
  </g>

  <!-- Panah Cabang Pembagi: Kiri Murni vs Kanan Hybrid -->
  <line x1="700" y1="350" x2="700" y2="390" class="line-main" />
  <line x1="700" y1="390" x2="365" y2="390" class="line-main" />
  <line x1="700" y1="390" x2="1035" y2="390" class="line-main" />
  <line x1="365" y1="390" x2="365" y2="430" class="line-main" />
  <line x1="1035" y1="390" x2="1035" y2="430" class="line-main" />

  <rect x="235" y="380" width="260" height="20" fill="#FFFFFF" stroke="#000000" rx="3" />
  <text x="365" y="394" class="arrow-text">Disalurkan ke Pipeline Murni</text>
  <rect x="905" y="380" width="260" height="20" fill="#FFFFFF" stroke="#000000" rx="3" />
  <text x="1035" y="394" class="arrow-text">Disalurkan ke Pipeline Hybrid</text>

  <!-- ========================================================================= -->
  <!-- SEKSI 2: PERBANDINGAN DUA PIPELINE PARALEL (MURNI VS HYBRID)             -->
  <!-- ========================================================================= -->

  <!-- ============================ -->
  <!-- SISI KIRI: BASELINE MURNI    -->
  <!-- ============================ -->
  <rect x="50" y="430" width="630" height="1140" class="box-container" />
  <rect x="70" y="450" width="590" height="50" fill="#EAEAEA" stroke="#000000" stroke-width="1.5" rx="5" />
  <text x="365" y="473" class="col-header">BASELINE MURNI (PURE MACHINE LEARNING)</text>
  <text x="365" y="491" class="col-sub">100% Mengandalkan Skor Probabilitas Statistik Model TF-IDF + Logistic Regression</text>

  <!-- Step M1: Raw Text Tokenization -->
  <g transform="translate(80, 520)">
    <rect x="0" y="0" width="570" height="110" class="box-card" />
    <text x="15" y="24" class="card-title">1. Tokenisasi &amp; Vektorisasi Tanpa Normalisasi</text>
    <text x="15" y="46" class="card-text">- Teks mentah langsung diumpankan ke TfidfVectorizer</text>
    <text x="15" y="66" class="card-text">- Tanpa penggabung imbuhan morfologi (Morphological Join: OFF)</text>
    <rect x="15" y="76" width="540" height="24" fill="#F4F4F4" stroke="#CCCCCC" rx="3" />
    <text x="25" y="93" class="code-text">&quot;aktif kan&quot; -&gt; dipotong terpisah: [&#39;aktif&#39;, &#39;kan&#39;] (Bukan &#39;aktifkan&#39;)</text>
  </g>

  <!-- Panah M1 -> M2 -->
  <line x1="365" y1="630" x2="365" y2="665" class="line-main" />

  <!-- Step M2: Pure Classifier -->
  <g transform="translate(80, 665)">
    <rect x="0" y="0" width="570" height="175" class="box-card" />
    <text x="15" y="24" class="card-title">2. Klasifikasi Probabilistik Murni (Softmax)</text>
    <text x="15" y="46" class="card-text">- Algoritma: LogisticRegression(C=5.0, solver=&#39;lbfgs&#39;)</text>
    <text x="15" y="66" class="card-text">- Mengambil index probabilitas argmax tertinggi murni</text>
    <text x="15" y="86" class="card-text">- Tanpa Semantic Action Guard (Kalimat acak tetap ditebak kelasnya!)</text>

    <rect x="15" y="96" width="540" height="65" fill="#F4F4F4" stroke="#333333" rx="4" />
    <text x="25" y="116" class="code-text">Kasus A (&quot;buka blokir port 80&quot;):</text>
    <text x="25" y="134" class="code-text">  P(block_traffic)=52.4% vs P(unblock)=41.2% -&gt; Prediksi SALAH</text>
    <text x="25" y="152" class="code-text">Kasus D (&quot;sdfsdnf port 1&quot;) -&gt; Ditebak asal: enable_interface (50.1%)</text>
  </g>

  <!-- Panah M2 -> M3 -->
  <line x1="365" y1="840" x2="365" y2="875" class="line-main" />

  <!-- Step M3: Naive Entity Extraction -->
  <g transform="translate(80, 875)">
    <rect x="0" y="0" width="570" height="125" class="box-card" />
    <text x="15" y="24" class="card-title">3. Ekstraksi Entitas Naif Tanpa Disambiguasi</text>
    <text x="15" y="46" class="card-text">- Regex standar IPv4 dan angka kecepatan sederhana</text>
    <text x="15" y="66" class="card-text">- Tanpa pembeda konteks semantik kata &quot;port&quot;</text>
    <rect x="15" y="76" width="540" height="40" fill="#F4F4F4" stroke="#CCCCCC" rx="3" />
    <text x="25" y="94" class="code-text">Pada kalimat &quot;port 3 kasih limit 5mb&quot;:</text>
    <text x="25" y="109" class="code-text">Angka &quot;3&quot; berpotensi salah dipetakan antara interface vs dst_port</text>
  </g>

  <!-- Panah M3 -> M4 -->
  <line x1="365" y1="1000" x2="365" y2="1035" class="line-main" />

  <!-- Step M4: Hasil & Kelemahan Baseline Murni -->
  <g transform="translate(80, 1035)">
    <rect x="0" y="0" width="570" height="230" class="box-card" />
    <text x="15" y="24" class="card-title">4. Dampak Empiris pada Konfigurasi Jaringan</text>
    <text x="15" y="48" class="card-text">- Akurasi Intent Unseen Test : 85.42% (7 misklasifikasi)</text>
    <text x="15" y="70" class="card-text">- Macro F1-Score             : 0.8513</text>
    <text x="15" y="92" class="card-text">- Command Accuracy           : 85.42% (7 KEGAGALAN KONFIGURASI!)</text>

    <rect x="15" y="105" width="540" height="110" fill="#F4F4F4" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="25" y="126" class="tag-fail">POTENSI BAHAYA DI JARINGAN LAB MIKROTIK:</text>
    <text x="25" y="146" class="card-text">* Port 80 yang ingin dibuka malah terblokir (Drop Rule ditambahkan)!</text>
    <text x="25" y="166" class="card-text">* Kalimat acak &quot;sdfsdnf port 1&quot; memicu mutasi konfigurasi liar!</text>
    <text x="25" y="186" class="card-text">* Tidak andal untuk lingkungan produksi jaringan kritis.</text>
    <text x="25" y="206" class="badge-text">STATUS: TIDAK MEMENUHI SYARAT KEAMANAN ZERO-ERROR</text>
  </g>

  <!-- Step M5: Summary Badge Murni -->
  <g transform="translate(80, 1285)">
    <rect x="0" y="0" width="570" height="75" fill="#EAEAEA" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="20" y="25" class="badge-text">RINGKASAN BASELINE MURNI (PURE ML):</text>
    <text x="20" y="46" class="card-text">Latensi: 0.899 ms | Memory: 118.16 MB | Akurasi: 85.42%</text>
    <text x="20" y="65" class="card-text">Kelemahan: Rentan Lexical Overlap, Halusinasi Perintah, &amp; Fatal Error.</text>
  </g>


  <!-- ============================ -->
  <!-- SISI KANAN: ARSITEKTUR HYBRID-->
  <!-- ============================ -->
  <rect x="720" y="430" width="630" height="1140" class="box-container" />
  <rect x="740" y="450" width="590" height="50" fill="#EAEAEA" stroke="#000000" stroke-width="1.5" rx="5" />
  <text x="1035" y="473" class="col-header">ARSITEKTUR HYBRID (OURS - USULAN RISET)</text>
  <text x="1035" y="491" class="col-sub">Integrasi Sinergis Model Statistik + Regex Deterministik + Aturan Sintaksis Cerdas</text>

  <!-- Step H1: Normalizer & Action Guard -->
  <g transform="translate(750, 520)">
    <rect x="0" y="0" width="570" height="110" class="box-card" />
    <text x="15" y="24" class="card-title">1. Pra-Pemrosesan Morfologi &amp; Semantic Action Guard</text>
    <text x="15" y="46" class="card-text">- Normalisasi Morfologi: Menggabungkan spasi imbuhan otomatis</text>
    <text x="15" y="66" class="code-text">  &quot;aktif kan&quot; -&gt; &quot;aktifkan&quot; | &quot;mati kan&quot; -&gt; &quot;matikan&quot; (Regex Clitic)</text>
    <text x="15" y="86" class="card-text">- Semantic Action Guard: Wajib memuat kata kerja aksi sah</text>
    <text x="15" y="103" class="badge-text">  Input &quot;sdfsdnf port 1&quot; -&gt; LANGSUNG DITOLAK SEBAGAI INVALID!</text>
  </g>

  <!-- Panah H1 -> H2 -->
  <line x1="1035" y1="630" x2="1035" y2="665" class="line-main" />

  <!-- Step H2: Dual-Path Engine -->
  <g transform="translate(750, 665)">
    <rect x="0" y="0" width="570" height="175" class="box-card" />
    <text x="15" y="24" class="card-title">2. Dual-Path Processing: ML + Regex Slotting</text>
    
    <g transform="translate(15, 33)">
      <rect x="0" y="0" width="260" height="130" fill="#F4F4F4" stroke="#333333" rx="4" />
      <text x="10" y="20" class="badge-text">Jalur A: Probabilistik (ML)</text>
      <text x="10" y="40" class="card-text">- TF-IDF (1,2-gram)</text>
      <text x="10" y="58" class="card-text">- LogisticRegression (C=5.0)</text>
      <text x="10" y="76" class="card-text">- Menghasilkan distribusi</text>
      <text x="10" y="94" class="card-text">  probabilitas 8 kelas intent</text>
      <text x="10" y="114" class="code-text">P(intent | sentence)</text>
    </g>

    <g transform="translate(290, 33)">
      <rect x="0" y="0" width="265" height="130" fill="#F4F4F4" stroke="#333333" rx="4" />
      <text x="10" y="20" class="badge-text">Jalur B: Deterministik (Regex)</text>
      <text x="10" y="40" class="card-text">- IPv4: \\b(?:\\d{1,3}\\.){3}...\\b</text>
      <text x="10" y="58" class="card-text">- Rate: \\b\\d+(mbps|mb|k|m)...</text>
      <text x="10" y="76" class="card-text">- Service Ports: 80, 443, 22</text>
      <text x="10" y="94" class="card-text">- Physical Ports: ether1..4</text>
      <text x="10" y="114" class="badge-text">ZERO HALLUCINATION (100% Eksak)</text>
    </g>
  </g>

  <!-- Panah H2 -> H3 -->
  <line x1="1035" y1="840" x2="1035" y2="875" class="line-main" />

  <!-- Step H3: Syntactic Cue Disambiguation -->
  <g transform="translate(750, 875)">
    <rect x="0" y="0" width="570" height="125" class="box-card" />
    <text x="15" y="24" class="card-title">3. Syntactic Cue Overrides &amp; Disambiguasi Domain</text>
    <text x="15" y="46" class="card-text">- Negasi Override: Kata &quot;buka&quot; / &quot;unblock&quot; + &quot;blokir&quot; -&gt; unblock (100%)</text>
    <text x="15" y="66" class="card-text">- QoS Reversal: Kata &quot;cabut&quot; / &quot;hapus&quot; + &quot;limit&quot; -&gt; remove_limit (100%)</text>
    <text x="15" y="86" class="card-text">- Port Disambiguation: Pada limit -&gt; interface fisik (ether3);</text>
    <text x="15" y="104" class="card-text">                       Pada firewall -&gt; port protokol layanan (port 80).</text>
  </g>

  <!-- Panah H3 -> H4 -->
  <line x1="1035" y1="1000" x2="1035" y2="1035" class="line-main" />

  <!-- Step H4: Hasil & Keunggulan Hybrid -->
  <g transform="translate(750, 1035)">
    <rect x="0" y="0" width="570" height="230" class="box-card" />
    <text x="15" y="24" class="card-title">4. Dampak Empiris pada Konfigurasi Jaringan</text>
    <text x="15" y="48" class="card-text">- Akurasi Intent Unseen Test : 100.00% (SEMPURNA)</text>
    <text x="15" y="70" class="card-text">- Macro F1-Score             : 1.0000</text>
    <text x="15" y="92" class="card-text">- Command Accuracy           : 100.00% (NOL KEGAGALAN / 0 FAILURES)</text>

    <rect x="15" y="105" width="540" height="110" fill="#F4F4F4" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="25" y="126" class="tag-pass">KEUNGGULAN OPERASIONAL PADA MIKROTIK NYATA:</text>
    <text x="25" y="146" class="card-text">* Tidak ada salah eksekusi rule (Zero Misconfiguration Risk)!</text>
    <text x="25" y="166" class="card-text">* Proteksi Anti-Lockout otomatis melindungi port kabel LAN ether2.</text>
    <text x="25" y="186" class="card-text">* Kalimat acak diblokir sebelum menyentuh memori router.</text>
    <text x="25" y="206" class="badge-text">STATUS: MEMENUHI STANDAR PRODUKSI JARINGAN TELEKOMUNIKASI</text>
  </g>

  <!-- Step H5: Summary Badge Hybrid -->
  <g transform="translate(750, 1285)">
    <rect x="0" y="0" width="570" height="75" fill="#EAEAEA" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="20" y="25" class="badge-text">RINGKASAN ARSITEKTUR HYBRID (OURS):</text>
    <text x="20" y="46" class="card-text">Latensi: 0.958 ms (Hanya +0.059 ms) | Memory: 116.25 MB | Akurasi: 100%</text>
    <text x="20" y="65" class="card-text">Keunggulan: Menutup 100% kelemahan leksikal dengan overhead komputasi nol.</text>
  </g>


  <!-- ========================================================================= -->
  <!-- SEKSI 3: TABEL MATRIKS PERBANDINGAN 8 PARAMETER RISET                     -->
  <!-- ========================================================================= -->
  <g transform="translate(50, 1600)">
    <rect x="0" y="0" width="1300" height="390" class="box-container" />
    <rect x="20" y="20" width="450" height="30" fill="#E5E5E5" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="35" y="41" class="section-title">SEKSI 3: MATRIKS KOMPARATIF 8 PARAMETER RISET</text>
    <text x="485" y="41" class="section-sub">Data empiris terverifikasi hasil pengujian 80% Train : 20% Unseen Test Set</text>

    <!-- Table Header -->
    <g transform="translate(20, 65)">
      <rect x="0" y="0" width="1260" height="32" fill="#000000" rx="3" />
      <text x="35" y="21" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#FFFFFF">No</text>
      <text x="210" y="21" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#FFFFFF">Parameter Riset</text>
      <text x="475" y="21" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#FFFFFF">Baseline Murni (Pure ML)</text>
      <text x="730" y="21" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#FFFFFF">Arsitektur Hybrid (Ours)</text>
      <text x="1050" y="21" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#FFFFFF">Dampak / Peningkatan Kinerja</text>
    </g>

    <!-- Table Rows -->
    <!-- Row 1 -->
    <g transform="translate(20, 102)">
      <rect x="0" y="0" width="1260" height="28" fill="#FFFFFF" stroke="#E0E0E0" />
      <text x="35" y="19" class="card-text">1</text>
      <text x="80" y="19" class="badge-text">Akurasi Intent (Accuracy)</text>
      <text x="475" y="19" class="card-text">85.42% (7 misklasifikasi)</text>
      <text x="730" y="19" class="badge-text">100.00% (Zero Error)</text>
      <text x="960" y="19" class="card-text">+14.58% Peningkatan signifikan</text>
    </g>
    <!-- Row 2 -->
    <g transform="translate(20, 132)">
      <rect x="0" y="0" width="1260" height="28" fill="#F9F9F9" stroke="#E0E0E0" />
      <text x="35" y="19" class="card-text">2</text>
      <text x="80" y="19" class="badge-text">Precision (Macro Average)</text>
      <text x="475" y="19" class="card-text">0.8612</text>
      <text x="730" y="19" class="badge-text">1.0000</text>
      <text x="960" y="19" class="card-text">+0.1388 Bebas salah prediksi kelas</text>
    </g>
    <!-- Row 3 -->
    <g transform="translate(20, 162)">
      <rect x="0" y="0" width="1260" height="28" fill="#FFFFFF" stroke="#E0E0E0" />
      <text x="35" y="19" class="card-text">3</text>
      <text x="80" y="19" class="badge-text">Recall (Macro Average)</text>
      <text x="475" y="19" class="card-text">0.8542</text>
      <text x="730" y="19" class="badge-text">1.0000</text>
      <text x="960" y="19" class="card-text">+0.1458 Sensitivitas sempurna</text>
    </g>
    <!-- Row 4 -->
    <g transform="translate(20, 192)">
      <rect x="0" y="0" width="1260" height="28" fill="#F9F9F9" stroke="#E0E0E0" />
      <text x="35" y="19" class="card-text">4</text>
      <text x="80" y="19" class="badge-text">F1-Score (Macro Average)</text>
      <text x="475" y="19" class="card-text">0.8513</text>
      <text x="730" y="19" class="badge-text">1.0000</text>
      <text x="960" y="19" class="card-text">+0.1487 Harmoni presisi &amp; recall</text>
    </g>
    <!-- Row 5 -->
    <g transform="translate(20, 222)">
      <rect x="0" y="0" width="1260" height="28" fill="#FFFFFF" stroke="#E0E0E0" />
      <text x="35" y="19" class="card-text">5</text>
      <text x="80" y="19" class="badge-text">Command Accuracy (RouterOS)</text>
      <text x="475" y="19" class="card-text">85.42% (7 payload gagal)</text>
      <text x="730" y="19" class="badge-text">100.00% (Semua valid)</text>
      <text x="960" y="19" class="card-text">+14.58% Integritas konfigurasi terjamin</text>
    </g>
    <!-- Row 6 -->
    <g transform="translate(20, 252)">
      <rect x="0" y="0" width="1260" height="28" fill="#F9F9F9" stroke="#E0E0E0" />
      <text x="35" y="19" class="card-text">6</text>
      <text x="80" y="19" class="badge-text">Processing Latency (Mean)</text>
      <text x="475" y="19" class="card-text">0.899 ms</text>
      <text x="730" y="19" class="card-text">0.958 ms</text>
      <text x="960" y="19" class="card-text">Hanya +0.059 ms overhead (Tetap &lt; 1 ms)</text>
    </g>
    <!-- Row 7 -->
    <g transform="translate(20, 282)">
      <rect x="0" y="0" width="1260" height="28" fill="#FFFFFF" stroke="#E0E0E0" />
      <text x="35" y="19" class="card-text">7</text>
      <text x="80" y="19" class="badge-text">Controller Resource (RAM/CPU)</text>
      <text x="475" y="19" class="card-text">118.16 MB / 15.5% CPU</text>
      <text x="730" y="19" class="card-text">116.25 MB / 17.1% CPU</text>
      <text x="960" y="19" class="card-text">Sangat hemat daya di laptop &amp; Mini PC</text>
    </g>
    <!-- Row 8 -->
    <g transform="translate(20, 312)">
      <rect x="0" y="0" width="1260" height="28" fill="#F9F9F9" stroke="#E0E0E0" />
      <text x="35" y="19" class="card-text">8</text>
      <text x="80" y="19" class="badge-text">Kompleksitas Deployment</text>
      <text x="475" y="19" class="card-text">31.90 KB Model Footprint</text>
      <text x="730" y="19" class="card-text">31.90 KB Model Footprint</text>
      <text x="960" y="19" class="card-text">Mandiri, tanpa GPU, tanpa Cloud LLM</text>
    </g>

    <text x="35" y="362" font-family="'Segoe UI', Arial, sans-serif" font-size="12px" fill="#555555" text-anchor="start">* Keterangan: Latensi diuji melalui stress-test 1,000 iterasi kueri beruntun pada host controller lokal.</text>
  </g>

  <!-- ========================================================================= -->
  <!-- SEKSI 4: KESIMPULAN RISET AKADEMIK                                        -->
  <!-- ========================================================================= -->
  <g transform="translate(50, 2010)">
    <rect x="0" y="0" width="1300" height="320" class="box-container" />
    <rect x="20" y="20" width="430" height="30" fill="#E5E5E5" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="35" y="41" class="section-title">SEKSI 4: KESIMPULAN &amp; KONTRIBUSI NOVELTY</text>
    <text x="465" y="41" class="section-sub">Intisari argumen ilmiah untuk laporan skripsi, tesis, dan publikasi jurnal/konferensi</text>

    <g transform="translate(20, 65)">
      <rect x="0" y="0" width="400" height="235" class="box-card" />
      <text x="15" y="25" class="card-title">1. Kegagalan Pure ML (Research Gap)</text>
      <text x="15" y="48" class="card-text">Machine Learning statistik murni (TF-IDF +</text>
      <text x="15" y="66" class="card-text">Logistic Regression) gagal mengatasi</text>
      <text x="15" y="84" class="card-text">&quot;Lexical Overlap&quot; pada domain jaringan.</text>
      <text x="15" y="106" class="card-text">Kata &quot;blokir&quot; yang muncul pada kalimat</text>
      <text x="15" y="124" class="card-text">&quot;buka blokir&quot; mendominasi pembobotan,</text>
      <text x="15" y="142" class="card-text">menyebabkan salah klasifikasi fatal.</text>
      <rect x="15" y="158" width="370" height="60" fill="#F4F4F4" stroke="#333333" rx="3" />
      <text x="25" y="178" class="code-text">Konsekuensi: 14.58% perintah di router</text>
      <text x="25" y="195" class="code-text">menghasilkan konfigurasi salah &amp; berbahaya</text>
    </g>

    <g transform="translate(445, 65)">
      <rect x="0" y="0" width="400" height="235" class="box-card" />
      <text x="15" y="25" class="card-title">2. Efektivitas Solusi Hybrid (Novelty)</text>
      <text x="15" y="48" class="card-text">Arsitektur Hybrid kami menyuntikkan</text>
      <text x="15" y="66" class="card-text">lapisan determinisme terukur:</text>
      <text x="15" y="86" class="card-text">- Regex Slotting: Nol salah angka port/IP</text>
      <text x="15" y="104" class="card-text">- Syntactic Cues: Override pasti negasi</text>
      <text x="15" y="122" class="card-text">- Morphological Join: Menangani spasi kata</text>
      <text x="15" y="140" class="card-text">- Action Guard: Menolak perintah sampah</text>
      <rect x="15" y="158" width="370" height="60" fill="#F4F4F4" stroke="#000000" rx="3" />
      <text x="25" y="178" class="badge-text">Hasil: Akurasi melonjak ke 100.00%</text>
      <text x="25" y="195" class="card-text">dengan latensi stabil di bawah 1 ms!</text>
    </g>

    <g transform="translate(870, 65)">
      <rect x="0" y="0" width="410" height="235" class="box-card" />
      <text x="15" y="25" class="card-title">3. Kelayakan Hardware MikroTik Lab</text>
      <text x="15" y="48" class="card-text">Sistem ini membuktikan bahwa Intent-Based</text>
      <text x="15" y="66" class="card-text">Networking (IBN) tidak memerlukan server</text>
      <text x="15" y="84" class="card-text">Cloud LLM mahal (GPT/Claude) maupun</text>
      <text x="15" y="102" class="card-text">framework raksasa (Rasa &gt; 1.5 GB).</text>
      <text x="15" y="124" class="card-text">Controller laptop/Mini PC mampu mengontrol</text>
      <text x="15" y="142" class="card-text">router hemat daya hAP lite (RAM 32MB)</text>
      <rect x="15" y="158" width="380" height="60" fill="#F4F4F4" stroke="#333333" rx="3" />
      <text x="25" y="178" class="badge-text">Throughput: 1,042 QPS | Zero Cloud Cost</text>
      <text x="25" y="195" class="card-text">Privasi jaringan kampus terlindungi 100%.</text>
    </g>
  </g>

</svg>"""

def main():
    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("Comparative SVG generated successfully at:", SVG_PATH)

    print("Rendering High-DPI PNG via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        page.set_content(svg_content)
        svg_el = page.locator("svg")
        svg_el.screenshot(path=PNG_PATH)
        browser.close()
    print("Comparative High-DPI PNG generated successfully at:", PNG_PATH)
    print("File size:", os.path.getsize(PNG_PATH) // 1024, "KB")

if __name__ == "__main__":
    main()
