import os
import math
import json
import numpy as np
import requests as req_lib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, date
import base64
from flask import Flask, render_template, request, jsonify, Response
from simulation import (run_simulation_core, h_convection_forcee_sphere_W_m2K,
                        mdot_evap_max_kg_s, H_FG, rk4_step, appliquer_cas_extreme)

app = Flask(__name__)

APP_PASSWORD = os.environ.get("APP_PASSWORD")

@app.before_request
def require_auth():
    if not APP_PASSWORD:
        return  # pas de mot de passe configuré → accès libre
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Basic "):
        try:
            decoded = base64.b64decode(auth[6:]).decode("utf-8")
            _, pwd = decoded.split(":", 1)
            if pwd == APP_PASSWORD:
                return  # mot de passe correct
        except Exception:
            pass
    return Response(
        "Accès protégé — SiteSphere Transport",
        401,
        {"WWW-Authenticate": 'Basic realm="SiteSphere Transport"'},
    )

# Session HTTP partagée avec connection pooling pour Open-Meteo
_http = req_lib.Session()
_http.mount("https://", req_lib.adapters.HTTPAdapter(
    pool_connections=4, pool_maxsize=20,
    max_retries=req_lib.adapters.Retry(total=1, backoff_factor=0.3)
))

# ── Races bovines — paramètres métaboliques (sources : CIGR 2002, ASHRAE 2011) ──
BREEDS = {
    "holstein":  {"fr": "Holstein-Friesian",  "en": "Holstein-Friesian",
                  "qv": 950, "rho": 800, "note_fr": "Race laitière haute production — métabolisme élevé"},
    "normande":  {"fr": "Normande",            "en": "Normande",
                  "qv": 880, "rho": 795, "note_fr": "Race mixte — métabolisme modéré à élevé"},
    "simmental": {"fr": "Simmental",           "en": "Simmental",
                  "qv": 860, "rho": 790, "note_fr": "Race mixte — métabolisme modéré"},
    "charolais": {"fr": "Charolais",           "en": "Charolais",
                  "qv": 810, "rho": 780, "note_fr": "Race à viande française — métabolisme modéré"},
    "angus":     {"fr": "Angus",               "en": "Angus",
                  "qv": 830, "rho": 800, "note_fr": "Race à viande — bonne résistance thermique"},
    "limousin":  {"fr": "Limousin",            "en": "Limousin",
                  "qv": 770, "rho": 775, "note_fr": "Race rustique à viande — métabolisme modéré-bas"},
    "blonde":    {"fr": "Blonde d'Aquitaine",  "en": "Blonde d'Aquitaine",
                  "qv": 790, "rho": 775, "note_fr": "Race à viande du Sud-Ouest — métabolisme modéré"},
    "salers":    {"fr": "Salers",              "en": "Salers",
                  "qv": 740, "rho": 760, "note_fr": "Race rustique de montagne — métabolisme bas"},
    "autre":     {"fr": "Autre / Indéfini",    "en": "Other / Undefined",
                  "qv": 800, "rho": 800, "note_fr": "Valeurs moyennes génériques"},
}


# ── Route interpolation helpers ───────────────────────────────────────────────

def _haversine_m(lon1, lat1, lon2, lat2):
    R = 6_371_000
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _cumul_distances(coords):
    """Precompute cumulative distances (m) along a coordinate list."""
    cumul = [0.0]
    for i in range(1, len(coords)):
        cumul.append(cumul[-1] + _haversine_m(*coords[i - 1], *coords[i]))
    return cumul


def position_at_fraction(coords, fraction, cumul=None):
    """Return [lon, lat] at given fraction (0–1) along route polyline."""
    fraction = max(0.0, min(1.0, fraction))
    if cumul is None:
        cumul = _cumul_distances(coords)
    total = cumul[-1]
    if total == 0:
        return coords[0]
    target = fraction * total
    for i in range(1, len(cumul)):
        if cumul[i] >= target:
            seg = cumul[i] - cumul[i - 1]
            t = (target - cumul[i - 1]) / seg if seg > 0 else 0
            lon = coords[i - 1][0] + t * (coords[i][0] - coords[i - 1][0])
            lat = coords[i - 1][1] + t * (coords[i][1] - coords[i - 1][1])
            return [lon, lat]
    return coords[-1]


def avg_truck_speed_over_window(coords, route_speeds_kmh, t_h, window_h, duration_h, cumul):
    """
    Distance-weighted average truck speed over the time window [t_h, t_h+window_h].
    Captures toll plazas, interchanges, urban sections that occur within the window
    even if they are brief — unlike single-point sampling which misses them.
    """
    if not route_speeds_kmh or not cumul:
        return 80.0
    total = cumul[-1]
    if total == 0 or duration_h == 0:
        return 80.0

    d1 = max(0.0, (t_h / duration_h) * total)
    d2 = min(total, ((t_h + window_h) / duration_h) * total)

    weighted = 0.0
    dist_sum = 0.0
    for i in range(1, len(cumul)):
        ov_s = max(cumul[i - 1], d1)
        ov_e = min(cumul[i], d2)
        if ov_e > ov_s:
            ov_len = ov_e - ov_s
            spd = route_speeds_kmh[min(i - 1, len(route_speeds_kmh) - 1)]
            weighted  += spd * ov_len
            dist_sum  += ov_len

    return weighted / dist_sum if dist_sum > 0 else 80.0


# ── Open-Meteo weather fetching ───────────────────────────────────────────────

def fetch_openmeteo_day(lat, lon, date_str):
    """
    Fetch the FULL day of minutely_15 data for a grid cell.
    Returns raw series dict (96 slots). One call covers all time slots for that day.
    Falls back to hourly ERA5 for dates >92 days in the past.
    """
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    today       = date.today()

    if target_date < today - timedelta(days=92):
        base_url = "https://archive-api.open-meteo.com/v1/era5"
        params   = {
            "latitude": round(lat, 2), "longitude": round(lon, 2),
            "hourly": "temperature_2m,relativehumidity_2m,windspeed_10m",
            "start_date": date_str, "end_date": date_str,
            "timezone": "Europe/Paris", "wind_speed_unit": "kmh",
        }
        r = _http.get(base_url, params=params, timeout=10)
        r.raise_for_status()
        return {"series": r.json().get("hourly", {}), "mode": "hourly"}
    else:
        base_url = "https://api.open-meteo.com/v1/forecast"
        params   = {
            "latitude": round(lat, 2), "longitude": round(lon, 2),
            "minutely_15": "temperature_2m,relativehumidity_2m,windspeed_10m",
            "start_date": date_str, "end_date": date_str,
            "timezone": "Europe/Paris", "wind_speed_unit": "kmh",
        }
        r = _http.get(base_url, params=params, timeout=10)
        r.raise_for_status()
        return {"series": r.json().get("minutely_15", {}), "mode": "minutely_15"}


def extract_weather(day_data, target_dt):
    """Extract T, RH, wind at target_dt from a pre-fetched day response."""
    series = day_data["series"]
    if day_data["mode"] == "minutely_15":
        idx = target_dt.hour * 4 + target_dt.minute // 15
    else:
        idx = target_dt.hour
    n = len(series.get("temperature_2m", [0]))
    idx = min(idx, n - 1)
    return {
        "temp_C":  series["temperature_2m"][idx],
        "rh_frac": series["relativehumidity_2m"][idx] / 100.0,
        "wind_kmh": series["windspeed_10m"][idx],
    }


def _fallback_weather(hour_local):
    """Sinusoidal fallback if Open-Meteo is unavailable."""
    T = 20 + 6 * math.sin(2 * math.pi * (hour_local - 14) / 24)
    return {"temp_C": T, "rh_frac": 0.60, "wind_kmh": 6.0}


WEATHER_STEP_MIN = 15  # résolution météo : toutes les 15 minutes


def build_hourly_weather(route_coords, route_speeds_kmh, departure_dt, duration_h, stops=None):
    """
    Compute weather every WEATHER_STEP_MIN minutes along the route.
    Positions are computed synchronously; Open-Meteo fetches run in parallel.
    stops: [{t_arrive_h, duration_h, t_depart_h, lat, lon}]
    """
    if stops is None:
        stops = []

    total_stops_h   = sum(s["duration_h"] for s in stops)
    total_driving_h = max(duration_h - total_stops_h, 1e-6)
    step_h          = WEATHER_STEP_MIN / 60.0
    cumul = _cumul_distances(route_coords) if (route_coords and len(route_coords) >= 2) else None

    # ── Étape 1 : calculer toutes les positions et vitesses (synchrone, rapide) ──
    points = []  # {lat, lon, truck_v, is_stopped, t_h, dt_i}
    t_h = 0.0
    while t_h <= duration_h + 1e-9:
        dt_i = departure_dt + timedelta(hours=t_h)
        stop_active = next((s for s in stops if s["t_arrive_h"] <= t_h < s["t_depart_h"]), None)

        if stop_active:
            lat, lon  = stop_active["lat"], stop_active["lon"]
            truck_v, is_stopped = 0.0, True
        else:
            driv_elapsed = t_h - sum(s["duration_h"] for s in stops if s["t_depart_h"] <= t_h)
            driv_elapsed = max(0.0, driv_elapsed)
            fraction     = min(driv_elapsed / total_driving_h, 1.0)
            if cumul:
                pos      = position_at_fraction(route_coords, fraction, cumul)
                lon, lat = pos[0], pos[1]
                truck_v  = avg_truck_speed_over_window(
                    route_coords, route_speeds_kmh, driv_elapsed, step_h, total_driving_h, cumul)
            else:
                lat, lon, truck_v = 46.5, 2.3, 80.0
            is_stopped = False

        points.append({"lat": lat, "lon": lon, "truck_v": truck_v,
                       "is_stopped": is_stopped, "t_h": t_h, "dt_i": dt_i})
        t_h = round(t_h + step_h, 6)

    # ── Étape 2 : fetch météo à résolution horaire seulement ──────────────────
    # La météo varie à l'heure, pas à la minute.
    # → 1 appel par heure entière (≤ ceil(duration_h)+1 appels), puis interpolation.
    hour_points = {}  # t_h_entier -> point de référence
    for p in points:
        h_int = math.floor(p["t_h"])
        if h_int not in hour_points:
            hour_points[h_int] = p

    def _fetch_hour(h, rep):
        try:
            day_data = fetch_openmeteo_day(rep["lat"], rep["lon"],
                                           rep["dt_i"].strftime("%Y-%m-%d"))
            return h, extract_weather(day_data, rep["dt_i"])
        except Exception:
            return h, _fallback_weather(rep["dt_i"].hour)

    hour_weather = {}
    with ThreadPoolExecutor(max_workers=min(16, len(hour_points))) as executor:
        futures = {executor.submit(_fetch_hour, h, rep): h for h, rep in hour_points.items()}
        for future in as_completed(futures):
            h, w = future.result()
            hour_weather[h] = w

    def _interpolate_weather(t_h):
        """Interpolation linéaire de la météo entre les heures entières."""
        h0 = math.floor(t_h)
        h1 = h0 + 1
        frac = t_h - h0
        w0 = hour_weather.get(h0) or hour_weather.get(min(hour_weather), _fallback_weather(h0))
        w1 = hour_weather.get(h1) or w0
        if frac == 0 or w0 is w1:
            return w0
        return {
            "temp_C":  w0["temp_C"]  + frac * (w1["temp_C"]  - w0["temp_C"]),
            "rh_frac": w0["rh_frac"] + frac * (w1["rh_frac"] - w0["rh_frac"]),
            "wind_kmh":w0["wind_kmh"]+ frac * (w1["wind_kmh"]- w0["wind_kmh"]),
        }

    # ── Étape 3 : assembler les points 15 min avec météo interpolée ──────────
    results = []
    for p in points:
        w = _interpolate_weather(p["t_h"])
        results.append({**w,
                        "lat":             p["lat"],
                        "lon":             p["lon"],
                        "truck_speed_kmh": round(p["truck_v"], 1),
                        "is_stopped":      p["is_stopped"],
                        "t_h":             round(p["t_h"], 4),
                        "hour_label":      p["dt_i"].strftime("%H:%M")})
    return results


# ── Regime builders ───────────────────────────────────────────────────────────

def build_regimes_hourly(hourly_weather, duration_h, mode, rng):
    """
    One regime per 15-min weather point.
    For 'ouvert': wind = truck speed at that segment (from OSRM annotations).
    For 'ferme':  wind = 3–5 km/h internal convection.
    """
    regimes = []
    for w in hourly_weather:
        h = w["t_h"]
        if h >= duration_h:
            break  # don't add regimes beyond trip end
        truck_v    = w.get("truck_speed_kmh", 80.0)
        is_stopped = w.get("is_stopped", False)
        if mode == "ferme":
            vent = float(rng.uniform(3.0, 5.0))
        elif mode == "ouvert":
            # À l'arrêt : vent ambiant (camion immobile) ; en route : vitesse camion
            vent = max(w["wind_kmh"], 3.0) if is_stopped else max(truck_v, 5.0)
        else:  # urgence
            vent = max(w["wind_kmh"], 5.0) if is_stopped else max(truck_v, 10.0)

        reg = {
            "t_debut_h":          h,
            "type":               2 if mode != "urgence" else 3,
            "Tinf_C":             w["temp_C"],
            "RH":                 w["rh_frac"],
            "vent_kmh":           vent,
            "hermetique":         False,
            "N":                  1,
            "mouillage_duree_min": 0 if mode != "urgence" else 60,
            "debit_eau_L_s":      0 if mode != "urgence" else 0.05,
        }
        regimes.append(reg)

    # Ensure at least one regime at t=0
    if not regimes:
        regimes.append({
            "t_debut_h": 0, "type": 2,
            "Tinf_C": hourly_weather[0]["temp_C"] if hourly_weather else 20,
            "RH": hourly_weather[0]["rh_frac"] if hourly_weather else 0.6,
            "vent_kmh": 4.0, "hermetique": False, "N": 1,
            "mouillage_duree_min": 0, "debit_eau_L_s": 0,
        })
    return regimes


def simulate_adaptive(hourly_weather, duration_h, masse_kg, qv, rho,
                      misting_min=1.0, misting_enabled=True, seed=42,
                      n_animals=1, available_water_L=None):
    """
    Step-by-step adaptive simulation with feedback control.

    Physics improvements vs. v1:
    - Pint is symmetric: cold side (T < T_set-Delta) increases metabolism (shivering)
    - Spray cooling applied only for actual misting sub-steps (not full 15-min step)
    - Residual water tracked on skin; continues evaporating in post-mist 'ouvert' steps
      → 15-min spray leaves ~0.57 kg on skin → ~60 min of continued evaporative cooling
      → 1-min spray: all water evaporates within the same step, no residual
    """
    rng = np.random.RandomState(seed)

    V_m3  = masse_kg / rho
    r     = (3.0 * V_m3 / (4.0 * np.pi)) ** (1.0 / 3.0)
    S     = 4.0 * np.pi * r ** 2
    C_JK  = masse_kg * 3500.0
    P0_W  = qv * V_m3
    Pmin  = P0_W * 0.60
    Pmax  = P0_W * 1.40
    T_SIG_THERMOREG = 38.5   # °C — inflexion sigmoïde thermoreg
    K_SIG_THERMOREG = 3.0    # 1/°C — raideur

    def Pint(T_C):
        P = Pmin + (Pmax - Pmin) / (1.0 + math.exp(K_SIG_THERMOREG * (T_C - T_SIG_THERMOREG)))
        return float(max(Pmin, min(Pmax, P)))

    T_DISCOMFORT      = 39.0   # °C  stress thermique → ouverture fenêtres
    T_RED_ZONE        = 39.5   # °C  zone critique
    T_CLOSE_WIN       = 38.5   # °C  refermer fenêtres
    T_EMERGENCY_CLOSE = 37.5   # °C  fermeture d'urgence (hypothermie)
    HIGH_SPEED        = 70.0   # km/h  autoroute
    T_EXT_HOT         = 36.0   # °C  au-dessus : convection insuffisante même avec vent
    WIND_MIST_KMH     = 50.0   # km/h  en dessous : brumisation plus efficace que fenêtres
    REGIME_COOLDOWN_H = 0.5    # h   min 30 min entre changements de régime
    MIST_PRE_MIN      = 10.0   # min  durée de stress avant action
    T_EXT_OPEN_MIN    = 22.0   # °C  en dessous (route rapide) : pas d'ouverture fenêtres
    STEP_MIN        = 15.0   # min  pas ODE
    N_SUB           = 90
    DT_S            = STEP_MIN * 60.0 / N_SUB   # 10 s
    STEP_S          = STEP_MIN * 60.0            # 900 s
    MIST_KG_S          = 0.05 / 60.0    # spray kg/s
    MDOT_TRANSP_M2_KGS = 1.5e-5         # kg/m²/s — débit max sudation (Bos taurus ~54 g/m²/h)
    T_TRANSP_MID       = 39.5           # °C — centre sigmoïde (zone rouge)
    K_TRANSP           = 8.0            # 1/°C — raideur

    mode          = "ferme"
    t_discomfort  = 0.0
    t_red         = 0.0
    misting_end_h = -1.0
    water_on_skin = 0.0   # kg of spray water remaining on animal (not yet evaporated)
    transp_factor = 0.0   # débit de sudation : 0 à T_set, 1 à T_RED_ZONE (linéaire)
    water_used_L      = 0.0   # total water consumed across all misting events (liters)
    water_shortfall_L = 0.0   # water that would have been needed but wasn't available

    regime_events  = [{"t_h": 0.0, "mode": "ferme", "reason": "Départ"}]
    misting_events = []
    t_arr     = []
    T_arr     = []
    transp_arr = []   # état transpiration à chaque pas (pour coloration frontale)
    T_cur = 38.5

    ws = sorted(hourly_weather, key=lambda x: x["t_h"])
    def nearest_w(t_h): return min(ws, key=lambda x: abs(x["t_h"] - t_h))

    # ── Pre-loop helpers (closures over simulation state; called inside the loop) ──

    def _calc_opt_spray_s():
        """Returns misting duration (s) to cool effectively with post-spray trend check.
        Reads T_cur, water_on_skin, truck_v, wind_amb, is_stopped, Tinf, RH, t from closure."""
        vent_b  = max(wind_amb, 5.0) if is_stopped else max(truck_v, 10.0)
        h_c_b   = h_convection_forcee_sphere_W_m2K(r, vent_b, Tinf, RH)
        mdot_b  = mdot_evap_max_kg_s(r, vent_b, Tinf, RH)
        sP      = min(MIST_KG_S, mdot_b) * H_FG
        net_b   = max(0.0, MIST_KG_S - mdot_b)

        def fb(pe):
            return lambda Tv: (Pint(Tv) - h_c_b * S * (Tv - Tinf) - pe) / C_JK

        def _sim_residual(T_s, w_s):
            T_r, w_r = T_s, w_s
            for _ in range(3):
                if w_r <= 0.0: break
                ec = mdot_b * STEP_S; ev = min(w_r, ec)
                pp = (ev / STEP_S) * H_FG; w_r = max(0.0, w_r - ev)
                for _s in range(N_SUB): T_r = rk4_step(T_r, DT_S, fb(pp))
            return T_r

        def _sim_spray_state(n_subs):
            """Simulate n_subs sub-steps of spray from T_cur; return (T_end, w_skin_end)."""
            T_t = float(T_cur); w_t = float(water_on_skin)
            for si in range(N_SUB):
                if si < n_subs:
                    w_t += net_b * DT_S
                    T_t  = rk4_step(T_t, DT_S, fb(sP))
                else:
                    pp = 0.0
                    if w_t > 0:
                        ev = min(w_t, mdot_b * DT_S); pp = (ev / DT_S) * H_FG
                        w_t = max(0.0, w_t - ev)
                    T_t = rk4_step(T_t, DT_S, fb(pp))
            return T_t, w_t

        T_POST_MIN = 38.0
        LOOK_STEPS = 4   # 4 × 15 min = 1 h de lookahead post-spray

        def _post_T_min(T0, w0, spray_end_t):
            """Simulate LOOK_STEPS sans spray; retourne le T minimum observé."""
            T_s, w_s, T_min = T0, w0, T0
            t_lk = spray_end_t
            for _ in range(LOOK_STEPS):
                wn     = nearest_w(t_lk)
                v_n    = wn.get("truck_speed_kmh", truck_v)
                stp    = wn.get("is_stopped", False)
                Te_n   = wn["temp_C"]; rh_n = wn["rh_frac"]
                wamb_n = wn.get("wind_kmh", 0.0)
                vb_n   = max(5.0, wamb_n if stp else max(v_n, 10.0))
                hc_n   = h_convection_forcee_sphere_W_m2K(r, vb_n, Te_n, rh_n)
                md_n   = mdot_evap_max_kg_s(r, vb_n, Te_n, rh_n)
                for _s in range(N_SUB):
                    pp = 0.0
                    if w_s > 0:
                        ev = min(w_s, md_n * DT_S); pp = (ev / DT_S) * H_FG
                        w_s = max(0.0, w_s - ev)
                    T_s = rk4_step(T_s, DT_S,
                        lambda Tv, hc=hc_n, Te=Te_n, p=pp: (Pint(Tv) - hc * S * (Tv - Te) - p) / C_JK)
                T_min = min(T_min, T_s)
                t_lk += STEP_MIN / 60.0
            return T_min

        # ── Phase 1 : minimum sub-steps within a single 15-min step ──
        opt_s = None; T_end = float(T_cur); w_end = float(water_on_skin)
        for n in range(1, N_SUB + 1):
            w_acc = water_on_skin + net_b * n * DT_S
            n_p   = N_SUB - n
            if n_p > 0 and w_acc > 0.0:
                ec = mdot_b * n_p * DT_S; ev = min(w_acc, ec)
                pp_v   = (ev / (n_p * DT_S)) * H_FG
                w_end_ = max(0.0, w_acc - ev)
            else:
                pp_v = 0.0; w_end_ = w_acc
            T_t = float(T_cur)
            for s in range(N_SUB):
                T_t = rk4_step(T_t, DT_S, fb(sP if s < n else pp_v))
            if _sim_residual(T_t, w_end_) <= T_DISCOMFORT:
                opt_s = n * DT_S; T_end = T_t; w_end = w_end_
                break

        # ── Phase 2 : additional full 15-min steps if phase 1 insufficient ──
        if opt_s is None:
            T_p, w_p = float(T_cur), float(water_on_skin)
            for extra in range(max(0, round(misting_min / STEP_MIN) - 1)):
                w_f = w_p + net_b * N_SUB * DT_S; T_f = T_p
                for _ in range(N_SUB):
                    T_f = rk4_step(T_f, DT_S, fb(sP))
                if _sim_residual(T_f, w_f) <= T_DISCOMFORT:
                    opt_s = (extra + 2) * STEP_MIN * 60.0; T_end = T_f; w_end = w_f
                    break
                T_p, w_p = T_f, w_f
            if opt_s is None:
                opt_s = misting_min * 60.0

        # ── Phase 3 : post-spray lookahead — réduire si tendance trop abrupte ──
        spray_end_t = t + opt_s / 3600.0
        T_min_post  = _post_T_min(T_end, w_end, spray_end_t)
        if T_min_post < T_POST_MIN:
            # Recherche binaire : durée maximale de spray où T_min_post reste ≥ T_POST_MIN
            # (spray plus court → T_end plus élevé → chute post-spray moins profonde)
            lo_s, hi_s = DT_S, opt_s
            for _ in range(6):
                mid_s = (lo_s + hi_s) / 2.0
                n_m   = max(1, min(N_SUB, round(mid_s / DT_S)))
                T_m, w_m = _sim_spray_state(n_m)
                t_m   = t + n_m * DT_S / 3600.0
                if _post_T_min(T_m, w_m, t_m) >= T_POST_MIN:
                    lo_s = mid_s   # cette durée est sûre, peut essayer plus long
                else:
                    hi_s = mid_s   # trop long, réduire
            opt_s = lo_s

        return opt_s

    def _do_trigger_misting(reason):
        nonlocal mode, misting_end_h, t_discomfort, t_red, water_used_L, water_shortfall_L
        opt_s        = _calc_opt_spray_s()
        water_needed = n_animals * MIST_KG_S * opt_s
        w_avail      = ((available_water_L - water_used_L)
                        if available_water_L is not None else float('inf'))
        if water_needed > w_avail:
            water_shortfall_L += water_needed - w_avail
            opt_s   = (w_avail / (n_animals * MIST_KG_S)) if n_animals * MIST_KG_S > 0 else 0.0
            water_L = w_avail
        else:
            water_L = water_needed
        water_used_L  += water_L
        mode           = "brumisation"
        misting_end_h  = t + opt_s / 3600.0
        t_discomfort   = 0.0
        t_red          = 0.0
        misting_events.append({
            "t_start_h": round(t, 4),
            "t_end_h":   round(misting_end_h, 4),
            "T_trigger": round(T_cur, 2),
            "water_L":   round(water_L, 3),
        })
        regime_events.append({"t_h": round(t, 4), "mode": "brumisation",
                               "reason": f"{reason} — {opt_s/60:.1f}min calculé"})

    last_change_h = -REGIME_COOLDOWN_H  # permet un premier changement dès le départ
    t = 0.0
    while t <= duration_h + 1e-9:
        w          = nearest_w(t)
        truck_v    = w.get("truck_speed_kmh", 80.0)
        is_stopped = w.get("is_stopped", False)
        Tinf       = w["temp_C"]
        RH         = w["rh_frac"]
        wind_amb   = w["wind_kmh"]
        is_highway      = truck_v > HIGH_SPEED and not is_stopped
        is_cold_highway = truck_v > 60.0       and not is_stopped  # seuil spécifique surcooldown

        # Zone timers (at start of step)
        if T_cur >= T_RED_ZONE:
            t_red += STEP_MIN; t_discomfort += STEP_MIN
        elif T_cur > T_DISCOMFORT:
            t_red = 0.0;       t_discomfort += STEP_MIN
        else:
            t_red = t_discomfort = 0.0

        is_misting    = misting_end_h > 0 and t < misting_end_h - 1e-9
        ahead         = [x for x in ws if t < x["t_h"] <= t + 0.5]
        highway_ahead = any(x.get("truck_speed_kmh", 80) > HIGH_SPEED for x in ahead)

        # ── Regime decision ──────────────────────────────────────────
        # Hierarchy: natural cooling (windows) first; misting = emergency only.
        # At highway speed (>70 km/h): skip windows to avoid wind stress → mist directly.
        # Misting is also the fallback on highway when no water remains (safety > comfort).
        time_left_h  = duration_h - t
        w_avail_now  = ((available_water_L - water_used_L)
                        if available_water_L is not None else float('inf'))
        can_mist     = misting_enabled and w_avail_now > 0

        vent_percu  = max(truck_v, wind_amb)
        low_wind    = vent_percu < WIND_MIST_KMH
        cooldown_ok = (t - last_change_h) >= REGIME_COOLDOWN_H

        # Risque physique de surcooldown : fenêtres ouvertes → T chuterait sous 38°C en 30 min
        _v_win   = max(wind_amb, 3.0) if is_stopped else max(truck_v, 5.0)
        _h_win   = h_convection_forcee_sphere_W_m2K(r, _v_win, Tinf, RH)
        _cool_w  = max(0.0, _h_win * S * (T_cur - Tinf) - Pint(T_cur))
        cold_risk = (T_cur - _cool_w * 900.0 / C_JK) < 38.0    # T_POST_MIN, horizon 15 min (1 pas ODE)
        must_close = (is_cold_highway and Tinf < T_EXT_OPEN_MIN) or cold_risk

        if not is_misting and time_left_h >= 10.0 / 60.0:

            # 0. Urgence froid : T trop basse → fermeture immédiate, sans cooldown
            if mode == "ouvert" and T_cur < T_EMERGENCY_CLOSE:
                mode = "ferme"; t_discomfort = 0.0; water_on_skin = 0.0
                last_change_h = t
                regime_events.append({"t_h": round(t, 4), "mode": "ferme",
                                       "reason": f"Urgence froid ({T_cur:.1f}°C) — fermeture immédiate"})

            # 1. Fin brumisation → ouvert (ou ferme si risque surcooldown)
            elif mode == "brumisation" and t >= misting_end_h - 1e-9:
                t_red = 0.0; t_discomfort = 0.0; last_change_h = t
                if must_close:
                    mode = "ferme"; water_on_skin = 0.0
                    regime_events.append({"t_h": round(t, 4), "mode": "ferme",
                                           "reason": f"Fin brumisation — T ext froide ({Tinf:.1f}°C), fenêtres fermées"})
                else:
                    mode = "ouvert"
                    regime_events.append({"t_h": round(t, 4), "mode": "ouvert",
                                           "reason": "Fin brumisation — refroidissement maintenu"})

            # 2a. Chaleur extrême : T_ext ≥ 36°C → convection inefficace même avec vent fort
            elif (mode == "ouvert" and T_cur >= T_RED_ZONE and Tinf >= T_EXT_HOT
                  and t_discomfort >= MIST_PRE_MIN and can_mist and cooldown_ok):
                _do_trigger_misting(
                    f"T ext élevée ({Tinf:.1f}°C) — convection insuffisante (T={T_cur:.1f}°C)")
                last_change_h = t

            # 2b. Vent faible : fenêtres ouvertes mais insuffisantes
            elif (mode == "ouvert" and t_discomfort >= MIST_PRE_MIN
                  and low_wind and can_mist and cooldown_ok):
                _do_trigger_misting(
                    f"Vent faible ({vent_percu:.0f} km/h) — fenêtres insuffisantes (T={T_cur:.1f}°C)")
                last_change_h = t

            # 3. Fermé + stress → ouvrir fenêtres (sauf risque surcooldown)
            elif mode == "ferme" and t_discomfort >= MIST_PRE_MIN and cooldown_ok:
                if must_close:
                    # Ouverture surrefroidirait → brumisation ciblée si critique, sinon attendre
                    if T_cur >= T_RED_ZONE and can_mist:
                        _do_trigger_misting(
                            f"T ext froide ({Tinf:.1f}°C) — brumisation ciblée (T={T_cur:.1f}°C)")
                        last_change_h = t
                else:
                    mode = "ouvert"; t_discomfort = 0.0
                    last_change_h = t
                    regime_events.append({"t_h": round(t, 4), "mode": "ouvert",
                                           "reason": (f"Stress {MIST_PRE_MIN:.0f}min → refroidissement naturel "
                                                       f"(T={T_cur:.1f}°C, vent {vent_percu:.0f} km/h)")})

            # 4. Pré-refroidissement avant autoroute (seulement si T_ext assez chaud)
            elif (mode == "ferme" and T_cur > T_CLOSE_WIN + 0.1
                  and not is_highway and highway_ahead and cooldown_ok
                  and not must_close):
                mode = "ouvert"
                last_change_h = t
                regime_events.append({"t_h": round(t, 4), "mode": "ouvert",
                                       "reason": f"Pré-refroidissement avant autoroute (T={T_cur:.1f}°C)"})

            # 5a. Fermeture préventive : risque de surcooldown (physique ou autoroute froide)
            elif mode == "ouvert" and must_close and cooldown_ok:
                mode = "ferme"; t_discomfort = 0.0; water_on_skin = 0.0
                last_change_h = t
                regime_events.append({"t_h": round(t, 4), "mode": "ferme",
                                       "reason": f"Fermeture préventive surcooldown (T ext {Tinf:.1f}°C, vent {vent_percu:.0f} km/h)"})

            # 5. T objectif atteint → fermer fenêtres (sans cooldown : fermeture = action protectrice)
            elif mode == "ouvert" and T_cur <= T_CLOSE_WIN:
                mode = "ferme"; t_discomfort = 0.0; water_on_skin = 0.0
                last_change_h = t
                regime_events.append({"t_h": round(t, 4), "mode": "ferme",
                                       "reason": f"T objectif atteint ({T_cur:.1f}°C) — fermeture"})

        # Re-evaluate after decisions
        is_misting = misting_end_h > 0 and t < misting_end_h - 1e-9
        active     = "brumisation" if is_misting else mode

        # ── Sudation sigmoïdale : ~0 à T_set, 50 % à T_TRANSP_MID (39.5°C) ──
        if active == "brumisation":
            transp_factor = 0.0
        else:
            transp_factor = 1.0 / (1.0 + math.exp(-K_TRANSP * (T_cur - T_TRANSP_MID)))

        # ── Airspeed and h_convection ─────────────────────────────────
        if active == "brumisation":
            vent = max(wind_amb, 5.0) if is_stopped else max(truck_v, 10.0)
        elif active == "ouvert":
            vent = max(wind_amb, 3.0) if is_stopped else max(truck_v, 5.0)
        else:
            vent = float(rng.uniform(3.0, 5.0))

        h_c     = h_convection_forcee_sphere_W_m2K(r, vent, Tinf, RH)
        mdot_mx = mdot_evap_max_kg_s(r, vent, Tinf, RH)

        # ── Spray sub-steps and residual water tracking ───────────────
        if active == "brumisation":
            # How many of the 90 sub-steps have spray active
            spray_s   = max(0.0, (misting_end_h - t) * 3600.0)
            n_spray   = min(N_SUB, max(0, math.ceil(spray_s / DT_S)))
            spray_P   = min(MIST_KG_S, mdot_mx) * H_FG   # W per sub-step during spray

            # Net water that doesn't evaporate immediately accumulates on skin
            net_acc_rate = max(0.0, MIST_KG_S - mdot_mx)  # kg/s net accumulation
            water_acc    = net_acc_rate * n_spray * DT_S   # kg added to skin this step

            # Post-spray sub-steps: evaporate water already on skin
            n_post = N_SUB - n_spray
            water_avail = water_on_skin + water_acc
            if n_post > 0 and water_avail > 0.0:
                evap_cap  = mdot_mx * n_post * DT_S
                evap_post = min(water_avail, evap_cap)
                post_P    = (evap_post / (n_post * DT_S)) * H_FG
                water_on_skin = max(0.0, water_avail - evap_post)
            else:
                post_P        = 0.0
                water_on_skin = water_avail

        elif active == "ouvert":
            spray_P = 0.0; n_spray = 0
            # Transpiration naturelle (sudation biologique)
            transpi_P = min(MDOT_TRANSP_M2_KGS * S * transp_factor, mdot_mx) * H_FG
            # Résidus d'eau sur la peau (post-brumisation)
            if water_on_skin > 0.0:
                evap_cap = mdot_mx * STEP_S
                evap     = min(water_on_skin, evap_cap)
                post_P   = (evap / STEP_S) * H_FG + transpi_P
                water_on_skin = max(0.0, water_on_skin - evap)
            else:
                post_P = transpi_P

        else:  # ferme — sudation sigmoïdale
            spray_P = n_spray = 0
            post_P = min(MDOT_TRANSP_M2_KGS * S * transp_factor, mdot_mx) * H_FG

        # ── RK4 integration ──────────────────────────────────────────
        T_new = float(T_cur)

        def make_f(pevap):
            return lambda Tv: (Pint(Tv) - h_c * S * (Tv - Tinf) - pevap) / C_JK

        if active == "brumisation":
            f_spray = make_f(spray_P)
            f_post  = make_f(post_P)
            for sub in range(N_SUB):
                T_new = rk4_step(T_new, DT_S, f_spray if sub < n_spray else f_post)
        else:
            f = make_f(post_P)
            for _ in range(N_SUB):
                T_new = rk4_step(T_new, DT_S, f)

        t_arr.append(round(t, 4))
        T_arr.append(round(T_cur, 3))
        transp_arr.append(transp_factor > 0.0)
        T_cur = T_new
        t     = round(t + STEP_MIN / 60.0, 6)

    water_remaining_L = ((available_water_L - water_used_L)
                         if available_water_L is not None else None)
    return {
        "series":              {"t_h": t_arr, "T_C": T_arr, "transpiring": transp_arr},
        "regime_events":       regime_events,
        "misting_events":      misting_events,
        "water_used_L":        round(water_used_L, 2),
        "water_remaining_L":   round(water_remaining_L, 2) if water_remaining_L is not None else None,
        "water_shortfall_L":   round(water_shortfall_L, 2),
        "available_water_L":   available_water_L,
    }


def replay_adaptive_schedule(regime_events, misting_events,
                              hourly_weather, duration_h,
                              masse_kg, qv, rho, transp_scale=1.0):
    """
    Replay a nominal adaptive schedule on a different animal model.
    No strategic decisions are made: mode at each step is read from the
    pre-computed regime_events / misting_events of the nominal run.
    """
    rng = np.random.RandomState(0)

    V_m3  = masse_kg / rho
    r     = (3.0 * V_m3 / (4.0 * np.pi)) ** (1.0 / 3.0)
    S     = 4.0 * np.pi * r ** 2
    C_JK  = masse_kg * 3500.0
    P0_W  = qv * V_m3
    Pmin  = P0_W * 0.60
    Pmax  = P0_W * 1.40
    T_SIG_THERMOREG = 38.5   # °C — inflexion sigmoïde thermoreg
    K_SIG_THERMOREG = 3.0    # 1/°C — raideur

    def Pint(T_C):
        P = Pmin + (Pmax - Pmin) / (1.0 + math.exp(K_SIG_THERMOREG * (T_C - T_SIG_THERMOREG)))
        return float(max(Pmin, min(Pmax, P)))

    STEP_MIN        = 15.0
    N_SUB           = 90
    DT_S            = STEP_MIN * 60.0 / N_SUB
    STEP_S          = STEP_MIN * 60.0
    MIST_KG_S          = 0.05 / 60.0
    MDOT_TRANSP_M2_KGS = 1.5e-5 * transp_scale   # kg/m²/s (10 % pour les cas extrêmes)
    T_TRANSP_MID       = 39.5
    K_TRANSP           = 8.0

    sorted_regimes  = sorted(regime_events,  key=lambda x: x["t_h"])
    sorted_mistings = sorted(misting_events, key=lambda x: x["t_start_h"])

    def _active_mode(t):
        for me in sorted_mistings:
            if me["t_start_h"] <= t < me["t_end_h"] - 1e-9:
                return "brumisation", me["t_end_h"]
        mode = "ferme"
        for re in sorted_regimes:
            if re["t_h"] <= t + 1e-9:
                mode = re["mode"]
        return mode, None

    ws = sorted(hourly_weather, key=lambda x: x["t_h"])
    def nearest_w(t_h): return min(ws, key=lambda x: abs(x["t_h"] - t_h))

    t_arr = []; T_arr = []; transp_arr = []
    T_cur = 38.5; water_on_skin = 0.0; transp_factor = 0.0

    t = 0.0
    while t <= duration_h + 1e-9:
        w          = nearest_w(t)
        truck_v    = w.get("truck_speed_kmh", 80.0)
        is_stopped = w.get("is_stopped", False)
        Tinf       = w["temp_C"]
        RH         = w["rh_frac"]
        wind_amb   = w["wind_kmh"]

        active, mist_end_h = _active_mode(t)

        # Sudation sigmoïdale (mirrors simulate_adaptive)
        if active == "brumisation":
            transp_factor = 0.0
        else:
            transp_factor = 1.0 / (1.0 + math.exp(-K_TRANSP * (T_cur - T_TRANSP_MID)))

        if active == "brumisation":
            vent = max(wind_amb, 5.0) if is_stopped else max(truck_v, 10.0)
        elif active == "ouvert":
            vent = max(wind_amb, 3.0) if is_stopped else max(truck_v, 5.0)
        else:
            vent = float(rng.uniform(3.0, 5.0))

        h_c     = h_convection_forcee_sphere_W_m2K(r, vent, Tinf, RH)
        mdot_mx = mdot_evap_max_kg_s(r, vent, Tinf, RH)

        if active == "brumisation":
            spray_s      = max(0.0, (mist_end_h - t) * 3600.0) if mist_end_h else STEP_S
            n_spray      = min(N_SUB, max(0, math.ceil(spray_s / DT_S)))
            spray_P      = min(MIST_KG_S, mdot_mx) * H_FG
            net_acc_rate = max(0.0, MIST_KG_S - mdot_mx)
            water_acc    = net_acc_rate * n_spray * DT_S
            n_post       = N_SUB - n_spray
            water_avail  = water_on_skin + water_acc
            if n_post > 0 and water_avail > 0.0:
                evap_cap      = mdot_mx * n_post * DT_S
                evap_post     = min(water_avail, evap_cap)
                post_P        = (evap_post / (n_post * DT_S)) * H_FG
                water_on_skin = max(0.0, water_avail - evap_post)
            else:
                post_P        = 0.0
                water_on_skin = water_avail
        elif active == "ouvert":
            spray_P = 0.0; n_spray = 0
            transpi_P = min(MDOT_TRANSP_M2_KGS * S * transp_factor, mdot_mx) * H_FG
            if water_on_skin > 0.0:
                evap_cap      = mdot_mx * STEP_S
                evap          = min(water_on_skin, evap_cap)
                post_P        = (evap / STEP_S) * H_FG + transpi_P
                water_on_skin = max(0.0, water_on_skin - evap)
            else:
                post_P = transpi_P
        else:
            spray_P = n_spray = 0
            post_P        = min(MDOT_TRANSP_M2_KGS * S * transp_factor, mdot_mx) * H_FG
            water_on_skin = 0.0

        T_new = float(T_cur)
        def make_f(pe): return lambda Tv: (Pint(Tv) - h_c * S * (Tv - Tinf) - pe) / C_JK

        if active == "brumisation":
            f_s = make_f(spray_P); f_p = make_f(post_P)
            for sub in range(N_SUB):
                T_new = rk4_step(T_new, DT_S, f_s if sub < n_spray else f_p)
        else:
            f = make_f(post_P)
            for _ in range(N_SUB):
                T_new = rk4_step(T_new, DT_S, f)

        t_arr.append(round(t, 4)); T_arr.append(round(T_cur, 3)); transp_arr.append(transp_factor > 0.0)
        T_cur = T_new
        t     = round(t + STEP_MIN / 60.0, 6)

    return {"t_h": t_arr, "T_C": T_arr, "transpiring": transp_arr}


def make_payload(masse_kg, qv, rho, duration_h, n_points, regimes):
    return {
        "masse_kg":                  masse_kg,
        "rho_sphere_kg_m3":          rho,
        "cp_sphere_J_kgK":           3500.0,
        "puissance_volumique_W_m3":  qv,
        "T0_C":                      38.5,
        "T_interval_min_C":          36.0,
        "T_interval_max_C":          39.5,
        "debit_apparition_eau_kg_s": 0.0002,
        "thermoreg_enabled":         True,
        "thermoreg_model":           "sigmoide",
        "T_sig_C":                   38.5,
        "k_sig_per_C":               3.0,
        "T_set_C":                   38.5,
        "Delta_C":                   0.2,
        "k_c_W_K":                   500,
        "k_h_W_K":                   500,
        "k_froid_emp_W_K":           50,
        "k_extrapole_emp_W_K":       500,
        "pct_pmin":                  60,
        "pct_pmax":                  140,
        "vent_ambiant_kmh":          0.1,
        "Rth_camion_K_W":            0.2,
        "V_camion_m3":               60,
        "V_poumon_m3":               0.01,
        "periode_resp_s":            3,
        "duree_totale_h":            duration_h,
        "n_points":                  n_points,
        "cas_extremes":              False,
        "conv_model":                "churchill",
        "regimes":                   regimes,
    }


def classify_risk(T_max):
    if T_max > 41.0:  return "danger"
    if T_max > 40.0:  return "warning"
    if T_max >= 39.5: return "caution"
    return "ok"


# ── Flask routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    today_str = date.today().strftime("%Y-%m-%d")
    return render_template("index.html", breeds=BREEDS, today=today_str)


@app.route("/api/breeds")
def api_breeds():
    return jsonify(BREEDS)


@app.route("/api/geocode")
def geocode():
    q = request.args.get("q", "")
    try:
        r = req_lib.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 5,
                    "countrycodes": "fr,be,ch,lu,de,es,it,pt,nl,at,pl,cz,sk,hu,ro,bg,hr,si,gr,dk,se,no,fi,ie,gb,ee,lv,lt,rs,ba,me,mk,al,cy,mt"},
            headers={"User-Agent": "SiteSphere-Transport/1.0 (cisco.bosma@gmail.com)"},
            timeout=5,
        )
        return jsonify(r.json())
    except Exception:
        return jsonify([]), 200


@app.route("/api/route", methods=["POST"])
def route():
    data = request.json or {}
    try:
        waypoints = data.get("waypoints")
        if waypoints and len(waypoints) >= 2:
            coords_str = ";".join(f"{p['lon']},{p['lat']}" for p in waypoints)
        else:
            lon1 = data["from"]["lon"]; lat1 = data["from"]["lat"]
            lon2 = data["to"]["lon"];   lat2 = data["to"]["lat"]
            coords_str = f"{lon1},{lat1};{lon2},{lat2}"

        url = (
            f"https://router.project-osrm.org/route/v1/driving/{coords_str}"
            f"?overview=full&geometries=geojson&annotations=speed"
        )
        r = req_lib.get(url, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    try:
        data = request.json or {}

        poids              = float(data.get("poids_kg", 350))
        duration_h         = float(data.get("duration_h", 4))
        hour_start         = int(data.get("hour_start", 8))
        seed               = int(data.get("seed", 42))
        race_key           = data.get("race", "autre")
        route_coords       = data.get("route_coords", None)
        route_speeds_kmh   = data.get("route_speeds_kmh", None)
        route_stops        = data.get("route_stops", []) or []
        avg_speed_kmh      = float(data.get("avg_speed_kmh", 80.0))
        departure_date     = data.get("departure_date", date.today().strftime("%Y-%m-%d"))
        adaptive_enabled      = bool(data.get("adaptive_enabled", False))
        misting_enabled       = bool(data.get("misting_enabled", True))
        misting_min           = float(data.get("misting_duration_min", 1.0))
        n_animals             = int(data.get("n_bovins", 1)) or 1
        available_water_L     = data.get("available_water_L")
        if available_water_L is not None:
            available_water_L = float(available_water_L)
        cas_extremes_enabled  = bool(data.get("cas_extremes_enabled", False))
        pct_chaud             = float(data.get("pct_chaud", 20.0) or 20.0)
        pct_froid             = float(data.get("pct_froid", 20.0) or 20.0)

        breed = BREEDS.get(race_key, BREEDS["autre"])
        qv  = float(breed["qv"])
        rho = float(breed["rho"])

        # Parse departure datetime (local Paris time)
        departure_dt = datetime.strptime(
            f"{departure_date} {hour_start:02d}:00", "%Y-%m-%d %H:%M"
        )

        # Build real weather + truck speed profile along the route
        hourly_weather = build_hourly_weather(
            route_coords, route_speeds_kmh, departure_dt, duration_h, route_stops
        )

        n_points = max(400, int(duration_h * 60))
        rng = np.random.RandomState(seed)

        # ── Étape 1 : fenêtres fermées ─────────────────────────────
        reg_ferme      = build_regimes_hourly(hourly_weather, duration_h, "ferme", rng)
        payload_ferme  = make_payload(poids, qv, rho, duration_h, n_points, reg_ferme)
        res_ferme      = run_simulation_core(payload_ferme)
        T_max_ferm     = max(res_ferme["series"]["T_C"])
        risk_ferme     = classify_risk(T_max_ferm)

        # Cas extrêmes — fenêtres fermées (chaud / froid)
        ferme_chaud = ferme_froid = None
        risk_ferme_chaud = risk_ferme_froid = None
        if cas_extremes_enabled:
            f_ch           = pct_chaud / 100.0
            f_fr           = pct_froid / 100.0
            # f_masse=1.0 : seul qv change — évite l'inversion due au couplage P0∝f² et thermoreg absolue
            payload_ch     = appliquer_cas_extreme(payload_ferme, 1.0, 1.0 + f_ch, 1.0 - f_ch, f_transp=0.1)
            payload_fr     = appliquer_cas_extreme(payload_ferme, 1.0, 1.0 - f_fr, 1.0 + f_fr, f_transp=1.0)
            ferme_chaud    = run_simulation_core(payload_ch).get("series")
            ferme_froid    = run_simulation_core(payload_fr).get("series")
            risk_ferme_chaud = classify_risk(max(ferme_chaud["T_C"])) if ferme_chaud else None
            risk_ferme_froid = classify_risk(max(ferme_froid["T_C"])) if ferme_froid else None

        # ── Étape 2 : si risque → fenêtres ouvertes (comparaison) ──
        res_ouvert  = None
        risk_ouvert = None
        T_max_ouv   = None
        if risk_ferme != "ok":
            rng2 = np.random.RandomState(seed + 1)
            reg_ouvert  = build_regimes_hourly(hourly_weather, duration_h, "ouvert", rng2)
            res_ouvert  = run_simulation_core(make_payload(poids, qv, rho, duration_h, n_points, reg_ouvert))
            T_max_ouv   = max(res_ouvert["series"]["T_C"])
            risk_ouvert = classify_risk(T_max_ouv)

        # ── Étape 3 : stratégie adaptative (si activée) ────────────
        res_adaptive = None
        adap_chaud = adap_froid = None
        risk_adap_chaud = risk_adap_froid = None
        adaptive_not_needed = False
        if adaptive_enabled:
            if risk_ferme == "ok":
                adaptive_not_needed = True  # fenêtres fermées suffisantes, pas d'intervention
            else:
                adap = simulate_adaptive(
                    hourly_weather, duration_h, poids, qv, rho,
                    misting_min=misting_min, misting_enabled=misting_enabled, seed=seed,
                    n_animals=n_animals, available_water_L=available_water_L,
                )
                T_max_adap    = max(adap["series"]["T_C"])
                risk_adaptive = classify_risk(T_max_adap)
                res_adaptive  = {
                    "series":             adap["series"],
                    "regime_events":      adap["regime_events"],
                    "misting_events":     adap["misting_events"],
                    "T_max":              round(T_max_adap, 2),
                    "risk":               risk_adaptive,
                    "water_used_L":       adap["water_used_L"],
                    "water_remaining_L":  adap["water_remaining_L"],
                    "water_shortfall_L":  adap["water_shortfall_L"],
                    "available_water_L":  adap["available_water_L"],
                }

                # Cas extrêmes adaptatifs : rejouer le planning nominal sur le modèle perturbé
                if cas_extremes_enabled:
                    f_ch  = pct_chaud / 100.0
                    f_fr  = pct_froid / 100.0
                    adap_chaud = replay_adaptive_schedule(
                        adap["regime_events"], adap["misting_events"],
                        hourly_weather, duration_h,
                        poids, qv * (1 + f_ch), rho,
                        transp_scale=0.1,
                    )
                    adap_froid = replay_adaptive_schedule(
                        adap["regime_events"], adap["misting_events"],
                        hourly_weather, duration_h,
                        poids, qv * (1 - f_fr), rho,
                        transp_scale=1.0,
                    )
                    risk_adap_chaud = classify_risk(max(adap_chaud["T_C"])) if adap_chaud else None
                    risk_adap_froid = classify_risk(max(adap_froid["T_C"])) if adap_froid else None

        # Build weather display series
        weather_series = {
            "hours":           [w["t_h"] for w in hourly_weather],
            "hour_labels":     [w["hour_label"] for w in hourly_weather],
            "temps_C":         [round(w["temp_C"], 1) for w in hourly_weather],
            "rh_pct":          [round(w["rh_frac"] * 100, 1) for w in hourly_weather],
            "wind_kmh":        [round(w["wind_kmh"], 1) for w in hourly_weather],
            "truck_speed_kmh": [round(w["truck_speed_kmh"], 1) for w in hourly_weather],
            "lats":            [round(w["lat"], 4) for w in hourly_weather],
            "lons":            [round(w["lon"], 4) for w in hourly_weather],
            "source":          "open-meteo" if route_coords else "fallback",
        }

        return jsonify({
            "ok":               True,
            "ferme":            res_ferme["series"],
            "ferme_timeline":   res_ferme.get("timeline", []),
            "ferme_chaud":      ferme_chaud,
            "ferme_froid":      ferme_froid,
            "ouvert":           res_ouvert["series"] if res_ouvert else None,
            "adaptive":         res_adaptive,
            "adaptive_chaud":   adap_chaud,
            "adaptive_froid":   adap_froid,
            "risk_ferme":        risk_ferme,
            "risk_ouvert":       risk_ouvert,
            "risk_ferme_chaud":  risk_ferme_chaud,
            "risk_ferme_froid":  risk_ferme_froid,
            "risk_adap_chaud":   risk_adap_chaud,
            "risk_adap_froid":   risk_adap_froid,
            "T_max_ferme":      round(T_max_ferm, 2),
            "T_max_ouvert":     round(T_max_ouv, 2) if T_max_ouv is not None else None,
            "strategy_needed":      risk_ferme != "ok",
            "adaptive_not_needed":  adaptive_not_needed,
            "breed_name":       breed["fr"],
            "avg_speed_kmh":    round(avg_speed_kmh, 1),
            "stops":            route_stops,
            "weather":          weather_series,
        })

    except Exception as e:
        import traceback
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5005))
    app.run(host="0.0.0.0", port=port, debug=True)
