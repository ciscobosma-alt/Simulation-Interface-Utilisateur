import base64
from io import BytesIO
import html
import copy
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ============================================================
# CONSTANTES PHYSIQUES ET PARAMÈTRES PAR DÉFAUT
# ============================================================
# Capacités thermiques massiques (J/kg/K)
CP_SPHERE = 3500.0                 # tissu bovin (Hasgall 2022 : ~3421 J/kg/K) — remplacé par cp_sphere_J_kgK dans le payload
CP_AIR = 1007.0                    # air sec — fallback pour le compartiment camion hermétique
H_SANS_VENT_W_M2K = 5.0            # W/m²/K — base du modèle empirique de convection naturelle

# Constantes des gaz parfaits pour l'air humide
P_ATM = 101325.0                   # Pa   — pression atmosphérique standard
R_D = 287.05                       # J/kg/K — constante gaz air sec
R_V = 461.5                        # J/kg/K — constante gaz vapeur d'eau

# Paramètres d'évaporation
D_V = 2.6e-5                       # m²/s — diffusivité de la vapeur d'eau dans l'air
H_FG = 2.43e6                      # J/kg — chaleur latente de vaporisation de l'eau


# ============================================================
# UTILITAIRES GÉNÉRAUX
# ============================================================

def clamp(x: float, a: float, b: float) -> float:
    """Borne x dans l'intervalle [a, b]."""
    return float(max(a, min(b, x)))


def html_table(title: str, headers: list[str], rows: list[list[str]]) -> str:
    """Génère un tableau HTML Bootstrap à partir d'un titre, d'en-têtes et de lignes.
    Utilisé pour afficher les résultats numériques dans l'interface web.
    """
    def esc(x): return html.escape(str(x))
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = ""
    for r in rows:
        tds = "".join(f"<td>{esc(c)}</td>" for c in r)
        body += f"<tr>{tds}</tr>"
    return f"""
    <h3 style="margin-top:18px; font-size:.95rem; font-weight:600; color:#e6edf3;">{esc(title)}</h3>
    <div style="overflow:auto; max-width:100%; margin-bottom:16px;">
      <table class="table table-sm table-striped" style="min-width:900px; font-size:.82rem;">
        <thead><tr>{th}</tr></thead>
        <tbody>{body}</tbody>
      </table>
    </div>
    """


# ============================================================
# PROPRIÉTÉS THERMODYNAMIQUES DE L'AIR HUMIDE
# ============================================================
# Ces fonctions calculent ρ, μ, k, cp, Pr de l'air humide en fonction
# de la température (°C) et de l'humidité relative RH ∈ [0,1].
# Elles alimentent TOUS les calculs de transfert thermique et d'évaporation.

def pression_saturation_eau_Pa(T_C: float) -> float:
    """Pression de vapeur saturante (Pa) — formule de Magnus. Valide entre -40°C et +60°C."""
    return float(610.78 * np.exp((17.2694 * T_C) / (T_C + 237.29)))


def mu_air_sutherland_Pa_s(T_K: float) -> float:
    """Viscosité dynamique de l'air sec (Pa·s) — loi de Sutherland. Valide de ~170 K à ~1900 K."""
    mu0 = 1.716e-5
    T0 = 273.15
    S = 111.0
    return mu0 * (T_K / T0) ** 1.5 * (T0 + S) / (T_K + S)


def mu_vapeur_sutherland_Pa_s(T_K: float) -> float:
    """Viscosité dynamique de la vapeur d'eau (Pa·s) — loi de Sutherland."""
    mu0 = 1.00e-5
    T0 = 273.15
    S = 350.0
    return mu0 * (T_K / T0) ** 1.5 * (T0 + S) / (T_K + S)


def k_air_W_mK(T_K: float) -> float:
    """Conductivité thermique de l'air sec (W/m·K) — interpolation linéaire."""
    return 0.024 + 7.0e-5 * (T_K - 273.15)


def k_vapeur_W_mK(T_K: float) -> float:
    """Conductivité thermique de la vapeur d'eau (W/m·K) — interpolation linéaire."""
    return 0.016 + 8.0e-5 * (T_K - 273.15)


def wilke_mixing_mu(mu1, mu2, M1, M2, x1, x2):
    """Viscosité d'un mélange binaire de gaz — règle de Wilke.
    mu1/mu2 : viscosités des composants purs | M1/M2 : masses molaires | x1/x2 : fractions molaires.
    """
    phi12 = (1 + (mu1/mu2)**0.5 * (M2/M1)**0.25)**2 / (8*(1 + M1/M2))**0.5
    phi21 = (1 + (mu2/mu1)**0.5 * (M1/M2)**0.25)**2 / (8*(1 + M2/M1))**0.5
    mu_mix = (x1*mu1) / (x1 + x2*phi12) + (x2*mu2) / (x2 + x1*phi21)
    return float(mu_mix)


def simple_mix_k(k1, k2, x1, x2):
    """Conductivité d'un mélange par moyenne molaire pondérée (linéaire)."""
    return float(x1*k1 + x2*k2)


def air_humide_properties(T_C: float, RH: float, P: float = P_ATM):
    """Calcule les propriétés thermodynamiques de l'air humide.
    Retourne : (ρ [kg/m³], μ [Pa·s], k [W/m·K], cp [J/kg·K], Pr [-])

    Méthodes :
    - ρ   : loi des gaz parfaits (air sec + vapeur séparés)
    - μ   : Sutherland + règle de mélange de Wilke
    - k   : interpolation linéaire + moyenne molaire
    - cp  : moyenne massique (cp_air_sec + cp_vapeur pondérés par fraction massique)
    - Pr  : μ·cp / k
    """
    RH = float(np.clip(RH, 0.0, 1.0))
    T_K = T_C + 273.15

    p_sat = pression_saturation_eau_Pa(T_C)
    p_v = RH * p_sat
    p_v = min(p_v, 0.99 * P)
    p_d = P - p_v

    rho = p_d / (R_D * T_K) + p_v / (R_V * T_K)

    x_v = p_v / P
    x_d = 1.0 - x_v

    M_d = 0.028965
    M_v = 0.018016

    mu_d = mu_air_sutherland_Pa_s(T_K)
    mu_v = mu_vapeur_sutherland_Pa_s(T_K)
    mu = wilke_mixing_mu(mu_d, mu_v, M_d, M_v, x_d, x_v)

    k_d = k_air_W_mK(T_K)
    k_v = k_vapeur_W_mK(T_K)
    k = simple_mix_k(k_d, k_v, x_d, x_v)

    rho_v = p_v / (R_V * T_K)
    Yv = float(np.clip(rho_v / rho, 0.0, 1.0))
    cp_d = 1007.0
    cp_v = 1850.0
    cp = (1 - Yv) * cp_d + Yv * cp_v

    Pr = mu * cp / k
    return float(rho), float(mu), float(k), float(cp), float(Pr)


# ============================================================
# TRANSFERT THERMIQUE PAR CONVECTION — coefficient h (W/m²·K)
# ============================================================
# Deux régimes distincts selon la présence ou non de vent :
#   - Avec vent  → convection FORCÉE  : corrélation de Ranz-Marshall (pilotée par Re)
#   - Sans vent  → convection NATURELLE : modèle empirique OU Churchill-Bernstein (pilotée par Ra)
# Le choix sans-vent est paramétrable via conv_model dans le payload.

def h_convection_forcee_sphere_W_m2K(rayon_m: float, vent_kmh: float, Tinf_C: float, RH: float) -> float:
    """Coefficient h en convection FORCÉE sur sphère — corrélation de Ranz-Marshall.
    Nu = 2 + (0.4·Re^½ + 0.06·Re^⅔) · Pr^0.4    →    h = Nu·k/D
    Valide pour 3.5 < Re < 7.6×10⁴ et 0.71 < Pr < 380.
    """
    U = vent_kmh / 3.6
    D = 2.0 * rayon_m
    rho, mu, k, cp, Pr = air_humide_properties(Tinf_C, RH)
    Re = rho * U * D / mu
    Nu = 2.0 + (0.4 * np.sqrt(Re) + 0.06 * (Re ** (2/3))) * (Pr ** 0.4)
    return float(Nu * k / D)


def h_sans_vent_corrige(Tinf_C: float, RH: float) -> float:
    """Modèle empirique (original) : base 5 W/m²/K corrigé k et Pr."""
    rho, mu, k, cp, Pr = air_humide_properties(Tinf_C, RH)
    k_ref = 0.0263
    Pr_ref = 0.707
    return float(H_SANS_VENT_W_M2K * (k / k_ref) * (Pr / Pr_ref) ** 0.1)


def h_sans_vent_churchill(Tinf_C: float, RH: float, T_sphere_C: float, rayon_m: float) -> float:
    """Convection naturelle : corrélation Churchill-Bernstein (Ra).
    Nu = 2 + 0.589·Ra^(1/4) / [1+(0.469/Pr)^(9/16)]^(4/9)
    L'humidité agit via les propriétés de l'air humide (k, Pr, rho, cp, mu).
    """
    rho, mu, k, cp_air, Pr = air_humide_properties(Tinf_C, RH)
    D = 2.0 * rayon_m
    T_K = Tinf_C + 273.15
    delta_T = max(abs(T_sphere_C - Tinf_C), 0.01)  # éviter Ra=0 si ΔT≈0

    g = 9.81
    beta = 1.0 / T_K  # approximation gaz parfait

    Ra = g * beta * delta_T * (D ** 3) * rho**2 * cp_air / (mu * k)
    Nu = 2.0 + 0.589 * (Ra ** 0.25) / (1.0 + (0.469 / Pr) ** (9.0 / 16.0)) ** (4.0 / 9.0)
    return float(Nu * k / D)


# ============================================================
# TRANSFERT DE MASSE — ÉVAPORATION (débit max via Sherwood)
# ============================================================
# Analogie avec la convection thermique : même structure que Ranz-Marshall
# mais pour le transfert de masse (vapeur d'eau → air ambiant).
# Le vent accélère l'évaporation (Sh ∝ √Re → ṁ ∝ √U).
# L'humidité relative RH réduit le gradient de vapeur : si RH=1, ṁ=0.

def mdot_evap_max_kg_s(rayon_m: float, vent_kmh: float, T_air_C: float, RH: float) -> float:
    """Débit massique maximal d'évaporation (kg/s) — Sherwood.
    Sh = 2 + 0.6·Re^½·Sc^⅓    →    k_c = Sh·D_v/D    →    ṁ = k_c·(ρ_v,sat - ρ_v,∞)·S
    """
    RH = float(np.clip(RH, 0.0, 1.0))

    # Plancher à 0.1 km/h : simule le micro-mouvement d'air par convection naturelle
    # même en l'absence totale de vent (Sh=2 sinon → évaporation quasi nulle, irréaliste).
    U = max(vent_kmh, 0.1) / 3.6
    D = 2.0 * rayon_m
    S = 4.0 * np.pi * rayon_m**2

    rho, mu, k, cp, Pr = air_humide_properties(T_air_C, RH)

    Re = rho * U * D / mu
    Sc = mu / (rho * D_V)

    Sh = 2.0 + 0.6 * np.sqrt(max(Re, 0.0)) * (Sc ** (1/3))
    k_c = Sh * D_V / D  # m/s

    T_K = T_air_C + 273.15
    p_sat = pression_saturation_eau_Pa(T_air_C)
    rho_v_sat = p_sat / (R_V * T_K)
    rho_v_inf = RH * rho_v_sat

    mdot = k_c * max(rho_v_sat - rho_v_inf, 0.0) * S
    return float(mdot)


# ============================================================
# INTÉGRATION NUMÉRIQUE — Runge-Kutta ordre 4 (RK4)
# ============================================================
# Résout l'ODE thermique C·dT/dt = f(T) pas à pas.
# Deux variantes :
#   - rk4_step     : scalaire (sphère seule)
#   - rk4_step_vec : vectoriel (système couplé sphère + air camion)

def rk4_step(T, dt, deriv_func):
    """Un pas RK4 scalaire. deriv_func : T (°C) → dT/dt (°C/s)."""
    k1 = deriv_func(T)
    k2 = deriv_func(T + 0.5 * dt * k1)
    k3 = deriv_func(T + 0.5 * dt * k2)
    k4 = deriv_func(T + dt * k3)
    return T + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def rk4_step_vec(y, dt, deriv_func_vec):
    """Un pas RK4 vectoriel (array NumPy). Utilisé pour [T_sphère, T_air_camion]."""
    k1 = deriv_func_vec(y)
    k2 = deriv_func_vec(y + 0.5 * dt * k1)
    k3 = deriv_func_vec(y + 0.5 * dt * k2)
    k4 = deriv_func_vec(y + dt * k3)
    return y + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)



# ============================================================
# CAS EXTRÊMES — perturbation du payload nominal
# ============================================================

def appliquer_cas_extreme(payload: dict, f_masse: float, f_qv: float, f_vent: float,
                          f_transp: float = 0.1) -> dict:
    """Crée un payload perturbé pour simuler un cas extrême (chaud ou froid).

    Cas chaud (f > 1) : masse ↑, qv ↑, vent ↓  → plus d'animaux, moins de refroidissement
    Cas froid (f < 1) : masse ↓, qv ↓, vent ↑  → moins d'animaux, plus de refroidissement
    Le vent n'est modifié que pour les régimes avec vent (type ≠ 1).
    f_transp : fraction du débit de sudation nominal (défaut 0.1 = 10 %).
    """
    p = copy.deepcopy(payload)

    p["masse_kg"] = float(p["masse_kg"]) * f_masse
    p["puissance_volumique_W_m3"] = float(p["puissance_volumique_W_m3"]) * f_qv
    p["mdot_transp_m2_kgs"] = float(p.get("mdot_transp_m2_kgs", 1.5e-5)) * f_transp

    new_regs = []
    for r in p.get("regimes", []):
        r2 = dict(r)
        if int(r2.get("type", 1)) != 1 and "vent_kmh" in r2:
            r2["vent_kmh"] = max(float(r2["vent_kmh"]) * f_vent, 0.0)
        new_regs.append(r2)
    p["regimes"] = new_regs

    return p


# ============================================================
# SIMULATION D'UN CAS (nominal, chaud ou froid)
# ============================================================

def run_simulation_core(payload: dict, label_cas: str = "Nominal") -> dict:
    """Simule l'évolution thermique de la sphère sur la durée totale via RK4.

    Résout l'ODE :   C · dT/dt = P_int(T)  -  h·S·(T - T∞)  -  P_evap
    où :
        C        = masse × cp_sphere                (capacité thermique totale, J/K)
        P_int(T) = puissance métabolique régulée    (thermorégulation kc/kh entre Pmin et Pmax)
        h        = coefficient de convection        (Ranz-Marshall avec vent, empirique/Churchill sans vent)
        P_evap   = puissance extraite par évaporation (transpiration ou mouillage régime 3)

    Retourne : séries temporelles Plotly, PNG de secours, tableaux HTML, résumé numérique.
    """
    masse_kg = float(payload["masse_kg"])
    rho_sphere = float(payload["rho_sphere_kg_m3"])
    qv = float(payload["puissance_volumique_W_m3"])
    T0 = float(payload["T0_C"])
    t_fin_h = float(payload["duree_totale_h"])
    n_points = int(payload.get("n_points", 3000))

    T_min = float(payload["T_interval_min_C"])
    T_max = float(payload["T_interval_max_C"])

    mdot_in_kg_s = float(payload.get("debit_apparition_eau_kg_s", 0.0))
    vent_ambiant_kmh = float(payload.get("vent_ambiant_kmh", 0.0))

    # ----- Paramètres respiration / camion (utilisés seulement si régime sans vent + hermétique) -----
    Rth_camion_K_W = float(payload.get("Rth_camion_K_W", 0.0))          # K/W (résistance thermique globale parois)
    V_camion_m3 = float(payload.get("V_camion_m3", 0.0))               # m³ (volume air camion)
    V_poumon_m3 = float(payload.get("V_poumon_m3", 0.0))               # m³ par cycle et par individu
    periode_resp_s = float(payload.get("periode_resp_s", 0.0))         # s par cycle

    regimes = payload["regimes"]

    # ----- Validations -----
    if masse_kg <= 0:
        raise ValueError("La masse doit être > 0.")
    if rho_sphere <= 0:
        raise ValueError("ρ doit être > 0.")
    if t_fin_h <= 0:
        raise ValueError("La durée totale doit être > 0.")
    if n_points < 400:
        raise ValueError("Nombre de points doit être ≥ 400.")
    if not (T_max > T_min):
        raise ValueError("Il faut Tmax > Tmin.")
    if not (T_min <= T0 <= T_max):
        raise ValueError(f"T(0) doit être dans [{T_min}, {T_max}].")
    if mdot_in_kg_s < 0:
        raise ValueError("Débit d’apparition d’eau doit être ≥ 0.")
    if vent_ambiant_kmh < 0:
        raise ValueError("Vent ambiant doit être ≥ 0.")

    t_list = [float(r["t_debut_h"]) for r in regimes]
    if len(t_list) == 0:
        raise ValueError("Ajoute au moins un régime.")
    if any(t_list[i] >= t_list[i+1] for i in range(len(t_list)-1)):
        raise ValueError("Les t_debut doivent être strictement croissants.")
    if float(t_list[0]) != 0.0:
        raise ValueError("Le premier régime doit commencer à t=0.")
    if float(t_list[-1]) > t_fin_h:
        raise ValueError("Le dernier t_debut dépasse la durée totale.")

    # ----- Géométrie -----
    V = masse_kg / rho_sphere
    r = (3.0 * V / (4.0 * np.pi)) ** (1.0 / 3.0)
    S = 4.0 * np.pi * r**2

    # ----- Puissance et capacité -----
    P0_W = qv * V
    cp_sphere = float(payload.get("cp_sphere_J_kgK", CP_SPHERE))
    C_J_K = masse_kg * cp_sphere
    conv_model = str(payload.get("conv_model", "empirique"))  # "empirique" ou "churchill"

    # ----- Thermorégulation (optionnelle) -----
    thermoreg_enabled = bool(payload.get("thermoreg_enabled", True))
    thermoreg_model   = str(payload.get("thermoreg_model", "sigmoide"))  # "sigmoide" | "lineaire" | "empirique"

    # --- Mode sigmoïde (défaut) ---
    # Sigmoïde unique : Pint passe de Pmax (froid) à Pmin (chaud) via σ(-k*(T-T_sig))
    # À T_sig et bornes symétriques (Pmin+Pmax=2P0) : Pint(T_sig) = P0 exactement
    T_sig_C     = float(payload.get("T_sig_C",     38.5))  # °C — inflexion (= T_set physiologique)
    k_sig_per_C = float(payload.get("k_sig_per_C",  3.0))  # 1/°C — raideur (gain max = (Pmax-Pmin)*k/4)

    # --- Mode linéaire ---
    T_set_C  = float(payload.get("T_set_C",  T0))
    Delta_C  = float(payload.get("Delta_C",  0.2))
    k_c_W_K  = float(payload.get("k_c_W_K",  0.0))
    k_h_W_K  = float(payload.get("k_h_W_K",  0.0))

    # --- Mode empirique ---
    # Ancrages mesurés (littérature, fixes) :
    #   [38.5°C → f=1.00]  [39.2°C → f=1.15]  (PMC6722315 + Robinson 1986)
    T_emp_ref  = 38.5   # °C — point TNZ de référence
    T_emp_haut = 39.2   # °C — dernier point mesuré
    f_emp_haut = 1.15   # P/P0 au point haut mesuré
    k_froid_emp_W_K    = float(payload.get("k_froid_emp_W_K",   50.0))   # W/°C branche froide
    k_extrapole_emp_W_K = float(payload.get("k_extrapole_emp_W_K", 500.0)) # W/°C au-delà de 39.2°C

    # Convention A : Pmin/Pmax en % de P0 (ex: 60 -> 0.60*P0 ; 140 -> 1.40*P0)
    pct_pmin = float(payload.get("pct_pmin", 60.0))
    pct_pmax = float(payload.get("pct_pmax", 140.0))

    if Delta_C < 0:
        raise ValueError("Δ doit être ≥ 0.")
    if k_c_W_K < 0 or k_h_W_K < 0:
        raise ValueError("Les gains kc/kh doivent être ≥ 0.")
    if pct_pmin <= 0 or pct_pmax <= 0:
        raise ValueError("pct Pmin/Pmax doivent être > 0.")

    # Chaque cas (nominal, chaud, froid) utilise son propre P0
    Pmin_W = P0_W * (pct_pmin / 100.0)
    Pmax_W = P0_W * (pct_pmax / 100.0)
    if not (Pmax_W > Pmin_W):
        raise ValueError("Il faut Pmax > Pmin (via les pourcentages).")

    def Pint_W_of_T(T_C: float) -> float:
        if not thermoreg_enabled:
            return float(P0_W)

        if thermoreg_model == "sigmoide":
            # Sigmoïde lisse : Pmax (froid) → P0 (T_sig) → Pmin (chaud)
            P = Pmin_W + (Pmax_W - Pmin_W) / (1.0 + np.exp(k_sig_per_C * (T_C - T_sig_C)))
            return clamp(P, Pmin_W, Pmax_W)

        elif thermoreg_model == "empirique":
            # Branche froide : linéaire avec k_froid_emp (P augmente si T < T_ref)
            if T_C < T_emp_ref:
                P = P0_W + k_froid_emp_W_K * (T_emp_ref - T_C)
            # Zone mesurée 38.5→39.2°C : interpolation linéaire des données
            elif T_C <= T_emp_haut:
                alpha = (T_C - T_emp_ref) / (T_emp_haut - T_emp_ref)
                P = P0_W * (1.0 + alpha * (f_emp_haut - 1.0))
            # Zone extrapolée > 39.2°C : linéaire avec k_extrapole
            else:
                P_at_haut = P0_W * f_emp_haut
                P = P_at_haut + k_extrapole_emp_W_K * (T_C - T_emp_haut)
            return clamp(P, Pmin_W, Pmax_W)

        else:  # mode linéaire
            cold = k_c_W_K * max(0.0, (T_set_C - Delta_C) - T_C)
            hot  = k_h_W_K * max(0.0, T_C - (T_set_C + Delta_C))
            return clamp(P0_W + cold - hot, Pmin_W, Pmax_W)

    # ----- Segments -----
    base_segments = []
    for i, reg in enumerate(regimes):
        t0_h = float(reg["t_debut_h"])
        t1_h = float(regimes[i+1]["t_debut_h"]) if i < len(regimes)-1 else t_fin_h

        type_reg = int(reg["type"])
        Tinf = float(reg["Tinf_C"])
        RH = float(np.clip(float(reg.get("RH", 0.5)), 0.0, 1.0))

        vent = float(reg.get("vent_kmh", 0.0)) if type_reg != 1 else 0.0

        mouillage_min = float(reg.get("mouillage_duree_min", 0.0)) if type_reg == 3 else 0.0
        debit_L_s = float(reg.get("debit_eau_L_s", 0.0)) if type_reg == 3 else 0.0

        if mouillage_min < 0:
            raise ValueError("Durée de mouillage doit être ≥ 0.")
        if debit_L_s < 0:
            raise ValueError("Débit d’eau (L/s) doit être ≥ 0.")

        seg = {
            "t0_h": t0_h, "t1_h": t1_h, "type": type_reg,
            "Tinf_C": Tinf, "RH": RH, "vent_kmh": vent,
            "mouillage_duree_h": mouillage_min / 60.0,
            "debit_eau_L_s": debit_L_s,
            "evap_duree_h": 0.0,
            "hermetique": bool(reg.get("hermetique", False)) if type_reg == 1 else False,
            "N_individus": int(reg.get("N_individus", 1)) if type_reg == 1 else 1,
        }
        base_segments.append(seg)

    def segment_at_time(t_h: float):
        for seg in base_segments:
            if seg["t0_h"] <= t_h < seg["t1_h"] - 1e-12:
                return seg
        return base_segments[-1]

    # pré-calc h + paramètres évap régime 3
    for seg in base_segments:
        if seg["type"] == 1:
            if conv_model == "churchill":
                seg["h"] = h_sans_vent_churchill(seg["Tinf_C"], seg["RH"], T0, r)
            else:
                seg["h"] = h_sans_vent_corrige(seg["Tinf_C"], seg["RH"])
            seg["Pevap_reg3"] = 0.0
        else:
            seg["h"] = h_convection_forcee_sphere_W_m2K(r, seg["vent_kmh"], seg["Tinf_C"], seg["RH"])
            seg["Pevap_reg3"] = 0.0
            seg["evap_duree_h"] = 0.0

            if seg["type"] == 3 and seg["mouillage_duree_h"] > 0 and seg["debit_eau_L_s"] > 0:
                mdot_max = mdot_evap_max_kg_s(r, seg["vent_kmh"], seg["Tinf_C"], seg["RH"])

                # masse d'eau totale dispo (kg) ~ debit(L/s) * durée(s)
                m_eau = seg["debit_eau_L_s"] * (seg["mouillage_duree_h"] * 3600.0)

                if mdot_max > 0 and m_eau > 0:
                    evap_duree_h = (m_eau / mdot_max) / 3600.0
                    evap_duree_h = min(evap_duree_h, seg["t1_h"] - seg["t0_h"])
                    seg["evap_duree_h"] = float(max(evap_duree_h, 0.0))
                    seg["Pevap_reg3"] = float(mdot_max * H_FG)

    # ----- Transpiration sigmoïdale (paramètres) -----
    T_TRANSP_MID    = float(payload.get("T_transp_mid_C",    39.5))   # °C — inflexion
    K_TRANSP        = float(payload.get("k_transp_per_C",     8.0))   # 1/°C — raideur
    mdot_transp_m2  = float(payload.get("mdot_transp_m2_kgs", 1.5e-5)) # kg/m²/s au plateau
    mdot_transp_max = mdot_transp_m2 * S                               # kg/s total pour l'animal

    # ----- Intégration -----
    t_s = np.linspace(0.0, t_fin_h * 3600.0, n_points)
    dt = float(t_s[1] - t_s[0])
    t_h_arr = t_s / 3600.0

    T = np.empty_like(t_s)
    T[0] = T0

    # ----- Air camion (régime sans vent + hermétique) -----
    T_air = None
    prev_seg_id = None

    labels = []
    hs = []
    Pevs = []
    RHs = []
    Tinfs = []
    mdots = []

    for i in range(1, len(t_s)):
        t_h = t_h_arr[i]
        seg = segment_at_time(t_h)

        Tinf = seg["Tinf_C"]
        RH = seg["RH"]
        h = seg["h"]
        vent_reg = seg["vent_kmh"]

        # ----- Mode hermétique (sans vent) : Tinf est la température extérieure, et l'air du camion T_air évolue
        herm = bool(seg.get("hermetique", False)) and int(seg.get("type", 1)) == 1
        seg_id = (seg["t0_h"], seg["t1_h"], seg.get("hermetique", False))

        if herm:
            # Au début de ce régime, l'air démarre à la température extérieure (consigne utilisateur)
            if prev_seg_id != seg_id or T_air is None:
                T_air = float(Tinf)

            # validations (uniquement si hermétique utilisé)
            if Rth_camion_K_W <= 0:
                raise ValueError("Rth_camion_K_W doit être > 0 (mode hermétique).")
            if V_camion_m3 <= 0:
                raise ValueError("V_camion_m3 doit être > 0 (mode hermétique).")
            if V_poumon_m3 <= 0:
                raise ValueError("V_poumon_m3 doit être > 0 (mode hermétique).")
            if periode_resp_s <= 0:
                raise ValueError("periode_resp_s doit être > 0 (mode hermétique).")

            N = int(seg.get("N_individus", 1))
            if N <= 0:
                raise ValueError("N_individus doit être ≥ 1 (mode hermétique).")
        else:
            T_air = None

        prev_seg_id = seg_id

        # évap régime 3 active seulement pendant sa fenêtre calculée
        evap_active_reg3 = False
        Pevap_reg3 = 0.0

        # ===========================
        # MODIF 1 : borne double
        # ===========================
        if seg["type"] == 3 and seg["evap_duree_h"] > 0:
            t_start = seg["t0_h"]
            t_end = seg["t0_h"] + seg["evap_duree_h"]
            if (t_h >= t_start) and (t_h < t_end):
                evap_active_reg3 = True
                Pevap_reg3 = seg["Pevap_reg3"]

        # Sigmoïde de sudation : ~0 à T_set, 50 % à T_TRANSP_MID (39.5°C), plateau au-delà
        transp_factor = (
            0.0 if evap_active_reg3
            else 1.0 / (1.0 + np.exp(-K_TRANSP * (T[i-1] - T_TRANSP_MID)))
        )

        # Vent pour transfert de masse pendant transpiration
        vent_evap = vent_reg if seg["type"] != 1 else vent_ambiant_kmh

        # Pevap total
        if evap_active_reg3:
            Pevap_total = Pevap_reg3
            mdot_evap = Pevap_total / H_FG if H_FG > 0 else 0.0
            label = f"{label_cas} | Évaporation (régime 3)"
        else:
            mdot_max = mdot_evap_max_kg_s(r, vent_evap, Tinf, RH)
            mdot_evap = min(mdot_transp_max * transp_factor, mdot_max)
            Pevap_total = mdot_evap * H_FG
            if transp_factor > 0.05:
                label = f"{label_cas} | Transpiration"
            elif seg["type"] == 1:
                label = f"{label_cas} | Sans vent (hermétique)" if herm else f"{label_cas} | Sans vent"
            elif seg["type"] == 2:
                label = f"{label_cas} | Vent sans évap"
            else:
                label = f"{label_cas} | Vent (post-mouillage)"

        # ODE (sphère seule ou système couplé air-camion)
        if herm:
            Text = float(Tinf)  # température extérieure
            # propriétés air au niveau actuel (on réutilise le module air humide; humidité ignorée dans la respiration)
            rho_air, _, _, cp_air, _ = air_humide_properties(float(T_air), RH)
            cp_air = float(cp_air) if cp_air > 0 else CP_AIR
            m_air = rho_air * V_camion_m3

            # débit volumique expiré total (m³/s) = N * V_poumon / periode
            Vdot_total = N * V_poumon_m3 / periode_resp_s  # m³/s

            y_prev = np.array([T[i-1], float(T_air)], dtype=float)

            def deriv(y):
                Ts, Ta = float(y[0]), float(y[1])
                # Q_resp = m_dot * cp * (T_sphère - T_air)
                mdot_air = rho_air * Vdot_total
                Qresp = mdot_air * cp_air * (Ts - Ta)
                Qloss = (Ta - Text) / Rth_camion_K_W
                dTa_dt = (Qresp - Qloss) / (m_air * cp_air)

                dTs_dt = (Pint_W_of_T(Ts) - h*S*(Ts - Ta) - Pevap_total) / C_J_K
                return np.array([dTs_dt, dTa_dt], dtype=float)

            y_new = rk4_step_vec(y_prev, dt, deriv)
            T[i] = float(y_new[0])
            T_air = float(y_new[1])
            Tref_for_transfer = float(T_air)
        else:
            Tref_for_transfer = float(Tinf)

            def dTdt(Tval):
                return (Pint_W_of_T(Tval) - h*S*(Tval - Tref_for_transfer) - Pevap_total) / C_J_K

            T[i] = rk4_step(T[i-1], dt, dTdt)

        labels.append(label)
        hs.append(h)
        Pevs.append(Pevap_total)
        RHs.append(RH)
        Tinfs.append(Tinf)
        mdots.append(mdot_evap)

    # ----- Timeline compressée (sur labels) -----
    timeline = []
    if labels:
        cur = labels[0]
        cur_h = hs[0]
        cur_P = Pevs[0]
        cur_RH = RHs[0]
        cur_Tinf = Tinfs[0]
        cur_mdot = mdots[0]
        start_idx = 1

        for k in range(2, len(t_s)):
            idx = k - 2
            if labels[idx] != cur or abs(hs[idx]-cur_h) > 1e-12 or abs(Pevs[idx]-cur_P) > 1e-6:
                timeline.append({
                    "t_debut_h": float(t_h_arr[start_idx-1]),
                    "t_fin_h": float(t_h_arr[k-1]),
                    "label": cur,
                    "RH": float(cur_RH),
                    "Tinf_C": float(cur_Tinf),
                    "h_W_m2K": float(cur_h),
                    "Pevap_W": float(cur_P),
                    "mdot_evap_kg_s": float(cur_mdot),
                })
                start_idx = k-1
                cur = labels[idx]
                cur_h = hs[idx]
                cur_P = Pevs[idx]
                cur_RH = RHs[idx]
                cur_Tinf = Tinfs[idx]
                cur_mdot = mdots[idx]

        timeline.append({
            "t_debut_h": float(t_h_arr[start_idx-1]),
            "t_fin_h": float(t_h_arr[-1]),
            "label": cur,
            "RH": float(cur_RH),
            "Tinf_C": float(cur_Tinf),
            "h_W_m2K": float(cur_h),
            "Pevap_W": float(cur_P),
            "mdot_evap_kg_s": float(cur_mdot),
        })

    # ----- PNG fallback (courbe seule du cas) -----
    fig = plt.figure(figsize=(10, 5))
    plt.plot(t_h_arr, T)
    plt.axhline(T_max, linestyle=":")
    plt.axhline(T0, linestyle=":")
    plt.xlabel("Temps (h)")
    plt.ylabel("Température (°C)")
    plt.title(f"Température — {label_cas}")
    plt.grid(True)
    plt.tight_layout()
    bio = BytesIO()
    fig.savefig(bio, format="png", dpi=150)
    plt.close(fig)
    img_b64 = base64.b64encode(bio.getvalue()).decode("ascii")

    # ----- Séries Plotly (downsample) -----
    max_plot_points = 6000
    if len(t_h_arr) > max_plot_points:
        step = int(np.ceil(len(t_h_arr) / max_plot_points))
        t_plot = t_h_arr[::step]
        T_plot = T[::step]
    else:
        t_plot = t_h_arr
        T_plot = T

    series = {"t_h": [float(x) for x in t_plot], "T_C": [float(x) for x in T_plot]}

    # ----- Tables -----
    global_html = html_table(
        f"Tableau global — {label_cas}",
        ["Paramètre", "Valeur", "Unité"],
        [
            ["Masse sphère", f"{masse_kg:.6g}", "kg"],
            ["Masse volumique ρ", f"{rho_sphere:.6g}", "kg/m³"],
            ["cp sphère", f"{cp_sphere:.6g}", "J/kg/K"],
            ["Volume (déduit)", f"{V:.6g}", "m³"],
            ["Rayon (déduit)", f"{r:.6g}", "m"],
            ["Surface (déduite)", f"{S:.6g}", "m²"],
            ["Puissance volumique", f"{qv:.6g}", "W/m³"],
            ["Puissance totale P0 (déduite)", f"{P0_W:.6g}", "W"],
            ["Thermorégulation", "ON" if thermoreg_enabled else "OFF", "-"],
            ["Tset", f"{T_set_C:.6g}", "°C"],
            ["Δ (bande morte)", f"{Delta_C:.6g}", "°C"],
            ["kc (gain froid)", f"{k_c_W_K:.6g}", "W/K"],
            ["kh (gain chaud)", f"{k_h_W_K:.6g}", "W/K"],
            ["pct Pmin", f"{pct_pmin:.6g}", "% de P0"],
            ["pct Pmax", f"{pct_pmax:.6g}", "% de P0"],
            ["P0 utilisé pour bornes", f"{P0_W:.6g}", "W"],
            ["Pmin (déduit)", f"{Pmin_W:.6g}", "W"],
            ["Pmax (déduit)", f"{Pmax_W:.6g}", "W"],
            ["Capacité thermique C (déduite)", f"{C_J_K:.6g}", "J/K"],
            ["T(0)", f"{T0:.6g}", "°C"],
            ["Intervalle", f"[{T_min:.6g}, {T_max:.6g}]", "°C"],
            ["Débit apparition eau", f"{mdot_in_kg_s:.6g}", "kg/s"],
            ["Vent ambiant évap (si sans vent)", f"{vent_ambiant_kmh:.6g}", "km/h"],
        ]
    )

    regimes_rows = []
    for i, seg in enumerate(timeline, start=1):
        regimes_rows.append([
            str(i),
            f"{seg['t_debut_h']:.6g}",
            f"{seg['t_fin_h']:.6g}",
            seg["label"],
            f"{seg['RH']:.3f}",
            f"{seg['Tinf_C']:.6g}",
            f"{seg['h_W_m2K']:.6g}",
            f"{seg['Pevap_W']:.6g}",
            f"{seg['mdot_evap_kg_s']*1000:.6g}",
        ])

    regimes_html = html_table(
        f"Régimes actifs simulés — {label_cas}",
        ["#", "t_debut (h)", "t_fin (h)", "Mode actif", "RH (-)", "Tinf (°C)", "h (W/m²/K)",
         "Pevap (W)", "mdot_evap (g/s)"],
        regimes_rows
    )

    summary = {
        "cas": label_cas,
        "masse_kg": masse_kg,
        "rho_sphere_kg_m3": rho_sphere,
        "volume_m3": V,
        "rayon_m": r,
        "surface_m2": S,
        "qv_W_m3": qv,
        "P_interne_W": P0_W,
        "thermoreg_enabled": thermoreg_enabled,
        "T_set_C": T_set_C,
        "Delta_C": Delta_C,
        "k_c_W_K": k_c_W_K,
        "k_h_W_K": k_h_W_K,
        "pct_pmin": pct_pmin,
        "pct_pmax": pct_pmax,
        "P0_for_bounds_W": P0_W,
        "Pmin_W": Pmin_W,
        "Pmax_W": Pmax_W,
        "C_J_K": C_J_K,
        "T0_C": T0,
        "T_interval_min_C": T_min,
        "T_interval_max_C": T_max,
        "t_fin_h": t_fin_h,
        "n_points": n_points,
    }

    return {
        "series": series,
        "image_png_base64": img_b64,
        "table_global_html": global_html,
        "table_regimes_html": regimes_html,
        "summary": summary,
        "timeline": timeline,
    }


# ============================================================
# POINT D'ENTRÉE — lancement des trois cas (nominal + extrêmes)
# ============================================================

def run_all_cases(payload: dict) -> dict:
    """Lance la simulation pour les trois cas : nominal, cas chaud et cas froid.

    Cas chaud : masse×(1+f), qv×(1+f), vent×(1-f)
    Cas froid : masse×(1-f), qv×(1-f), vent×(1+f)
    Chaque cas calcule ses propres Pmin/Pmax depuis son P0 — sans référence au nominal.
    Retourne les séries et tableaux HTML pour l'interface web.
    """
    cas_extremes = bool(payload.get("cas_extremes", False))
    pct_chaud = float(payload.get("pct_chaud", 0.0) or 0.0)
    pct_froid = float(payload.get("pct_froid", 0.0) or 0.0)

    if cas_extremes:
        if not (0.0 <= pct_chaud < 100.0):
            raise ValueError("Pourcentage critique chaud doit être dans [0, 100[.")
        if not (0.0 <= pct_froid < 100.0):
            raise ValueError("Pourcentage critique froid doit être dans [0, 100[.")

    # ============================================================
    # ✅ MODIF MINIMALE : calcul du P0 nominal de référence (W)
    # (sert UNIQUEMENT à donner de la marge au cas froid)
    # ============================================================
    try:
        m0 = float(payload["masse_kg"])
        rho0 = float(payload["rho_sphere_kg_m3"])
        qv0 = float(payload["puissance_volumique_W_m3"])
        V0 = m0 / rho0
        P0_ref_W = qv0 * V0
    except Exception:
        P0_ref_W = None

    nominal = run_simulation_core(payload, label_cas="Nominal")

    chaud = None
    froid = None

    if cas_extremes:
        f_ch = pct_chaud / 100.0
        f_fr = pct_froid / 100.0

        payload_chaud = appliquer_cas_extreme(payload, f_masse=1.0, f_qv=1.0 + f_ch, f_vent=1.0 - f_ch)
        chaud = run_simulation_core(payload_chaud, label_cas="Cas chaud")

        payload_froid = appliquer_cas_extreme(payload, f_masse=1.0, f_qv=1.0 - f_fr, f_vent=1.0 + f_fr)
        froid = run_simulation_core(payload_froid, label_cas="Cas froid")

    rows = []
    rows.append([
        "Nominal",
        f"{nominal['summary']['masse_kg']:.6g}",
        f"{nominal['summary']['qv_W_m3']:.6g}",
        f"{nominal['summary']['P_interne_W']:.6g}",
        f"{nominal['summary']['rayon_m']:.6g}",
        f"{nominal['summary']['surface_m2']:.6g}",
    ])
    if chaud:
        rows.append([
            "Cas chaud",
            f"{chaud['summary']['masse_kg']:.6g}",
            f"{chaud['summary']['qv_W_m3']:.6g}",
            f"{chaud['summary']['P_interne_W']:.6g}",
            f"{chaud['summary']['rayon_m']:.6g}",
            f"{chaud['summary']['surface_m2']:.6g}",
        ])
    if froid:
        rows.append([
            "Cas froid",
            f"{froid['summary']['masse_kg']:.6g}",
            f"{froid['summary']['qv_W_m3']:.6g}",
            f"{froid['summary']['P_interne_W']:.6g}",
            f"{froid['summary']['rayon_m']:.6g}",
            f"{froid['summary']['surface_m2']:.6g}",
        ])

    table_extremes_html = html_table(
        "Comparatif des cas (nominal / chaud / froid)",
        ["Cas", "Masse (kg)", "qv (W/m³)", "P interne (W)", "Rayon (m)", "Surface (m²)"],
        rows
    )

    out = {
        "ok": True,

        "nominal": nominal["series"],
        "chaud": chaud["series"] if chaud else None,
        "froid": froid["series"] if froid else None,

        "table_global_html": nominal["table_global_html"],
        "table_regimes_html": nominal["table_regimes_html"],
        "table_extremes_html": table_extremes_html,

        "summary_nominal": nominal["summary"],
        "summary_chaud": chaud["summary"] if chaud else None,
        "summary_froid": froid["summary"] if froid else None,

        "timeline": nominal["timeline"],
        "image_png_base64": nominal["image_png_base64"],
    }
    return out
