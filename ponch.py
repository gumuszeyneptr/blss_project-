from plants import VOC_PROFILES, PLANTS


def voc_analysis(stress_level, pathogen_risk):
    results = []
    for voc_name, profile in VOC_PROFILES.items():
        raw = stress_level * profile["stress_w"] + pathogen_risk * profile["path_w"]
        ppb = round(min(raw, 95.0), 1)
        pct = round(ppb / 95 * 100, 1)

        if pct > 70:
            status = "critical"
        elif pct > 40:
            status = "warning"
        else:
            status = "normal"

        results.append({
            "name":   voc_name,
            "ppb":    ppb,
            "pct":    pct,
            "color":  profile["color"],
            "note":   profile["note"],
            "status": status,
        })
    return results


def chlorophyll_fluorescence(stress_level, day_in_cycle, cycle):
    base        = 0.88
    stress_drop = (stress_level / 100) * 0.12
    age_factor  = (day_in_cycle / max(cycle, 1)) * 0.04
    fvfm        = round(base - stress_drop - age_factor, 3)
    fvfm        = max(0.50, min(0.92, fvfm))

    if fvfm < 0.75:
        status  = "critical"
        message = f"Fv/Fm = {fvfm} — Foto-inhibisyon riski! Isik spektrumu otomatik ayarlaniyor."
    elif fvfm < 0.83:
        status  = "warning"
        message = f"Fv/Fm = {fvfm} — Akut stres esigi altinda. Mudahale onerilir."
    else:
        status  = "normal"
        message = f"Fv/Fm = {fvfm} — Normal fotosentetik verimlilik."

    return {"fvfm": fvfm, "status": status, "message": message}


def ethylene_status(plant_key, progress, stress_level):
    peak = PLANTS[plant_key]["eth_peak"]
    eth  = round(peak * progress * (0.5 + stress_level / 200), 1)

    if eth > peak * 0.75:
        status  = "critical"
        message = f"Etilen = {eth} ppb — Hasat gecikmesi veya toksik birikim riski."
    elif eth > peak * 0.45:
        status  = "warning"
        message = f"Etilen = {eth} ppb — Olgunlasma fazi. Hasat zamanlamasini kontrol et."
    else:
        status  = "normal"
        message = f"Etilen = {eth} ppb — Normal seviye."

    return {"ethylene_ppb": eth, "status": status, "message": message}


def ponch_diagnosis(stress_level, pathogen_risk):
    voc           = voc_analysis(stress_level, pathogen_risk)
    critical_vocs = [v for v in voc if v["status"] == "critical"]
    warning_vocs  = [v for v in voc if v["status"] == "warning"]

    if pathogen_risk > 55:
        level  = "critical"
        bilge  = "Bitkiler SOS veriyor."
        detail = "Patojen biyobelirtecleri tespit edildi. Karantina protokolu baslatilmali."
    elif stress_level > 65:
        level  = "warning"
        bilge  = "Zaman yavasliyor."
        detail = "Yuksek abiyotik stres. Terpenoid piki izleniyor. Sicaklik ve besin kontrolu onerilir."
    elif len(critical_vocs) > 0:
        level  = "warning"
        bilge  = "Kimyasal imza anormal."
        detail = f"{', '.join(v['name'] for v in critical_vocs)} kritik seviyede."
    else:
        level  = "normal"
        bilge  = "Sistem dengede."
        detail = "Tum VOC seviyeleri guvenli aralikta."

    return {
        "level":          level,
        "bilge_message":  bilge,
        "detail":         detail,
        "voc_results":    voc,
        "critical_count": len(critical_vocs),
        "warning_count":  len(warning_vocs),
    }