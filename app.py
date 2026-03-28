import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import google.generativeai as genai

from plants import PLANTS, CO2_PER_PERSON, O2_PER_PERSON
from bionot import modular_phase, reflection_symmetry, subjective_time, projection_30days
from ponch import voc_analysis, chlorophyll_fluorescence, ethylene_status, ponch_diagnosis

# =========================================================================
# GÜVENLİK ALANI: API ANAHTARI
GEMINI_API_KEY = "AIzaSyBDTem4FLlz-htQR32R3rYZfkTMsw41NaM"
# =========================================================================

# BİO-NOT'UN DİJİTAL BEYNİ
BLSS_BILGI_BANKASI = """
TEMEL KAVRAMLAR:
- BLSS (Biyorejeneratif Yaşam Destek Sistemi): Oksijen üretimi, CO2 giderimi ve gıda sağlayan kapalı döngü.
- Bitki Psikolojisi & VOC: Bitkiler arası haberleşme uçucu organik bileşikler (VOC) ile sağlanır. GLV hasar sinyali, Terpenoidler abiyotik stres direncidir. Linalool rahatlatıcı etki yapar.
BITKILER:
1. Tatlı Patates: Karbon sabitleyici. Siyah çürüklükte 55 farklı VOC yayar.
2. Cüce Domates: Olgunlaşma evresinde yoğun Etilen salgılar. Toksiktir, epinastiye yol açar.
3. Cüce Bezelye: %45 CO2 sekestrasyonu yapar. Kuraklıkta Absisik asit yayar.
4. Spirulina: 1 kg Spirulina = 1.335 kg O2 üretir.
5. Mikroyeşillikler: Hızlı gıda kaynağı. Turp raphasatin, Mizuna 2-hexenal yayar.
YAPAY ZEKA MODÜLLERİ:
- PONCH: VOC ve Klorofil Floresansı üzerinden teşhis yapar.
- BİO-NOT: Matematiksel karar motoru (Öznel Zaman, Yansıma Simetrisi, Modüler Aritmetik).
"""

st.set_page_config(page_title="BLSS Paneli", page_icon="🌱", layout="wide")

st.markdown("""
<style>
.bilge-box {
    background: #ede7f6;
    border-left: 4px solid #5e35b1;
    border-radius: 6px;
    padding: 12px 16px;
    font-style: italic;
    color: #311b92;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🌱 BLSS Simülasyon Paneli")
st.caption("Biyorejeneratif Yaşam Destek Sistemleri — BİO-NOT & PONCH Entegrasyonu")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Sistem Parametreleri")

    st.subheader("Mürettebat")
    crew        = st.slider("Astronot sayısı", 1, 6, 4)
    mission_day = st.slider("Görev günü", 1, 180, 30)

    st.subheader("Bitki Alanları (m²)")
    area_tp = st.slider("Tatlı Patates", 0, 20, 8)
    area_cd = st.slider("Cüce Domates",  0, 15, 5)
    area_bz = st.slider("Cüce Bezelye",  0, 10, 3)
    area_my = st.slider("Mikroyeşillikler", 0, 10, 2)

    st.subheader("Spirulina")
    sp_volume = st.slider("Spirulina hacmi (L)", 10, 300, 100)

    st.subheader("Atmosfer")
    co2_ppm = st.slider("CO₂ set değeri (ppm)", 400, 1200, 800, step=50)

    st.subheader("PONCH Parametreleri")
    stress_level  = st.slider("Abiyotik stres (%)", 0, 100, 20)
    pathogen_risk = st.slider("Patojen riski (%)",  0, 100, 5)

    st.subheader("Öznel Zaman (τ)")
    delta_x = st.slider("Metabolik çıktı ΔX", 0, 100, 60)
    delta_t = st.slider("Geçen süre Δt (saat)", 1, 48, 24)

# ── Hesaplamalar ──────────────────────────────────────────────────────────────
areas = {
    "tatlı_patates":    area_tp,
    "cüce_domates":     area_cd,
    "cüce_bezelye":     area_bz,
    "mikroyeşillikler": area_my,
}

sym  = reflection_symmetry(crew, areas, sp_volume, co2_ppm)
tau  = subjective_time(delta_x, delta_t)
proj = projection_30days(crew, areas, sp_volume, co2_ppm)
diag = ponch_diagnosis(stress_level, pathogen_risk)

# ── Üst metrik kartları ───────────────────────────────────────────────────────
st.subheader("Anlık Sistem Durumu")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("CO₂ Üretim",   f"{sym['co2_input']} kg/gün",  f"{crew} kişi")
c2.metric("CO₂ Emilim",   f"{sym['total_co2_abs']} kg/gün")
c3.metric("O₂ Üretim",    f"{sym['total_o2']} kg/gün",   f"İhtiyaç: {sym['o2_need']}")
c4.metric("O₂ Net",       f"{sym['o2_net']:+.2f} kg/gün")
c5.metric("Asimetri",     f"{sym['asymmetry']:+.2f} kg/gün")
c6.metric("Verimlilik k", f"{sym['efficiency_k']}")

if sym["status"] == "critical":
    st.error(f"🔴 BİO-NOT: {sym['message']}")
elif sym["status"] == "warning":
    st.warning(f"🟡 BİO-NOT: {sym['message']}")
elif sym["status"] == "surplus":
    st.info(f"🔵 BİO-NOT: {sym['message']}")
else:
    st.success(f"🟢 BİO-NOT: {sym['message']}")

# ── Sekmeler ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌿 Bitki Döngüleri",
    "💨 Gaz Dengesi",
    "🔬 PONCH / VOC",
    "📐 BİO-NOT Modelleri",
    "💬 BİO-NOT Chat",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Bitki Döngüleri
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(f"Görev Günü {mission_day} — Bitki Büyüme Fazları")
    plant_keys = list(PLANTS.keys())
    cols = st.columns(len(plant_keys))

    for i, key in enumerate(plant_keys):
        if key in PLANTS:
            p = PLANTS[key]
            info = modular_phase(key, mission_day)
            fvfm = chlorophyll_fluorescence(stress_level, info["day_in_cycle"], p["cycle"])
            eth  = ethylene_status(key, info["progress"], stress_level)

            with cols[i]:
                st.markdown(f"**{p['name']}**")
                st.caption(f"*{p['latin']}*")
                st.progress(info["progress"], text=f"{info['progress_pct']}%")
                st.caption(f"Faz: **{info['phase']}**")
                st.caption(info["mod_notation"])
                st.metric("Fv/Fm", fvfm["fvfm"])
                st.metric("Etilen", f"{eth['ethylene_ppb']} ppb")
                if fvfm["status"] == "critical":
                    st.error(fvfm["message"])
                elif fvfm["status"] == "warning":
                    st.warning(fvfm["message"])

    st.divider()
    st.subheader("Hasat Takvimi (İlk 120 Gün)")
    harvest_data = []
    for key in [k for k in plant_keys if k != "spirulina"]:
        p = PLANTS[key]
        for d in range(1, 121):
            info = modular_phase(key, d)
            if info["day_in_cycle"] == p["cycle"]:
                harvest_data.append({"Gün": d, "Bitki": p["name"]})

    if harvest_data:
        df_h = pd.DataFrame(harvest_data)
        color_map = {PLANTS[k]["name"]: PLANTS[k]["color"] for k in plant_keys if k != "spirulina"}
        fig_h = px.scatter(df_h, x="Gün", y="Bitki", color="Bitki", title="Hasat Noktaları", color_discrete_map=color_map)
        fig_h.update_traces(marker_size=12)
        fig_h.update_layout(showlegend=False, height=280)
        st.plotly_chart(fig_h, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Gaz Dengesi
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Yansıma Simetrisi — Kütle Dengesi")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**CO₂ Emilim Dağılımı**")
        abs_data = {}
        abs_colors = []
        for k, v in sym["co2_absorption"].items():
            label = PLANTS[k]["name"] if k in PLANTS else "Spirulina"
            abs_data[label] = v
            abs_colors.append(PLANTS[k]["color"] if k in PLANTS else "#185FA5")

        fig_pie = go.Figure(go.Pie(labels=list(abs_data.keys()), values=list(abs_data.values()), hole=0.4, marker_colors=abs_colors))
        fig_pie.update_layout(height=320, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.markdown("**Denklem: y = n − x**")
        st.latex(r"CO_2^{input} = CO_2^{absorption} + \Delta O_2 + \Delta biomass")
        st.metric("CO₂ Girdi",          f"{sym['co2_input']} kg/gün")
        st.metric("Toplam CO₂ Emilim",  f"{sym['total_co2_abs']} kg/gün")
        st.metric("O₂ Net",             f"{sym['o2_net']:+.3f} kg/gün")
        st.metric("Biyokütle",          f"{sym['total_biomass']} kg/gün")
        st.metric("Asimetri (Δ)",       f"{sym['asymmetry']:+.3f} kg/gün")

    st.divider()
    st.subheader("30 Günlük Projeksiyon")
    fig_proj = go.Figure()
    fig_proj.add_trace(go.Scatter(x=proj["days"], y=proj["co2_prod"], name="CO₂ üretim", line=dict(color="#c62828", width=2)))
    fig_proj.add_trace(go.Scatter(x=proj["days"], y=proj["co2_abs"], name="CO₂ emilim", line=dict(color="#2e7d32", width=2)))
    fig_proj.add_trace(go.Scatter(x=proj["days"], y=proj["o2_net"], name="Net O₂", line=dict(color="#1565c0", width=1.5, dash="dot")))
    fig_proj.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig_proj.update_layout(xaxis_title="Görev Günü", yaxis_title="kg/gün", height=360, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_proj, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — PONCH / VOC
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("PONCH — Biyokimyasal Algılama Sistemi")
    icon_map = {"critical": "🔴", "warning": "🟡", "normal": "🟢"}
    d_icon   = icon_map.get(diag["level"], "⚪")
    
    bilge_html = f'<div class="bilge-box">{d_icon} <strong>Bilge-Bot:</strong> "{diag["bilge_message"]}"<br><small>{diag["detail"]}</small></div>'
    st.markdown(bilge_html, unsafe_allow_html=True)

    col_v, col_f = st.columns([3, 2])
    with col_v:
        st.markdown("**VOC Kimyasal İmza Analizi**")
        voc_list = []
        for v in diag["voc_results"]:
            voc_list.append({"VOC": v["name"], "Seviye (ppb)": v["ppb"], "Yüzde (%)": v["pct"], "Not": v["note"], "Durum": icon_map.get(v["status"], "⚪")})
        st.dataframe(pd.DataFrame(voc_list), hide_index=True, use_container_width=True)

        fig_voc = go.Figure(go.Bar(x=[v["ppb"] for v in diag["voc_results"]], y=[v["name"] for v in diag["voc_results"]], orientation="h", marker_color=[v["color"] for v in diag["voc_results"]]))
        fig_voc.update_layout(xaxis_title="ppb", height=260, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_voc, use_container_width=True)

    with col_f:
        st.markdown("**Klorofil Floresansı (Fv/Fm)**")
        for key in list(PLANTS.keys())[:4]:
            p = PLANTS[key]
            info = modular_phase(key, mission_day)
            fvfm = chlorophyll_fluorescence(stress_level, info["day_in_cycle"], p["cycle"])
            icon = icon_map.get(fvfm["status"], "⚪")
            st.metric(label=f"{icon} {p['name']}", value=fvfm["fvfm"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — BİO-NOT Modelleri
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("BİO-NOT Matematiksel Modülleri")
    col_m, col_t = st.columns(2)

    with col_m:
        st.markdown("**Modüler Aritmetik ℤₙ**")
        mod_rows = []
        for key in PLANTS:
            info = modular_phase(key, mission_day)
            mod_rows.append({
                "Bitki":     PLANTS[key]["name"],
                "n (döngü)": info["cycle_length"],
                "x (gün)":   info["day_in_cycle"],
                "Faz":       info["phase"],
                "İlerleme":  f"{info['progress_pct']}%",
                "Notasyon":  info["mod_notation"],
            })
        st.dataframe(pd.DataFrame(mod_rows), hide_index=True, use_container_width=True)

    with col_t:
        st.markdown("**Öznel Zaman τ = ΔX / Δt**")
        st.latex(r"\tau = \frac{\Delta X}{\Delta t}")
        t_icon = {"critical": "🔴", "warning": "🟡", "normal": "🟢"}.get(tau["status"], "⚪")
        st.metric(f"{t_icon} τ değeri", tau["tau"])
        st.caption(tau["message"])

        st.divider()
        st.markdown("**Yansıma Simetrisi Özet**")
        df_sym = pd.DataFrame([
            {"Parametre": "CO₂ girdi (x)",    "Değer": f"{sym['co2_input']} kg/gün"},
            {"Parametre": "CO₂ emilim",        "Değer": f"{sym['total_co2_abs']} kg/gün"},
            {"Parametre": "Asimetri (Δ)",      "Değer": f"{sym['asymmetry']:+.3f} kg/gün"},
            {"Parametre": "Verimlilik k",       "Değer": str(sym["efficiency_k"])},
            {"Parametre": "Durum",              "Değer": sym["status"].upper()},
        ])
        st.dataframe(df_sym, hide_index=True, use_container_width=True)

        st.divider()
        st.markdown("**Stokiyometrik Element Döngüsü**")
        df_elem = pd.DataFrame([
            {"Element": "C (Karbon)",   "Günlük döngü (kg)": round(sym["total_co2_abs"] * 0.27, 2)},
            {"Element": "H (Hidrojen)", "Günlük döngü (kg)": round(sym["total_o2"] * 0.11, 2)},
            {"Element": "N (Azot)",     "Günlük döngü (kg)": round(area_bz * 0.15, 2)},
            {"Element": "O (Oksijen)",  "Günlük döngü (kg)": round(sym["total_o2"], 2)},
            {"Element": "P (Fosfor)",   "Günlük döngü (kg)": round((area_tp + area_cd) * 0.02, 3)},
        ])
        st.dataframe(df_elem, hide_index=True, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — BİO-NOT CHAT (SİHİRLİ RADARLI GEMINI AI)
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("💬 BİO-NOT Akıllı Asistanı")
    st.caption("Uzay habitatı sensörlerine ve BLSS veri bankasına bağlı otonom zeka.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Merhaba Mürettebat! Ben sisteme entegre BİO-NOT Asistanıyım. Ekosistem dinamiklerine ve anlık gaz değişimlerine hakimim. Bana sistem durumu veya spesifik bitkiler hakkında sorular sorabilirsiniz."}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Mürettebat komutunu girin..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            
            # --- SİHİRLİ RADAR ---
            # O an Google sunucularında çalışan en stabil modeli otomatik bulur
            aktif_model = "gemini-1.5-flash" 
            try:
                modeller = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                if modeller:
                    if "models/gemini-1.5-flash" in modeller:
                        aktif_model = "models/gemini-1.5-flash"
                    elif "models/gemini-pro" in modeller:
                        aktif_model = "models/gemini-pro"
                    else:
                        aktif_model = modeller[0] 
            except Exception:
                pass # Radar çalışmazsa varsayılan ile devam et
                
            model = genai.GenerativeModel(aktif_model)
            # ---------------------

            sistem_durumu = f"""
            Sen uzay kolonizasyonu için tasarlanmış BİO-NOT adında akıllı bir Yaşam Destek Sistemi (BLSS) yapay zekasısın. 
            Aşağıdaki BİLGİ BANKASI'na ve CANLI SENSÖR VERİLERİNE dayanarak astronotların (mürettebatın) sorularını yanıtla.

            --- BİLGİ BANKASI ---
            {BLSS_BILGI_BANKASI}
            ---------------------

            --- CANLI SİSTEM VERİLERİ ---
            Astronot Sayısı: {crew} kişi
            Görev Günü: {mission_day}
            CO2 Asimetrisi (Yansıma Simetrisi): {sym['asymmetry']} kg/gün
            Net O2 Üretimi: {sym['o2_net']} kg/gün
            Abiyotik Stres Seviyesi: %{stress_level}
            Patojen Riski: %{pathogen_risk}
            PONCH Teşhisi: {diag['bilge_message']} ({diag['detail']})
            Öznel Zaman (Tau) Değeri: {tau['tau']}
            -------------------------------------

            Mürettebatın Sorusu: "{prompt}"
            
            Görevlerin:
            1. BİO-NOT yapay zekası kimliğinde kal, konuşan kişiye her zaman "Mürettebat" diye hitap et.
            2. Soruyu doğrudan bilgi bankasındaki verilere ve anlık sensör değerlerine göre yanıtla. 
            3. Net, profesyonel ve hedefe yönelik konuş. Bilim-kurgu filmlerindeki gelişmiş gemi asistanları gibi bir ton kullan.
            """

            response = model.generate_content(sistem_durumu)
            cevap = response.text

            with st.chat_message("assistant"):
                st.markdown(cevap)
            st.session_state.messages.append({"role": "assistant", "content": cevap})

        except Exception as e:
            hata = f"Bağlantı kesildi. Kritik iletişim hatası: Lütfen API anahtarınızın geçerli olduğundan ve internet bağlantınızdan emin olun. Detay: {e}"
            with st.chat_message("assistant"):
                st.error(hata)

st.divider()
st.caption("BLSS Simülasyon Paneli · Eureka Takımı · BİO-NOT & PONCH Altyapısı")