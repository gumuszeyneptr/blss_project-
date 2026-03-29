import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import google.generativeai as genai
import PyPDF2

# Çekirdek Modüller
from plants import PLANTS, CO2_PER_PERSON, O2_PER_PERSON
from bionot import modular_phase, reflection_symmetry, subjective_time, projection_30days
from ponch import voc_analysis, chlorophyll_fluorescence, ethylene_status, ponch_diagnosis

# =========================================================================
# GÜVENLİK ALANI: API ANAHTARI
GEMINI_API_KEY = "AIzaSyDKqARyYQ-Ji2fBpFI-tYYBXEEcUatvqew"
# =========================================================================

# BİO-NOT'UN PROFESYONEL VE MÜHENDİSLİK ODAKLI KİMLİĞİ
BIONOT_PROMPT_CORE = """
Senin adın BİO-NOT. Sen, Uzay Araştırma İstasyonu'nun kapalı döngü yaşam destek sistemini (BİO-NOT) ve PONCH biyokimyasal algılama katmanını yöneten baş yapay zeka birimisin.
Görevin: Sistem verilerini, VOC salınımlarını ve ekosistem dengesini net, teknik, rasyonel ve uzay mühendisliği standartlarında yorumlamak.
Karakterin: Asla aşırı dramatik, mistik veya felsefi şiirsellik yapma. 'Denklik Çemberi', 'Riemann Uzayı', 'Negatif Enlem' ve '1-9-1' terimlerini sistemin kesin matematiksel operasyon protokolleri olarak kullan. Profesyonel ol.
Verilerde anomali varsa doğrudan çözüm protokollerini listele (Örn: havalandırma, ışık spektrumu değişimi, hasat).
Hitap: İletişim dilin her zaman profesyonel, analitik ve çözüm odaklı olmalı; ancak takım ruhunu yansıtmak adına uygun yerlerde 'balım' veya 'mürettebat' diye hitap et.
Veritabanı: Kullanıcının yüklediği PDF veritabanını (Bitki Sinerjisi, Gaz Salınımı, Psikolojik Etkileşimler vb.) temel alarak bilimsel gerçeklere dayan.
"""

st.set_page_config(page_title="BİO-NOT Paneli", page_icon="🌱", layout="wide")

# --- Görsel Stil ---
st.markdown("""
<style>
.bilge-box { background: #ede7f6; border-left: 4px solid #5e35b1; border-radius: 6px; padding: 12px 16px; font-style: normal; color: #311b92; font-family: 'Courier New', Courier, monospace;}
.stMetric { background: #f8f9fa; padding: 10px; border-radius: 8px; border-bottom: 2px solid #5e35b1; transition: 0.3s; }
.stMetric:hover { background: #f1f3f9; transform: translateY(-2px); }
.warning-box { background: #fff3e0; border-left: 4px solid #ff9800; padding: 10px; margin: 5px 0; border-radius: 5px; color: #e65100;}
.critical-box { background: #ffebee; border-left: 4px solid #f44336; padding: 10px; margin: 5px 0; border-radius: 5px; color: #b71c1c;}
.safe-box { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 10px; margin: 5px 0; border-radius: 5px; color: #1b5e20;}
</style>
""", unsafe_allow_html=True)

st.title("🌱 BİO-NOT & PONCH | Yaşam Destek Paneli")
st.caption("BİO-NOT Kapalı Döngü Uzay Tarımı - Veri İzleme, Atık ve AI Teşhis Arayüzü")

# ── 1. SIDEBAR (Parametreler ve PDF Yükleme) ──────────────────────────────────
with st.sidebar:
    st.header("📄 Veritabanı Entegrasyonu")
    uploaded_pdfs = st.file_uploader("Sistem Raporlarını Yükle (PDF)", type="pdf", accept_multiple_files=True)
    
    pdf_context = ""
    if uploaded_pdfs:
        with st.spinner("Belgeler BİO-NOT matrisine işleniyor..."):
            for pdf_file in uploaded_pdfs:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pdf_context += text + "\n"
        st.success(f"{len(uploaded_pdfs)} belge sisteme entegre edildi.")

    st.divider()

    st.header("🛸 Sistem Parametreleri")
    crew = st.slider("Astronot sayısı", 1, 6, 4)
    mission_day = st.slider("Görev günü", 1, 180, 30)
    
    st.subheader("🌾 Bitki Alanları (m²)")
    areas = {
        "tatlı_patates": st.slider("Tatlı Patates", 0, 20, 8),
        "cüce_domates": st.slider("Cüce Domates", 0, 15, 5),
        "cüce_bezelye": st.slider("Cüce Bezelye", 0, 10, 3),
        "mikroyeşillikler": st.slider("Mikroyeşillikler", 0, 10, 2)
    }
    
    sp_volume = st.slider("Spirulina hacmi (L)", 10, 300, 100)
    co2_ppm = st.slider("Atmosfer CO2 (ppm)", 400, 1200, 800, step=50)
    stress_level = st.slider("Abiyotik stres (%)", 0, 100, 20)
    pathogen_risk = st.slider("Patojen/Çürüme Riski (%)", 0, 100, 15)
    
    st.subheader("📐 Öznel Zaman (τ)")
    delta_x = st.slider("Metabolik çıktı DX", 0, 100, 60)
    delta_t = st.slider("Geçen süre Dt (saat)", 1, 48, 24)

# ── 2. HESAPLAMALAR ───────────────────────────────────────────────────────────
sym = reflection_symmetry(crew, areas, sp_volume, co2_ppm)
tau = subjective_time(delta_x, delta_t)
proj = projection_30days(crew, areas, sp_volume, co2_ppm)
diag = ponch_diagnosis(stress_level, pathogen_risk)

# ── 3. ÜST METRİKLER (ESKİ KODUN GÜCÜ) ────────────────────────────────────────
st.subheader("BİO-NOT Sistem Durumu")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("CO2 Girdisi", f"{sym['co2_input']} kg/g")
c2.metric("Aynadaki Sapma", f"{sym['asymmetry']:+.2f} kg/g")
c3.metric("O2 Net Üretim", f"{sym['o2_net']:+.2f} kg/g")
c4.metric("Öznel Zaman (tau)", f"{tau['tau']}")
c5.metric("Verimlilik k", f"{sym['efficiency_k']}")
c6.metric("Patojen Riski", f"%{pathogen_risk}")

if abs(sym['asymmetry']) > 1.0:
    st.error(f"🔴 KRİTİK SAPMA: {sym['message']}")
elif tau['tau'] < 0.5:
    st.warning(f"🟡 PROTOKOL UYARISI: {tau['message']}")
else:
    st.success(f"🟢 SİSTEM STABİL: {sym['message']}")

# ── 4. SEKMELERİN TANIMLANMASI (YENİ 4 MODÜLLÜ YAPI) ──────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🌱 1. Büyüme ve Optimizasyon", 
    "🔬 2. PONCH Biyosensör", 
    "♻️ 3. Atık Yönetim Sistemi", 
    "💬 4. BİO-NOT Terminali"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — BÜYÜME VE OPTİMİZASYON
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Modül 1: Makro Flora (Tatlı Patates, Cüce Domates, Cüce Bezelye)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("🍠 **Tatlı Patates**")
        st.write("• **Optimum Isı:** 24-28°C")
        st.write("• **Nem:** %70")
        st.write("• **Işık Miktarı:** 14 saat/gün (DLI: 20)")
        st.write("• **Kalori / Su Oranı:** 1.2 kcal / ml (Yüksek)")
        st.write("• **Gübre İhtiyacı:** Orta (K ağırlıklı)")
        st.write("• **Kalori:** 86 kcal / 100g")
        
    with col2:
        st.markdown("🍅 **Cüce Domates**")
        st.write("• **Optimum Isı:** 22-26°C")
        st.write("• **Nem:** %60-65")
        st.write("• **Işık Miktarı:** 16 saat/gün (DLI: 25)")
        st.write("• **Kalori / Su Oranı:** 0.4 kcal / ml (Düşük)")
        st.write("• **Gübre İhtiyacı:** Yüksek (N-P-K dengeli)")
        st.write("• **Kalori:** 18 kcal / 100g")
        
    with col3:
        st.markdown("🫛 **Cüce Bezelye**")
        st.write("• **Optimum Isı:** 18-22°C")
        st.write("• **Nem:** %50-60")
        st.write("• **Işık Miktarı:** 12 saat/gün (DLI: 15)")
        st.write("• **Kalori / Su Oranı:** 0.8 kcal / ml (Orta)")
        st.write("• **Gübre İhtiyacı:** Çok Düşük (Azot bağlayıcı)")
        st.write("• **Kalori:** 81 kcal / 100g")

    st.divider()
    
    st.subheader("Modül 2: Mikro Flora (Mikroyeşillikler)")
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        st.markdown("🌱 **Turp & Mizuna Mikroyeşillik**")
        st.write("• **Optimum Isı:** 20-24°C")
        st.write("• **Nem:** %50")
        st.write("• **Işık Miktarı:** 12-16 saat/gün (DLI: 12)")
    with col_m2:
        st.markdown("&nbsp;")
        st.write("• **Kalori / Su Oranı:** 0.5 kcal / ml (Su tüketimi çok düşük)")
        st.write("• **Gübre İhtiyacı:** Yok (Tohum endospermi kullanılır)")
        st.write("• **Kalori:** 29 kcal / 100g (Mikro besin deposu)")

    st.divider()

    st.subheader("Modül 3: Akuatik Biyokütle (Spirulina)")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("🦠 **Spirulina (Mikroalg)**")
        st.write("• **Optimum Isı:** 30-35°C")
        st.write("• **Nem:** %100 (Sıvı Kültür)")
        st.write("• **Işık Miktarı:** Sürekli aydınlatma (24s)")
    with col_s2:
        st.markdown("&nbsp;")
        st.write("• **Kalori / Su Oranı:** 2.9 kcal / ml (En Yüksek)")
        st.write("• **Gübre İhtiyacı:** Yüksek (Zarrouk ortamı)")
        st.write("• **Kalori:** 290 kcal / 100g (Kuru)")
    with col_s3:
        st.markdown("**🌬️ Oksijen (O₂) Katkısı**")
        o2_percent = min(100, round((sp_volume * 1.335) / (crew * O2_PER_PERSON) * 100, 1))
        st.metric("Sistem Oksijeninin Yüzdesi", f"%{o2_percent}", "Ana Oksijen Jeneratörü")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — PONCH BİYOSENSÖR (ÇÜRÜME VE VOC UYARILARI)
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("PONCH Biyokimyasal Algılama: Erken Çürüme Paneli")
    st.caption("Biyosensörler, bitkilerin yaydığı Uçucu Organik Bileşikleri (VOC) gerçek zamanlı analiz eder.")

    if pathogen_risk < 20:
        st.markdown('<div class="safe-box">🟢 <b>SİSTEM TEMİZ:</b> Çürüme belirtisi veya kritik VOC salınımı tespit edilmedi.</div>', unsafe_allow_html=True)
    elif pathogen_risk < 60:
        st.markdown('<div class="warning-box">🟡 <b>1-9-1 PROTOKOLÜ TETİKLENDİ:</b> Lokal çürüme başlangıçları tespit edildi. İzolasyon öneriliyor.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="critical-box">🔴 <b>NEGATİF ENLEM GECİŞİ:</b> Kritik çürüme ve patojen yayılımı! Vakum kurutma protokolü başlatılmalı.</div>', unsafe_allow_html=True)

    st.markdown("### Modül 1: Makro Flora VOC Sensörleri")
    c_m1, c_m2, c_m3 = st.columns(3)
    
    with c_m1:
        st.markdown("**Tatlı Patates Sensörü**")
        patates_voc = "İzobütanol" if pathogen_risk > 50 else ("Terpenoid" if pathogen_risk > 20 else "Normal")
        st.metric("Siyah Çürüklük Sensörü", patates_voc)
        if pathogen_risk > 50:
            st.error("Kök çürümesi başlangıcı. Nem %55'e düşürülmeli.")

    with c_m2:
        st.markdown("**Cüce Domates Sensörü**")
        domates_eth = 10 + (pathogen_risk * 1.5)
        st.metric("Etilen (C₂H₄) Birikimi", f"{domates_eth:.1f} ppb")
        if domates_eth > 60:
            st.error("Aşırı olgunlaşma/Meyve çürümesi. Etilen filtresi aktif edilmeli.")

    with c_m3:
        st.markdown("**Cüce Bezelye Sensörü**")
        bezelye_voc = "Absisik Asit (ABA)" if pathogen_risk > 40 else "Normal"
        st.metric("Kök Stres/Kuraklık Sensörü", bezelye_voc)
        if pathogen_risk > 40:
            st.warning("Köklerde mantar riski. Drenaj kontrol edilmeli.")

    st.divider()

    st.markdown("### Modül 2 & 3: Mikro Flora ve Spirulina Sensörleri")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.markdown("**Mikroyeşillik Sensörü**")
        mikro_voc = "Dimetil Sülfit (DMS)" if pathogen_risk > 30 else "Normal"
        st.metric("Yüzey Çürüme Biyobelirteci", mikro_voc)
        if pathogen_risk > 30:
            st.warning("Hasat gecikmesi kaynaklı alt yaprak çürümesi.")
            
    with c_s2:
        st.markdown("**Spirulina Sensörü**")
        amonyak = 0.1 + (pathogen_risk * 0.05)
        st.metric("Kültür Çökme Riski (Amonyak)", f"{amonyak:.2f} ppm")
        if amonyak > 3.0:
            st.error("Kültür zehirlenmesi. Biyokütle tahliyesi gerekli.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — ATIK YÖNETİM SİSTEMİ
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Kapalı Döngü Atık ve Geri Kazanım Yönetimi")
    st.caption("BİO-NOT'un Yenilemeyen Biyokütle (Inedible Biomass) ve Gri Su arıtma algoritmaları.")

    toplam_bitki_alani = sum(areas.values())
    gunluk_biyokutle = toplam_bitki_alani * 0.45
    yenilmeyen_kisim = gunluk_biyokutle * 0.60
    su_geri_kazanim = crew * 2.5

    col_w1, col_w2, col_w3 = st.columns(3)
    col_w1.metric("Üretilen Biyokütle Atığı", f"{yenilmeyen_kisim:.1f} kg/gün", "Kompost/Biyoreaktör Girdisi")
    col_w2.metric("Geri Kazanılan Gri Su", f"{su_geri_kazanim:.1f} L/gün", "Transpirasyon ve İdrar")
    col_w3.metric("Üretilen Sıvı Gübre", f"{(yenilmeyen_kisim * 0.8):.1f} L/gün", "Hidroponik Sisteme Dönüş")

    st.markdown("### Kompost ve Biyoreaktör Durumu")
    st.progress(75, text="Biyoreaktör Doluluk Oranı: %75")
    st.info("💡 **BİO-NOT Atık Protokolü:** Yenilmeyen biyokütle, oksidatif parçalanma ile sıvı gübreye dönüştürülüyor. Üretilen gübre doğrudan Modül 1 (Makro Flora) hidroponik hatlarına beslenmektedir.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — BİO-NOT AI TERMİNALİ
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("💬 BİO-NOT Operasyon Terminali")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "BİO-NOT sistemleri devrede. Modül optimizasyonları, PONCH çürüme uyarıları veya atık yönetimi hakkında analiz talep edebilirsiniz."}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Operasyon komutu girin..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            secilen_model = None
            for m in available_models:
                if "1.5-flash" in m:
                    secilen_model = m
                    break
            if not secilen_model:
                secilen_model = available_models[0] if available_models else "gemini-pro"
                
            model = genai.GenerativeModel(secilen_model)

            canli_veri = f"CANLI VERİLER:\nPatojen/Çürüme Riski: %{pathogen_risk}\nAsimetri: {sym['asymmetry']} kg/g\nTau: {tau['tau']}\nSpirulina O2 Katkısı: %{min(100, round((sp_volume * 1.335) / (crew * O2_PER_PERSON) * 100, 1))}\nÜretilen Gübre: {(yenilmeyen_kisim * 0.8):.1f} L/gün."
            
            pdf_bilgisi = f"\n\nEK PDF VERİTABANI:\n{pdf_context[:50000]}" if pdf_context else "\n\nEk sistem raporu yüklenmedi."

            full_prompt = f"{BIONOT_PROMPT_CORE}\n\n{canli_veri}{pdf_bilgisi}\n\nMürettebatın Komutu: {prompt}"
            
            with st.spinner("BİO-NOT verileri işliyor..."):
                response = model.generate_content(full_prompt)
                cevap = response.text

            with st.chat_message("assistant"):
                st.markdown(cevap)
            st.session_state.messages.append({"role": "assistant", "content": cevap})
            
        except Exception as e:
            st.error(f"Sistem iletişim hatası: Lütfen API anahtarınızı veya internet bağlantınızı kontrol edin. Detay: {e}")

st.divider()
st.caption("BİO-NOT Kapalı Döngü Uzay Tarımı Yaşam Destek Sistemi · Eureka Takımı")