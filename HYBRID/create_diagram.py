import os
from playwright.sync_api import sync_playwright

SVG_PATH = r"D:\KULIAH S1\RISET JARKOM\TEST\PRAKTIK_IBN\GAMBAR\diagram_arsitektur_ibn_mikrotik.svg"
PNG_PATH = r"D:\KULIAH S1\RISET JARKOM\TEST\PRAKTIK_IBN\GAMBAR\diagram_arsitektur_ibn_mikrotik.png"

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 2360" width="1400" height="2360">
  <defs>
    <style>
      .bg { fill: #FFFFFF; }
      .title-main { font-family: 'Segoe UI', Arial, sans-serif; font-size: 26px; font-weight: bold; fill: #000000; text-anchor: middle; }
      .title-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; fill: #444444; text-anchor: middle; }
      .meta-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; fill: #666666; text-anchor: middle; }
      .phase-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 18px; font-weight: bold; fill: #000000; }
      .phase-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-style: italic; fill: #555555; }
      .card-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: bold; fill: #000000; }
      .card-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; fill: #222222; }
      .code-text { font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; fill: #111111; }
      .badge-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #000000; }
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

  <!-- Background -->
  <rect width="1400" height="2360" class="bg" />

  <!-- HEADER BLOCK -->
  <rect x="50" y="30" width="1300" height="120" fill="#FFFFFF" stroke="#000000" stroke-width="2" rx="8" />
  <text x="700" y="70" class="title-main">ALUR ARSITEKTUR INTENT-BASED NETWORKING (IBN) MIKROTIK</text>
  <text x="700" y="98" class="title-sub">Pipeline End-to-End: Natural Language Intake -> Hybrid NLP -> Policy Engine -> RouterOS API -> Real Network Behavior</text>
  <text x="700" y="126" class="meta-text">Target: MikroTik hAP lite (RouterOS v6.49.17) | Controller: Python 3.12 (librouteros) | NLP: Scikit-Learn TF-IDF (35 KB) + Regex</text>

  <!-- ========================================== -->
  <!-- FASE 1: INPUT ALAMI (OPERATOR INTAKE LAYER) -->
  <!-- ========================================== -->
  <rect x="50" y="180" width="1300" height="220" class="box-container" />
  <rect x="70" y="200" width="280" height="32" fill="#E5E5E5" stroke="#000000" stroke-width="1.5" rx="4" />
  <text x="85" y="222" class="phase-title">FASE 1: OPERATOR INTAKE</text>
  <text x="365" y="222" class="phase-sub">Antarmuka CLI Interaktif (main_ibn.py) menerima kalimat bebas berbahasa Indonesia</text>

  <!-- Contoh Input Kartu -->
  <g transform="translate(80, 250)">
    <rect x="0" y="0" width="280" height="125" class="box-card" />
    <text x="15" y="25" class="card-title">1. Limit Bandwidth Host</text>
    <text x="15" y="50" class="card-text">Contoh Kalimat:</text>
    <rect x="15" y="60" width="250" height="50" fill="#F8F8F8" stroke="#CCCCCC" rx="4" />
    <text x="25" y=\"82\" class="code-text">&quot;Batasi bandwidth</text>
    <text x="25" y="100" class="code-text"> 192.168.88.50 jadi 2 Mbps&quot;</text>
  </g>

  <g transform="translate(385, 250)">
    <rect x="0" y="0" width="280" height="125" class="box-card" />
    <text x="15" y="25" class="card-title">2. Limit Port Fisik (Interface)</text>
    <text x="15" y="50" class="card-text">Contoh Kalimat:</text>
    <rect x="15" y="60" width="250" height="50" fill="#F8F8F8" stroke="#CCCCCC" rx="4" />
    <text x="25" y="82" class="code-text">&quot;saya ingin port 3</text>
    <text x="25" y="100" class="code-text"> kasih limit 5mb&quot;</text>
  </g>

  <g transform="translate(690, 250)">
    <rect x="0" y="0" width="280" height="125" class="box-card" />
    <text x="15" y="25" class="card-title">3. Firewall Drop Port Spesifik</text>
    <text x="15" y="50" class="card-text">Contoh Kalimat:</text>
    <rect x="15" y="60" width="250" height="50" fill="#F8F8F8" stroke="#CCCCCC" rx="4" />
    <text x="25" y="82" class="code-text">&quot;blokir port 80 untuk</text>
    <text x="25" y="100" class="code-text"> 192.168.88.50&quot;</text>
  </g>

  <g transform="translate(995, 250)">
    <rect x="0" y="0" width="280" height="125" class="box-card" />
    <text x="15" y="25" class="card-title">4. Global Drop &amp; Rollback</text>
    <text x="15" y="50" class="card-text">Contoh Kalimat:</text>
    <rect x="15" y="60" width="250" height="50" fill="#F8F8F8" stroke="#CCCCCC" rx="4" />
    <text x="25" y="82" class="code-text">&quot;blokir port 443&quot; /</text>
    <text x="25" y="100" class="code-text">&quot;buka blokir port 80&quot;</text>
  </g>

  <!-- Panah Penghubung Fase 1 ke Fase 2 -->
  <line x1="700" y1="400" x2="700" y2="450" class="line-main" />
  <rect x="550" y="415" width="300" height="20" fill="#FFFFFF" stroke="#000000" rx="3" />
  <text x="700" y="429" class="arrow-text">Raw String Teks Bahasa Alami</text>

  <!-- ========================================== -->
  <!-- FASE 2: HYBRID NLP ENGINE (nlp_parser.py)  -->
  <!-- ========================================== -->
  <rect x="50" y="450" width="1300" height="390" class="box-container" />
  <rect x="70" y="470" width="340" height="32" fill="#E5E5E5" stroke="#000000" stroke-width="1.5" rx="4" />
  <text x="85" y="492" class="phase-title">FASE 2: LIGHTWEIGHT HYBRID NLP</text>
  <text x="425" y="492" class="phase-sub">Pemisahan Jalur Probabilistik (Machine Learning) &amp; Jalur Deterministik (Regex)</text>

  <!-- Jalur Kiri: Machine Learning -->
  <g transform="translate(80, 520)">
    <rect x="0" y="0" width="580" height="220" class="box-card" />
    <rect x="15" y="15" width="320" height="25" fill="#F0F0F0" stroke="#333333" rx="3" />
    <text x="25" y="32" class="card-title">JALUR 1: Intent Classification (ML)</text>
    
    <text x="15" y="65" class="card-text">- Model: Scikit-Learn TF-IDF (1,2-gram) + LogisticRegression</text>
    <text x="15" y="85" class="card-text">- Dataset: dataset_intent.json (120 kalimat, 4 kelas seimbang)</text>
    <text x="15" y="105" class="card-text">- Footprint: Sangat Ringan (File model: intent_model.joblib 35.37 KB)</text>
    <text x="15" y="125" class="card-text">- Latensi Inferensi: &lt; 1.0 ms (RAM &lt; 15 MB)</text>
    
    <rect x="15" y="145" width="550" height="60" fill="#FAFAFA" stroke="#000000" stroke-dasharray="3,3" rx="4" />
    <text x="25" y="165" class="badge-text">Output Intent Terdeteksi &amp; Confidence Score:</text>
    <text x="25" y="188" class="code-text">limit_bandwidth | remove_limit | block_traffic | unblock_traffic</text>
  </g>

  <!-- Jalur Kanan: Regex Entity & Syntactic Cues -->
  <g transform="translate(695, 520)">
    <rect x="0" y="0" width="630" height="220" class="box-card" />
    <rect x="15" y="15" width="340" height="25" fill="#F0F0F0" stroke="#333333" rx="3" />
    <text x="25" y="32" class="card-title">JALUR 2: Regex Entity &amp; Disambiguasi</text>
    
    <text x="15" y="65" class="card-text">- IP Regex: \\b(?:\\d{1,3}\\.){3}\\d{1,3}(?:/\\d{1,2})?\\b</text>
    <text x="15" y="85" class="card-text">- Rate Regex: \\b\\d+(?:\\.\\d+)?\\s*(mbps|mb|mega|kbps|k|g)\\b</text>
    <text x="15" y="105" class="card-text">- Port Fisik (Interface): &quot;port X&quot; / &quot;ether X&quot; -&gt; ether1..ether4</text>
    <text x="15" y="125" class="card-text">- Port Layanan &amp; Aliases: &quot;port 80&quot;, &quot;port 443&quot;, http, https, ssh, dns</text>
    
    <rect x="15" y="145" width="600" height="60" fill="#FAFAFA" stroke="#000000" stroke-dasharray="3,3" rx="4" />
    <text x="25" y="165" class="badge-text">Syntactic Cue Disambiguation (Aturan Sintaksis):</text>
    <text x="25" y="188" class="card-text">Kata pembalikan (&quot;buka&quot;, &quot;cabut&quot;, &quot;unblock&quot;) override intent ke unblock/remove</text>
  </g>

  <!-- Agregator Hasil NLP -->
  <g transform="translate(80, 755)">
    <rect x="0" y="0" width="1245" height="65" fill="#FFFFFF" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="20" y="25" class="badge-text">HASIL AGREGASI NLP (nlp_parser.parse_intent) - Total Latensi: ~1.2 ms :</text>
    <text x="20" y="48" class="code-text">{ intent: &quot;limit_bandwidth&quot;, confidence: 0.85, entities: { target: &quot;ether3&quot;, rate: &quot;5mb&quot;, dst_port: null } }</text>
  </g>

  <!-- Panah Penghubung Fase 2 ke Fase 3 -->
  <line x1="700" y1="840" x2="700" y2="890" class="line-main" />
  <rect x="540" y="855" width="320" height="20" fill="#FFFFFF" stroke="#000000" rx="3" />
  <text x="700" y="869" class="arrow-text">Entitas &amp; Intent Hasil Ekstraksi NLP</text>

  <!-- ============================================== -->
  <!-- FASE 3: POLICY ENGINE & SAFETY (policy_engine) -->
  <!-- ============================================== -->
  <rect x="50" y="890" width="1300" height="470" class="box-container" />
  <rect x="70" y="910" width="360" height="32" fill="#E5E5E5" stroke="#000000" stroke-width="1.5" rx="4" />
  <text x="85" y="932" class="phase-title">FASE 3: POLICY &amp; SAFETY ENGINE</text>
  <text x="445" y="932" class="phase-sub">Penerjemahan Kebijakan Agnostik Vendor &amp; Pengecekan Guard-Rails Keamanan</text>

  <!-- 3 Kotak Verifikasi Keamanan -->
  <g transform="translate(80, 960)">
    <rect x="0" y="0" width="385" height="160" class="box-card" />
    <text x="15" y="25" class="card-title">1. Normalisasi Rate &amp; Target</text>
    <text x="15" y="50" class="card-text">- &quot;2 Mbps&quot; / &quot;9mb&quot; -&gt; &quot;2M/2M&quot; / &quot;9M/9M&quot;</text>
    <text x="15" y="72" class="card-text">- &quot;512 kbps&quot; -&gt; &quot;512k/512k&quot;</text>
    <text x="15" y="94" class="card-text">- IP: &quot;192.168.88.50&quot; -&gt; &quot;.../32&quot;</text>
    <text x="15" y="116" class="card-text">- Subnet: &quot;192.168.88.0/24&quot;</text>
    <text x="15" y="138" class="card-text">- Interface: ether1..ether4, wlan1</text>
  </g>

  <g transform="translate(490, 960)">
    <rect x="0" y="0" width="395" height="160" class="box-card" />
    <text x="15" y="25" class="card-title">2. Proteksi Anti-Lockout Router</text>
    <text x="15" y="50" class="card-text">- Melindungi IP Router: 192.168.88.1</text>
    <text x="15" y="72" class="card-text">- Melindungi IP Controller Laptop</text>
    <text x="15" y="94" class="card-text">- Melindungi Subnet Manajemen</text>
    <rect x="15" y="108" width="365" height="40" fill="#F4F4F4" stroke="#333333" rx="3" />
    <text x="25" y="125" class="code-text">Jika ada perintah blokir IP router:</text>
    <text x="25" y="140" class="code-text">REJECT: Anti-lockout Protection Active</text>
  </g>

  <g transform="translate(910, 960)">
    <rect x="0" y="0" width="415" height="160" class="box-card" />
    <text x="15" y="25" class="card-title">3. Validasi Hardware Catalog</text>
    <text x="15" y="50" class="card-text">- Verifikasi batas fisik router hAP lite</text>
    <text x="15" y="72" class="card-text">- Tersedia: ether1, ether2, ether3, ether4, wlan1</text>
    <rect x="15" y="90" width="385" height="58" fill="#F4F4F4" stroke="#333333" rx="3" />
    <text x="25" y="110" class="code-text">Jika user meminta &quot;port 5&quot;:</text>
    <text x="25" y="125" class="code-text">REJECT: Interface ether5 tidak ada di</text>
    <text x="25" y="140" class="code-text">hAP lite (tersedia: ether1-ether4)</text>
  </g>

  <!-- Kotak Intermediate Policy JSON -->
  <g transform="translate(80, 1140)">
    <rect x="0" y="0" width="1245" height="105" class="box-card-gray" />
    <text x="20" y="25" class="card-title">INTERMEDIATE POLICY JSON (Agnostik Vendor - Siap Eksekusi):</text>
    <text x="20" y="50" class="code-text">{</text>
    <text x="35" y="68" class="code-text">&quot;intent&quot;: &quot;limit_bandwidth&quot;,  &quot;action&quot;: &quot;apply_bandwidth_limit&quot;,  &quot;target&quot;: &quot;ether3&quot;,  &quot;rate&quot;: &quot;5M/5M&quot;,</text>
    <text x="35" y="88" class="code-text">&quot;dst_port&quot;: null,  &quot;protocol&quot;: null,  &quot;name&quot;: &quot;qos_ether3&quot;,  &quot;is_valid&quot;: true,  &quot;error&quot;: null</text>
    <text x="20" y="102" class="code-text">}</text>
  </g>

  <!-- Decision Gate: Apakah Policy Valid? -->
  <g transform="translate(580, 1265)">
    <polygon points="120,0 240,40 120,80 0,40" class="box-decision" />
    <text x="120" y="38" class="badge-text" text-anchor="middle">Apakah Policy</text>
    <text x="120" y="54" class="badge-text" text-anchor="middle">Valid &amp; Aman?</text>
  </g>

  <!-- Cabang Ditolak (Kiri) -->
  <line x1="580" y1="1305" x2="280" y2="1305" class="line-main" />
  <line x1="280" y1="1305" x2="280" y2="1340" class="line-main" />
  <rect x="130" y="1340" width="300" height="50" fill="#FFFFFF" stroke="#000000" stroke-width="1.5" rx="4" />
  <text x="280" y="1362" class="badge-text" text-anchor="middle">[TIDAK] BATALKAN EKSEKUSI</text>
  <text x="280" y="1380" class="card-text" text-anchor="middle">Tampilkan alasan edukatif di CLI</text>

  <!-- Cabang Valid (Bawah) -->
  <line x1="700" y1="1345" x2="700" y2="1410" class="line-main" />
  <text x="715" y="1380" class="badge-text">[YA]</text>

  <!-- ============================================== -->
  <!-- FASE 4: MIKROTIK ADAPTER & IDEMPOTENCY ENGINE  -->
  <!-- ============================================== -->
  <rect x="50" y="1410" width="1300" height="390" class="box-container" />
  <rect x="70" y="1430" width="380" height="32" fill="#E5E5E5" stroke="#000000" stroke-width="1.5" rx="4" />
  <text x="85" y="1452" class="phase-title">FASE 4: ADAPTER &amp; IDEMPOTENCY</text>
  <text x="465" y="1452" class="phase-sub">Penerjemahan Policy ke RouterOS Command &amp; Proteksi Memori hAP lite (RAM 32MB)</text>

  <!-- Kotak Pre-flight Inspection & Idempotency -->
  <g transform="translate(80, 1480)">
    <rect x="0" y="0" width="580" height="190" class="box-card" />
    <text x="15" y="25" class="card-title">1. Pre-Flight State Inspection (Cek Tabel)</text>
    <text x="15" y="50" class="card-text">Sebelum menambahkan rule baru, Controller membaca state:</text>
    <text x="15" y="72" class="code-text">- Query: /queue/simple/print (QoS)</text>
    <text x="15" y="92" class="code-text">- Query: /ip/firewall/filter/print (Firewall)</text>
    <text x="15" y="120" class="card-title">2. Prinsip Idempotency (Anti-Duplikasi):</text>
    <text x="15" y="142" class="card-text">- Jika rule sudah ada: Lakukan update (set) atau noop</text>
    <text x="15" y="162" class="card-text">- Jika rule belum ada: Lakukan penambahan (add)</text>
    <text x="15" y="182" class="badge-text">Hasil: Mencegah pemborosan RAM hAP lite (Free ~8.4 MB)</text>
  </g>

  <!-- Kotak Protokol Transport API -->
  <g transform="translate(695, 1480)">
    <rect x="0" y="0" width="630" height="190" class="box-card" />
    <text x="15" y="25" class="card-title">3. Protokol Transport: RouterOS Binary API</text>
    <text x="15" y="50" class="card-text">- Port Transport: TCP Port 8728 (Active Service di RouterOS v6)</text>
    <text x="15" y="72" class="card-text">- Pustaka Python: librouteros (Socket Transport Cepat)</text>
    <text x="15" y="92" class="card-text">- Keamanan Autentikasi: Login plain/token credentials</text>
    
    <rect x="15" y="110" width="600" height="65" fill="#F4F4F4" stroke="#333333" rx="3" />
    <text x="25" y="130" class="code-text">API Sentence Dispatched:</text>
    <text x="25" y="148" class="code-text">/queue/simple/add =name=qos_ether3 =target=ether3 =max-limit=5M/5M</text>
    <text x="25" y="165" class="code-text">/ip/firewall/filter/add =chain=forward =action=drop =protocol=tcp =dst-port=80</text>
  </g>

  <!-- Feedback Banner Controller -->
  <g transform="translate(80, 1690)">
    <rect x="0" y="0" width="1245" height="85" fill="#FFFFFF" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="20" y="25" class="card-title">FEEDBACK INSTAN KE OPERATOR (CLI TERMINAL):</text>
    <text x="20" y="48" class="code-text">[STATUS: SUKSES] Aksi: added | Rule ID: *36 | Target: ether3 | Max Limit: 5M/5M</text>
    <text x="20" y="68" class="code-text">Total Latensi Eksekusi: 16.44 ms (NLP: 1.25 ms + Policy: 0.15 ms + RouterOS API: 15.04 ms)</text>
  </g>

  <!-- Panah Penghubung Fase 4 ke Fase 5 -->
  <line x1="700" y1="1800" x2="700" y2="1850" class="line-main" />
  <rect x="540" y="1815" width="320" height="20" fill="#FFFFFF" stroke="#000000" rx="3" />
  <text x="700" y="1829" class="arrow-text">Eksekusi Konfigurasi ke Router Fisik</text>

  <!-- ============================================== -->
  <!-- FASE 5: ROUTER FISIK & PERILAKU JARINGAN NYATA -->
  <!-- ============================================== -->
  <rect x="50" y="1850" width="1300" height="440" class="box-container" />
  <rect x="70" y="1870" width="430" height="32" fill="#E5E5E5" stroke="#000000" stroke-width="1.5" rx="4" />
  <text x="85" y="1892" class="phase-title">FASE 5: ROUTER FISIK &amp; PERILAKU NYATA</text>
  <text x="515" y="1892" class="phase-sub">Perubahan Tabel Konfigurasi RouterOS &amp; Dampak Empiris pada Trafik Jaringan</text>

  <!-- Kartu Router Fisik -->
  <g transform="translate(80, 1920)">
    <rect x="0" y="0" width="580" height="210" class="box-card" />
    <text x="15" y="25" class="card-title">MikroTik RouterOS v6.49.17 (hAP lite Fisik)</text>
    <text x="15" y="50" class="card-text">Spesifikasi Hardware Lab:</text>
    <text x="15" y="70" class="card-text">- Arsitektur: smips (CPU MIPS 24Kc @ 650 MHz, 1 Core)</text>
    <text x="15" y="90" class="card-text">- Memori: RAM 32 MB (Free ~8.4 MB) | Flash 16 MB</text>
    <text x="15" y="110" class="card-text">- Interface Aktif: ether1 (WAN), ether2 (Bridge), ether3, ether4, wlan1</text>
    
    <rect x="15" y="130" width="550" height="65" fill="#F4F4F4" stroke="#333333" rx="3" />
    <text x="25" y="150" class="badge-text">Mutasi Tabel Aktif di Winbox:</text>
    <text x="25" y="168" class="code-text">1. Simple Queue: /queue simple add name=qos_ether3 target=ether3 max-limit=5M/5M</text>
    <text x="25" y="185" class="code-text">2. Filter Table : /ip firewall filter add chain=forward action=drop dst-port=80</text>
  </g>

  <!-- Kartu Perilaku Jaringan Nyata -->
  <g transform="translate(695, 1920)">
    <rect x="0" y="0" width="630" height="210" class="box-card" />
    <text x="15" y="25" class="card-title">Observable Network Behavior (Dampak Trafik)</text>
    <text x="15" y="50" class="card-text">Pengujian Empiris pada Client Uji (Laptop / HP):</text>
    
    <g transform="translate(15, 65)">
      <rect x="0" y="0" width="290" height="125" fill="#FAFAFA" stroke="#000000" rx="4" />
      <text x="15" y="25" class="badge-text">Uji QoS (Limit Bandwidth):</text>
      <text x="15" y="48" class="card-text">- Pengujian: iperf3 / Speedtest</text>
      <text x="15" y="70" class="card-text">- Hasil: Throughput tercekik</text>
      <text x="15" y="92" class="card-text">  secara presisi sesuai limit</text>
      <text x="15" y="112" class="code-text">(misal: tepat 5 Mbps / 2 Mbps)</text>
    </g>

    <g transform="translate(320, 65)">
      <rect x="0" y="0" width="295" height="125" fill="#FAFAFA" stroke="#000000" rx="4" />
      <text x="15" y="25" class="badge-text">Uji Firewall (Traffic Drop):</text>
      <text x="15" y="48" class="card-text">- Pengujian: ping &amp; curl port 80</text>
      <text x="15" y="70" class="card-text">- Hasil: Paket drop seketika</text>
      <text x="15" y="92" class="card-text">  (RTO / Connection Refused)</text>
      <text x="15" y="112" class="code-text">Layanan web langsung terblokir</text>
    </g>
  </g>

  <!-- Closed-Loop Feedback Loop Line -->
  <g transform="translate(80, 2150)">
    <rect x="0" y="0" width="1245" height="115" fill="#FFFFFF" stroke="#000000" stroke-width="1.5" rx="4" />
    <text x="20" y="25" class="card-title">CLOSED-LOOP VALIDATION &amp; ASSURANCE CYCLE (SIKLUS TERTUTUP):</text>
    <text x="20" y="50" class="card-text">1. State Inspection: Controller memverifikasi ulang perubahan di router via query /print sesaat setelah eksekusi.</text>
    <text x="20" y="72" class="card-text">2. Rollback Capability: Perintah pembalikan (&quot;cabut limit port 3&quot; / &quot;buka blokir port 80&quot;) mengembalikan router ke kondisi awal.</text>
    <text x="20" y="94" class="badge-text">3. Zero Residual Rules: Sistem menjamin tidak ada rule sampah yang tertinggal sehingga stabilitas router terjaga 100%.</text>
  </g>

</svg>"""

def main():
    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("SVG generated successfully at:", SVG_PATH)

    print("Rendering High-DPI PNG via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2)
        # load file
        page.set_content(svg_content)
        svg_el = page.locator("svg")
        svg_el.screenshot(path=PNG_PATH)
        browser.close()
    print("High-DPI PNG generated successfully at:", PNG_PATH)
    print("File size:", os.path.getsize(PNG_PATH) // 1024, "KB")

if __name__ == "__main__":
    main()
