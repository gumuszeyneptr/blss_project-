from plants import PLANTS, CO2_PER_PERSON, O2_PER_PERSON, SPIRULINA_O2_FACTOR

def co2_efficiency(co2_ppm):
    if co2_ppm <= 750:
        return 1.0
    elif co2_ppm <= 1000:
        return 1.0 - (co2_ppm - 750) / 250 * 0.08
    else:
        return 0.92 - (co2_ppm - 1000) / 200 * 0.14


def modular_phase(plant_key, mission_day):
    plant = PLANTS[plant_key]
    n = plant["cycle"]
    x = ((mission_day - 1) % n) + 1
    progress = x / n

    cumulative = 0
    current_phase = plant["phases"][-1]["label"]
    for phase in plant["phases"]:
        cumulative += phase["days"]
        if x <= cumulative:
            current_phase = phase["label"]
            break

    return {
        "day_in_cycle":  x,
        "cycle_length":  n,
        "progress":      round(progress, 3),
        "progress_pct":  round(progress * 100, 1),
        "phase":         current_phase,
        "mod_notation":  f"x = {x} (mod {n})",
    }


def reflection_symmetry(crew, areas, spirulina_volume, co2_ppm):
    k = co2_efficiency(co2_ppm)

    co2_input = round(crew * CO2_PER_PERSON, 3)
    o2_need   = round(crew * O2_PER_PERSON, 3)

    co2_absorption = {}
    o2_production  = {}
    biomass        = {}

    for key, area in areas.items():
        p = PLANTS[key]
        co2_absorption[key] = round(area * p["ncer"] * k / 1000, 3)
        o2_production[key]  = round(area * p["o2_factor"] * k, 3)
        biomass[key]        = round(area * p["biomass_factor"] * k, 3)

    sp_o2  = round(spirulina_volume * SPIRULINA_O2_FACTOR / 100 * k, 3)
    sp_co2 = round(spirulina_volume * 0.18 * k / 1000, 3)
    co2_absorption["spirulina"] = sp_co2
    o2_production["spirulina"]  = sp_o2

    total_co2_abs = round(sum(co2_absorption.values()), 3)
    total_o2      = round(sum(o2_production.values()), 3)
    total_biomass = round(sum(biomass.values()), 3)

    asymmetry = round(co2_input - total_co2_abs, 3)
    o2_net    = round(total_o2 - o2_need, 3)

    if abs(asymmetry) < 0.3:
        status  = "balanced"
        message = "Yansima simetrisi saglandi. Sistem stabil."
    elif asymmetry > 1.5:
        status  = "critical"
        message = "KRITIK: Aynada sapma var! CO2 birikimi tehlikeli. Acil mudahale gerekli."
    elif asymmetry > 0:
        status  = "warning"
        message = f"Hafif asimetri ({asymmetry:+.2f} kg/gun). Spirulina veya bitki alani artirilmali."
    else:
        status  = "surplus"
        message = f"Fazla O2 uretimi ({asymmetry:.2f} kg/gun). Kaynak optimizasyonu yapilabilir."

    return {
        "co2_input":      co2_input,
        "o2_need":        o2_need,
        "co2_absorption": co2_absorption,
        "total_co2_abs":  total_co2_abs,
        "o2_production":  o2_production,
        "total_o2":       total_o2,
        "total_biomass":  total_biomass,
        "asymmetry":      asymmetry,
        "o2_net":         o2_net,
        "efficiency_k":   round(k, 3),
        "status":         status,
        "message":        message,
    }


def subjective_time(delta_x, delta_t):
    if delta_t == 0:
        return {"tau": 0.0, "status": "critical", "message": "Delta_t = 0: Hesaplanamıyor."}

    tau = round(delta_x / delta_t, 3)

    if tau < 0.5:
        status  = "critical"
        message = "Tau sifira yakin — Zaman durdu! Acil mudahale: besin takviyesi veya isik spektrumu degisimi."
    elif tau < 1.5:
        status  = "warning"
        message = "Dusuk metabolik hiz. Besin veya isik ayari onerilir."
    else:
        status  = "normal"
        message = "Metabolik hiz normal. Buyume devam ediyor."

    return {"tau": tau, "status": status, "message": message}


def projection_30days(crew, areas, spirulina_volume, co2_ppm):
    days = list(range(1, 31))
    co2_prod, co2_abs, o2_net = [], [], []

    for d in days:
        ramp = min(1.0, 0.70 + (d / 30) * 0.35)
        k    = co2_efficiency(co2_ppm)

        prod = round(crew * CO2_PER_PERSON * (1 + d * 0.001), 3)
        co2_prod.append(prod)

        ab = sum(
            areas.get(key, 0) * PLANTS[key]["ncer"] * k * ramp / 1000
            for key in areas
        ) + spirulina_volume * 0.18 * k / 1000
        co2_abs.append(round(ab, 3))

        o2 = sum(
            areas.get(key, 0) * PLANTS[key]["o2_factor"] * k * ramp
            for key in areas
        ) + spirulina_volume * SPIRULINA_O2_FACTOR / 100 * k
        net = round(o2 - crew * O2_PER_PERSON, 3)
        o2_net.append(net)

    return {"days": days, "co2_prod": co2_prod, "co2_abs": co2_abs, "o2_net": o2_net}