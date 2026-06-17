// ═══════════════════════════════════════════════════════
// SiteSphere Transport — Interface Routier
// ═══════════════════════════════════════════════════════

// ── Traductions ──────────────────────────────────────────────────────────────
const STRINGS = {
  fr: {
    hero_eyebrow:     "Bien-être animal en transport",
    hero_title:       "Protégez votre troupeau en transit",
    hero_sub:         "Simulez la température de vos bovins pendant le transport routier. En quelques secondes, sachez si votre chargement est en sécurité.",
    hero_cta:         "Lancer une simulation",
    scroll_hint:      "↓ Commencer",
    s1_title:         "Vos animaux",
    race_label:       "Race",
    n_bovins_label:   "Nombre d'animaux",
    poids_label:      "Poids moyen (kg)",
    age_label:        "Âge moyen (mois)",
    strategy_title:   "Stratégie adaptive — en cours de développement",
    strategy_desc:    "Le graphe compare le trajet fenêtres fermées et fenêtres ouvertes. La logique de choix automatique sera définie prochainement.",
    s2_title:         "Itinéraire",
    depart_label:     "Ville de départ",
    arrivee_label:    "Ville d'arrivée",
    add_stop:         "Ajouter une étape",
    stop_label:       "Étape",
    stop_duration:    "Durée d'arrêt",
    distance:         "Distance :",
    duree_route:      "Durée du voyage :",
    duree_arrets:     "dont arrêts :",
    vitesse:          "Vitesse moy. :",
    date_depart_label:  "Date de départ",
    heure_depart_label: "Heure de départ",
    s3_title:         "Mode de ventilation",
    mode_ferme:       "Fenêtres fermées",
    mode_ferme_desc:  "Convection naturelle uniquement. Aucune circulation d'air forcée.",
    mode_ouvert:      "Fenêtres ouvertes",
    mode_ouvert_desc: "Circulation d'air naturelle par les ouvertures latérales du camion.",
    mode_urgence:     "Mode urgence",
    mode_urgence_desc:"Mouillage + évaporation forcée. Refroidissement maximal d'urgence.",
    simulate_btn:     "Simuler le trajet",
    graph_title:      "Température interne du bovin au cours du trajet",
    weather_title:    "Conditions météorologiques",
    temp_ext:         "Temp. extérieure",
    humidity:         "Humidité moy.",
    wind:             "Vent moy.",
    risk_ok_title:    "Confort thermique maintenu ✓",
    risk_ok_desc:     "Les bovins maintiennent une température normale tout au long du trajet. Aucune intervention nécessaire.",
    risk_caution_title:"Légère élévation thermique",
    risk_caution_desc: "La température dépasse légèrement les valeurs normales. Surveiller les animaux et prévoir une pause si le trajet se prolonge.",
    risk_warning_title:"Stress thermique — Attention ⚠",
    risk_warning_desc: "La température atteint des niveaux préoccupants. Un arrêt pour ventilation est fortement recommandé.",
    risk_danger_title: "Danger — Hyperthermie ❌",
    risk_danger_desc:  "La température est dangereusement élevée. Arrêt immédiat et refroidissement d'urgence nécessaires.",
    no_route:         "Veuillez sélectionner une ville de départ et d'arrivée.",
    sim_error:        "Erreur de simulation.",
    computing:        "Calcul en cours…",
    t_max_label:      "T max",
    unlimited:        "Illimité",
    timeline_title:   "Chronologie des interventions",
    misting_label:    "Brumisation",
    misting_event:    "min — déclenchée à T=",
    extreme_hot:      "cas chaud",
    extreme_cold:     "cas froid",
    extreme_cases:    "Cas extrêmes",
    adaptive_label:   "Adaptatif",
    closed_label:     "Fermé",
    adaptive_not_needed_msg: "✓ Fenêtres fermées suffisantes — aucune ouverture ni brumisation nécessaire.",
    windows_only_msg:        "✓ Ouverture des fenêtres suffisante — aucune brumisation nécessaire.",
    misting_needed_msg:      "⚠ Brumisation nécessaire —",
    misting_interventions:   "intervention(s) sur ce trajet —",
    misting_water_used:      "L d'eau utilisés.",
    water_reserve_label: "Réserve eau brumisation",
    water_used_of:    "utilisés",
    water_remaining:  "restants après le trajet",
    water_shortage:   "⚠ Eau insuffisante — il manquait",
    water_shortage_suf: "pour assurer le refroidissement sur l'ensemble du trajet.",
    water_ok:         "✓ Réservoir suffisant —",
    water_ok_suf:     "restants à l'arrivée.",
    water_used_unlimited: "Eau de brumisation utilisée :",
    water_tank_title: "Niveau du réservoir au cours du trajet",
    axis_time:        "Temps (h)",
    axis_temp_animal: "T animale (°C)",
    axis_temp_ext:    "T ext. (°C)",
    axis_limit:       "Limite",
    axis_normal:      "Normale",
    stop_chart:       "Arrêt",
    adaptive_strategy: "Stratégie adaptative",
    t_ext_label:      "T extérieure",
  },
  en: {
    hero_eyebrow:     "Animal welfare in transport",
    hero_title:       "Protect your herd in transit",
    hero_sub:         "Simulate the internal temperature of your cattle during road transport. In seconds, know if your load is safe.",
    hero_cta:         "Launch a simulation",
    scroll_hint:      "↓ Start",
    s1_title:         "Your animals",
    race_label:       "Breed",
    strategy_title:   "Adaptive strategy — in development",
    strategy_desc:    "The graph compares the trip with windows closed vs open. The automatic logic for choosing when to open or activate emergency cooling will be defined soon.",
    n_bovins_label:   "Number of cattle",
    poids_label:      "Average weight (kg)",
    age_label:        "Average age (months)",
    s2_title:         "Route",
    depart_label:     "Departure city",
    arrivee_label:    "Arrival city",
    add_stop:         "Add a stop",
    stop_label:       "Stop",
    stop_duration:    "Stop duration",
    distance:         "Distance:",
    duree_route:      "Journey time:",
    duree_arrets:     "of which stops:",
    vitesse:          "Avg. speed:",
    date_depart_label:  "Departure date",
    heure_depart_label: "Departure time",
    s3_title:         "Ventilation mode",
    mode_ferme:       "Windows closed",
    mode_ferme_desc:  "Natural convection only. No forced air circulation.",
    mode_ouvert:      "Windows open",
    mode_ouvert_desc: "Natural airflow through side openings of the truck.",
    mode_urgence:     "Emergency mode",
    mode_urgence_desc:"Wetting + forced evaporation. Maximum emergency cooling.",
    simulate_btn:     "Simulate the trip",
    graph_title:      "Internal cattle temperature during the trip",
    weather_title:    "Weather conditions",
    temp_ext:         "Ext. temperature",
    humidity:         "Avg. humidity",
    wind:             "Avg. wind",
    risk_ok_title:    "Thermal comfort maintained ✓",
    risk_ok_desc:     "Cattle maintain normal temperature throughout the trip. No intervention needed.",
    risk_caution_title:"Slight temperature rise",
    risk_caution_desc: "Temperature slightly exceeds normal values. Monitor animals and plan a break if the trip extends.",
    risk_warning_title:"Thermal stress — Warning ⚠",
    risk_warning_desc: "Temperature reaches concerning levels. A ventilation stop is strongly recommended.",
    risk_danger_title: "Danger — Hyperthermia ❌",
    risk_danger_desc:  "Temperature is dangerously high. Immediate stop and emergency cooling required.",
    no_route:         "Please select a departure and arrival city.",
    sim_error:        "Simulation error.",
    computing:        "Computing…",
    t_max_label:      "T max",
    unlimited:        "Unlimited",
    timeline_title:   "Intervention timeline",
    misting_label:    "Misting",
    misting_event:    "min — triggered at T=",
    extreme_hot:      "hot case",
    extreme_cold:     "cold case",
    extreme_cases:    "Extreme cases",
    adaptive_label:   "Adaptive",
    closed_label:     "Closed",
    adaptive_not_needed_msg: "✓ Windows closed sufficient — no opening or misting required.",
    windows_only_msg:        "✓ Window opening sufficient — no misting required.",
    misting_needed_msg:      "⚠ Misting required —",
    misting_interventions:   "intervention(s) on this trip —",
    misting_water_used:      "L of water used.",
    water_reserve_label: "Misting water reserve",
    water_used_of:    "used",
    water_remaining:  "remaining after trip",
    water_shortage:   "⚠ Insufficient water — missing",
    water_shortage_suf: "to ensure cooling throughout the trip.",
    water_ok:         "✓ Tank sufficient —",
    water_ok_suf:     "remaining on arrival.",
    water_used_unlimited: "Misting water used:",
    water_tank_title: "Tank level during the trip",
    axis_time:        "Time (h)",
    axis_temp_animal: "Animal temp (°C)",
    axis_temp_ext:    "Ext. temp (°C)",
    axis_limit:       "Limit",
    axis_normal:      "Normal",
    stop_chart:       "Stop",
    adaptive_strategy: "Adaptive strategy",
    t_ext_label:      "Ext. temp.",
  }
};

let currentLang = 'fr';

function t(key) { return STRINGS[currentLang][key] || key; }

let lastSimData = null;

function setLang(lang) {
  currentLang = lang;
  document.querySelectorAll('.lang-btn').forEach(b => {
    b.classList.toggle('active', b.textContent === lang.toUpperCase());
  });
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });
  document.documentElement.lang = lang;
  updateBreedNote();
  if (lastSimData) renderResults(lastSimData);
}

// ── Theme ────────────────────────────────────────────────────────────────────
let currentTheme = localStorage.getItem('sitesphere-theme') || 'dark';

function applyTheme(theme) {
  currentTheme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('sitesphere-theme', theme);
  const btn = document.getElementById('themeToggleBtn');
  if (btn) btn.textContent = theme === 'dark' ? '☀' : '🌙';
  setMapTiles(theme);
}

function toggleTheme() { applyTheme(currentTheme === 'dark' ? 'light' : 'dark'); }

// ── Map ──────────────────────────────────────────────────────────────────────
let map, mapTileLayer = null, routeLine = null;
const mapMarkers  = [];
const timeMarkers = [];

const MAP_TILES = {
  dark:  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
};

function setMapTiles(theme) {
  if (!map) return;
  if (mapTileLayer) { map.removeLayer(mapTileLayer); }
  mapTileLayer = L.tileLayer(MAP_TILES[theme] || MAP_TILES.dark, {
    attribution: '© OpenStreetMap © CARTO',
    subdomains: 'abcd', maxZoom: 19
  }).addTo(map);
}

function initMap() {
  map = L.map('map', { zoomControl: true, scrollWheelZoom: true }).setView([46.5, 2.3], 6);
  setMapTiles(currentTheme);
}

function makeMarkerIcon(color, glow) {
  return L.divIcon({
    className: '',
    html: `<div style="width:13px;height:13px;background:${color};border:2px solid #fff;border-radius:50%;box-shadow:0 0 10px ${glow}"></div>`,
    iconSize: [13, 13], iconAnchor: [6, 6],
  });
}

// ── City search ───────────────────────────────────────────────────────────────
let fromCoord = null, toCoord = null;
let debounceTimers = {};

function setupCitySearch(inputId, sugId, onSelect) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  const sug = document.getElementById(sugId);

  inp.addEventListener('input', () => {
    clearTimeout(debounceTimers[inputId]);
    const q = inp.value.trim();
    if (q.length < 2) { sug.style.display = 'none'; return; }
    debounceTimers[inputId] = setTimeout(async () => {
      try {
        const res  = await fetch(`/api/geocode?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        if (!data.length) { sug.style.display = 'none'; return; }
        sug.innerHTML = data.slice(0, 5).map((item) => {
          const label = item.display_name.split(',').slice(0, 3).join(', ');
          return `<div class="suggestion-item" data-lon="${item.lon}" data-lat="${item.lat}" data-name="${label}">${label}</div>`;
        }).join('');
        sug.style.display = 'block';
        sug.querySelectorAll('.suggestion-item').forEach(el => {
          el.addEventListener('click', () => {
            inp.value = el.dataset.name;
            sug.style.display = 'none';
            onSelect({ lon: parseFloat(el.dataset.lon), lat: parseFloat(el.dataset.lat), name: el.dataset.name });
          });
        });
      } catch {}
    }, 300);
  });

  document.addEventListener('click', e => {
    if (!inp.contains(e.target) && !sug.contains(e.target)) sug.style.display = 'none';
  });
}

function onFromSelected(coord) {
  fromCoord = coord;
  if (fromCoord && toCoord) calcRoute();
}
function onToSelected(coord) {
  toCoord = coord;
  if (fromCoord && toCoord) calcRoute();
}

// ── Intermediate stops ────────────────────────────────────────────────────────
let stopCounter = 0;
const stopsData = {};  // { id: { coord, stopDurationH } }

function addStop() {
  stopCounter++;
  const id = stopCounter;
  stopsData[id] = { coord: null, stopDurationH: 1 };

  const container = document.getElementById('stops_container');
  const div = document.createElement('div');
  div.id = `wp_stop_${id}`;
  div.className = 'wp-row';
  div.innerHTML = `
    <div class="wp-aside">
      <div class="wp-dot wp-dot--stop"></div>
      <div class="wp-line"></div>
    </div>
    <div class="wp-content">
      <div class="wp-stop-card">
        <div class="wp-stop-header">
          <span class="wp-stop-label">${t('stop_label')} ${id}</span>
          <button class="wp-remove-btn" onclick="removeStop(${id})">×</button>
        </div>
        <div class="city-search-wrapper">
          <input class="input-field" type="text" id="city_stop_${id}" placeholder="Clermont-Ferrand" autocomplete="off">
          <div class="suggestions" id="sug_stop_${id}"></div>
        </div>
        <div class="stop-duration-row">
          <label>${t('stop_duration')} :</label>
          <input class="input-field" type="number" id="dur_stop_${id}" value="1" min="0" max="24" step="0.5">
          <span>h</span>
        </div>
      </div>
    </div>`;
  container.appendChild(div);

  document.getElementById(`dur_stop_${id}`).addEventListener('input', () => {
    stopsData[id].stopDurationH = parseFloat(document.getElementById(`dur_stop_${id}`).value) || 0;
    if (fromCoord && toCoord) calcRoute();
  });

  setupCitySearch(`city_stop_${id}`, `sug_stop_${id}`, coord => {
    stopsData[id].coord = coord;
    if (fromCoord && toCoord) calcRoute();
  });
}

function removeStop(id) {
  delete stopsData[id];
  const el = document.getElementById(`wp_stop_${id}`);
  if (el) el.remove();
  if (fromCoord && toCoord) calcRoute();
}

function getOrderedStops() {
  return Object.entries(stopsData)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([, v]) => v)
    .filter(s => s.coord !== null);
}

// ── Route calculation (multi-waypoint) ───────────────────────────────────────
let routeDurationH   = 4;
let routeCoords      = null;
let routeSpeedsKmh   = null;
let routeAvgSpeedKmh = 80;
let routeStops       = [];  // [{t_arrive_h, duration_h, t_depart_h, lat, lon}]
const MAX_TRUCK_KMH  = 80;

// ── Adaptive strategy ─────────────────────────────────────────────────────────
const mistingDurationMin = 60;

// Wizard state — drives simulation params
let wizAdaptive  = false;   // adaptive strategy on/off
let wizMisting   = false;   // misting available (only relevant when adaptive on)
let wizReservoir = 10;      // liters (null = unlimited)

function wizardContinue() {
  if (!fromCoord || !toCoord) { showAlert(t('no_route')); return; }
  clearAlert();
  document.getElementById('wizOverlay').classList.add('open');
  // Scroll overlay to top in case it was scrolled before
  document.getElementById('wizOverlay').scrollTop = 0;
}

function wizardBack() {
  document.getElementById('wizOverlay').classList.remove('open');
}

function toggleAdaptiveCard() {
  wizAdaptive = !wizAdaptive;
  const card  = document.getElementById('cardAdaptive');
  const chk   = document.getElementById('chkAdaptive');
  card.classList.toggle('r-on-adaptive', wizAdaptive);
  chk.className = wizAdaptive ? 'r-check chk-adaptive' : 'r-check';
  chk.textContent = wizAdaptive ? '✓' : '';

  // Dim/enable misting card based on adaptive state
  const cardMist = document.getElementById('cardMist');
  if (!wizAdaptive) {
    cardMist.classList.add('r-dim');
    if (wizMisting) { wizMisting = false; _applyMistingState(); }
  } else {
    cardMist.classList.remove('r-dim');
  }
}

function toggleMistingCard() {
  if (!wizAdaptive) return;
  wizMisting = !wizMisting;
  _applyMistingState();
}

function _applyMistingState() {
  const card = document.getElementById('cardMist');
  const chk  = document.getElementById('chkMist');
  card.classList.toggle('r-on-mist', wizMisting);
  chk.className = wizMisting ? 'r-check chk-mist' : 'r-check';
  chk.textContent = wizMisting ? '✓' : '';
  // Show/hide reservoir section
  document.getElementById('wizRes').classList.toggle('res-hidden', !wizMisting);
}

function setReservoir(val) {
  wizReservoir = val;
  document.querySelectorAll('.res-pill').forEach(btn => {
    const rv = btn.dataset.rv;
    const btnVal = rv === 'unlimited' ? null : parseInt(rv);
    btn.classList.toggle('rp-on', btnVal === val);
  });
}

function onCasExtremesWizToggle() {
  const en = document.getElementById('casExtremesEnabled').checked;
  document.getElementById('extremeBodyWiz').classList.toggle('xopen', en);
}

function carToTruckKmh(carMs) {
  const kmh = carMs * 3.6;
  return kmh <= 50 ? Math.min(kmh, 50) : 80;
}

async function calcRoute() {
  if (!fromCoord || !toCoord) return;
  const orderedStops = getOrderedStops();
  const allPoints    = [fromCoord, ...orderedStops.map(s => s.coord), toCoord];

  try {
    const res  = await fetch('/api/route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ waypoints: allPoints }),
    });
    const data = await res.json();
    if (data.code !== 'Ok' || !data.routes?.length) throw new Error('No route');

    const route  = data.routes[0];
    const distKm = route.distance / 1000;
    routeCoords  = route.geometry.coordinates;

    // Merge per-leg annotation speeds
    const allSpeeds = [];
    for (const leg of route.legs || []) {
      for (const s of (leg.annotation?.speed || [])) allSpeeds.push(carToTruckKmh(s));
    }
    routeSpeedsKmh = allSpeeds.length ? allSpeeds : null;

    // Build stop timeline
    routeStops = [];
    let cumulH = 0;
    for (let i = 0; i < orderedStops.length; i++) {
      const legDistKm = route.legs[i].distance / 1000;
      const legDrivH  = legDistKm / MAX_TRUCK_KMH;
      cumulH += legDrivH;
      const durH = orderedStops[i].stopDurationH;
      routeStops.push({ t_arrive_h: cumulH, duration_h: durH, t_depart_h: cumulH + durH,
                        lat: orderedStops[i].coord.lat, lon: orderedStops[i].coord.lon });
      cumulH += durH;
    }
    const lastLeg   = route.legs[route.legs.length - 1];
    const lastDrivH = (lastLeg.distance / 1000) / MAX_TRUCK_KMH;
    cumulH += lastDrivH;

    routeAvgSpeedKmh = MAX_TRUCK_KMH;
    routeDurationH   = Math.max(0.5, cumulH);
    const totalStopH = orderedStops.reduce((s, st) => s + st.stopDurationH, 0);
    const totalH = routeDurationH;
    const th = Math.floor(totalH), tm = Math.round((totalH - th) * 60);

    document.getElementById('route_dist').textContent = ` ${distKm.toFixed(0)} km`;
    document.getElementById('route_dur').textContent  = ` ${th}h${tm > 0 ? tm + 'min' : ''}`;
    document.getElementById('route_meta').style.display = 'flex';

    const stopsItem = document.getElementById('route_stops_item');
    if (totalStopH > 0 && stopsItem) {
      const sh = Math.floor(totalStopH), sm = Math.round((totalStopH - sh) * 60);
      document.getElementById('route_stops_dur').textContent = ` ${sh}h${sm > 0 ? sm + 'min' : ''}`;
      stopsItem.style.display = '';
    } else if (stopsItem) {
      stopsItem.style.display = 'none';
    }

    // Refresh map
    mapMarkers.forEach(mk => mk.remove()); mapMarkers.length = 0;
    mapMarkers.push(L.marker([fromCoord.lat, fromCoord.lon], { icon: makeMarkerIcon('#2997ff','rgba(41,151,255,0.6)') }).addTo(map));
    orderedStops.forEach(s => mapMarkers.push(L.marker([s.coord.lat, s.coord.lon], { icon: makeMarkerIcon('#ff9f0a','rgba(255,159,10,0.6)') }).addTo(map)));
    mapMarkers.push(L.marker([toCoord.lat, toCoord.lon], { icon: makeMarkerIcon('#30d158','rgba(48,209,88,0.6)') }).addTo(map));

    if (routeLine) routeLine.remove();
    routeLine = L.polyline(routeCoords.map(([ln, lt]) => [lt, ln]), { color: '#2997ff', weight: 3, opacity: 0.85 }).addTo(map);
    map.fitBounds(routeLine.getBounds(), { padding: [20, 20] });
    buildTimeMarkers();

  } catch {
    routeCoords = null; routeSpeedsKmh = null; routeStops = [];
    const R    = 6371;
    const dLat = (toCoord.lat - fromCoord.lat) * Math.PI / 180;
    const dLon = (toCoord.lon - fromCoord.lon) * Math.PI / 180;
    const a    = Math.sin(dLat/2)**2 + Math.cos(fromCoord.lat*Math.PI/180)*Math.cos(toCoord.lat*Math.PI/180)*Math.sin(dLon/2)**2;
    const dist = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    routeAvgSpeedKmh = 80; routeDurationH = Math.max(0.5, dist / 80);
    const h = Math.floor(routeDurationH), m = Math.round((routeDurationH - h) * 60);
    document.getElementById('route_dist').textContent = ` ~${dist.toFixed(0)} km`;
    document.getElementById('route_dur').textContent  = ` ${h}h${m > 0 ? m + 'min' : ''}`;
    document.getElementById('route_meta').style.display = 'flex';
    if (routeLine) routeLine.remove();
    routeLine = L.polyline([[fromCoord.lat, fromCoord.lon],[toCoord.lat, toCoord.lon]],
      { color: '#2997ff', weight: 2, dashArray: '6 4', opacity: 0.7 }).addTo(map);
    map.fitBounds(routeLine.getBounds(), { padding: [20, 20] });
    buildTimeMarkers();
  }
}

// ── Time markers on route ────────────────────────────────────────────────────
function buildTimeMarkers() {
  timeMarkers.forEach(m => m.remove()); timeMarkers.length = 0;
  if (!routeCoords || routeCoords.length < 2 || routeDurationH < 2) return;

  const totalStopH = (routeStops || []).reduce((s, st) => s + (st.duration_h || 0), 0);
  const drivingH   = Math.max(0.01, routeDurationH - totalStopH);

  // Cumulative distance along routeCoords
  const cumDist = [0];
  for (let i = 1; i < routeCoords.length; i++) {
    const [ln1, lt1] = routeCoords[i - 1], [ln2, lt2] = routeCoords[i];
    const R = 6371, dLat = (lt2 - lt1) * Math.PI / 180, dLon = (ln2 - ln1) * Math.PI / 180;
    const a = Math.sin(dLat/2)**2 + Math.cos(lt1*Math.PI/180)*Math.cos(lt2*Math.PI/180)*Math.sin(dLon/2)**2;
    cumDist.push(cumDist[i - 1] + R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
  }
  const totalDist = cumDist[cumDist.length - 1];

  // Departure hour from form
  const deptStr  = (document.getElementById('heure_depart')?.value || '08:00').split(':');
  const deptHour = parseInt(deptStr[0]) + parseInt(deptStr[1] || 0) / 60;

  for (let t = 2; t < routeDurationH; t += 2) {
    // Driving time elapsed at total-time t (subtract stops that occurred before t)
    let stopsBefore = 0;
    for (const st of (routeStops || [])) {
      if (st.t_arrive_h < t) stopsBefore += Math.min(st.duration_h, t - st.t_arrive_h);
    }
    const drivElapsed = Math.min(drivingH, t - stopsBefore);
    const fraction    = drivElapsed / drivingH;
    const targetDist  = fraction * totalDist;

    let idx = cumDist.findIndex(d => d >= targetDist);
    if (idx < 0) idx = routeCoords.length - 1;
    const [lon, lat] = routeCoords[idx];

    const clockH = Math.floor((deptHour + t) % 24);
    const clockM = Math.round(((deptHour + t) % 1) * 60);
    const clock  = `${String(clockH).padStart(2,'0')}:${String(clockM).padStart(2,'0')}`;

    const icon = L.divIcon({
      className: '',
      html: `<div class="route-time-dot"><span class="rtd-label">+${t}h</span><span class="rtd-clock">${clock}</span></div>`,
      iconAnchor: [0, 8],
    });
    timeMarkers.push(L.marker([lat, lon], { icon, interactive: false }).addTo(map));
  }
}

// ── Race dropdown custom ──────────────────────────────────────────────────────
function toggleRaceDropdown() {
  document.getElementById('raceSelect').classList.toggle('open');
}

function selectRace(value, label) {
  document.getElementById('race').value        = value;
  document.getElementById('race_display').textContent = label;
  document.querySelectorAll('#race_options .custom-option').forEach(el => {
    el.classList.toggle('selected', el.dataset.value === value);
  });
  document.getElementById('raceSelect').classList.remove('open');
  updateBreedNote();
}

document.addEventListener('click', e => {
  const sel = document.getElementById('raceSelect');
  if (sel && !sel.contains(e.target)) sel.classList.remove('open');
});

// ── Mode selection (interne, non exposé à l'UI) ───────────────────────────────
let selectedMode = 'ferme';

function selectMode(mode) {
  selectedMode = mode;
  document.querySelectorAll('.mode-card').forEach(c => {
    c.classList.remove('selected', 'selected-urgence');
  });
  const card = document.querySelector(`.mode-card[data-mode="${mode}"]`);
  if (mode === 'urgence') card.classList.add('selected-urgence');
  else card.classList.add('selected');
}

// ── Simulation ────────────────────────────────────────────────────────────────
async function runSimulation() {
  const btn = document.getElementById('btnSimulateWiz');
  const errEl = document.getElementById('alertErrorWiz');
  const clearWizAlert = () => { if (errEl) { errEl.textContent = ''; errEl.style.display = 'none'; } };
  const showWizAlert  = msg => { if (errEl) { errEl.textContent = msg; errEl.style.display = 'block'; } };
  clearWizAlert();

  btn.classList.add('loading');
  btn.disabled = true;
  btn.querySelector('.btn-label').textContent = t('computing');
  startSimAnimation();

  try {
    const timeVal       = document.getElementById('heure_depart').value || '08:00';
    const hourStart     = parseInt(timeVal.split(':')[0]) || 8;
    const departureDateEl = document.getElementById('date_depart');
    const departureDate = departureDateEl ? departureDateEl.value : new Date().toISOString().slice(0, 10);

    const body = {
      poids_kg:            parseFloat(document.getElementById('poids').value) || 350,
      n_bovins:            parseInt(document.getElementById('n_bovins').value) || 10,
      race:                document.getElementById('race')?.value || 'autre',
      duration_h:          routeDurationH,
      hour_start:          hourStart,
      departure_date:      departureDate,
      route_coords:        routeCoords,
      route_speeds_kmh:    routeSpeedsKmh,
      route_stops:         routeStops,
      avg_speed_kmh:       routeAvgSpeedKmh,
      adaptive_enabled:    wizAdaptive,
      misting_enabled:     wizMisting,
      misting_duration_min: mistingDurationMin,
      available_water_L:   wizAdaptive && wizMisting ? wizReservoir : null,
      cas_extremes_enabled: document.getElementById('casExtremesEnabled')?.checked ?? false,
      pct_chaud:           parseFloat(document.getElementById('pct_chaud')?.value) || 20,
      pct_froid:           parseFloat(document.getElementById('pct_froid')?.value) || 20,
      seed:                Math.floor(Math.random() * 9999),
    };

    const res  = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();

    if (!data.ok) { stopSimAnimation(); showWizAlert(data.error || t('sim_error')); return; }

    // Close wizard, show results
    stopSimAnimation();
    document.getElementById('wizOverlay').classList.remove('open');
    renderResults(data);

  } catch (e) {
    stopSimAnimation();
    showWizAlert(e.message);
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
    btn.querySelector('.btn-label').textContent = 'Simuler le trajet';
  }
}

// ── Breed note ────────────────────────────────────────────────────────────────
const BREED_NOTES = {
  fr: {
    holstein:  "Race laitière haute production — métabolisme élevé",
    normande:  "Race mixte — métabolisme modéré à élevé",
    simmental: "Race mixte — métabolisme modéré",
    charolais: "Race à viande française — métabolisme modéré",
    angus:     "Race à viande — bonne résistance thermique",
    limousin:  "Race rustique à viande — métabolisme modéré-bas",
    blonde:    "Race à viande du Sud-Ouest — métabolisme modéré",
    salers:    "Race rustique de montagne — métabolisme bas",
    autre:     "Valeurs moyennes génériques",
  },
  en: {
    holstein:  "High-yield dairy breed — elevated metabolism",
    normande:  "Dual-purpose breed — moderate to high metabolism",
    simmental: "Dual-purpose breed — moderate metabolism",
    charolais: "French beef breed — moderate metabolism",
    angus:     "Beef breed — good heat resistance",
    limousin:  "Rustic beef breed — moderate-low metabolism",
    blonde:    "Southwest French beef breed — moderate metabolism",
    salers:    "Mountain rustic breed — low metabolism",
    autre:     "Generic average values",
  }
};

function updateBreedNote() {
  const key = document.getElementById('race')?.value || 'autre';
  const el  = document.getElementById('breed_note');
  if (el) el.textContent = BREED_NOTES[currentLang]?.[key] || '';
}

// ── Risk classification ───────────────────────────────────────────────────────
function classifyRisk(tMax) {
  if (tMax > 41.0) return 'danger';
  if (tMax > 40.0) return 'warning';
  if (tMax > 39.5) return 'caution';
  return 'ok';
}

// ── Curve visibility toggles ─────────────────────────────────────────────────
let _allTraces   = [];   // full trace list, set after each simulation
let _traceVis    = {};   // { traceName: bool }

function buildCurveToggles(traces) {
  _allTraces = traces;
  _traceVis  = {};

  // Default visibility: hide open-windows + ext-temp; also hide closed-windows when adaptive
  // BUT if adaptive_not_needed, closed-windows IS the answer → keep it visible
  const HIDDEN_BY_DEFAULT = new Set([t('mode_ouvert'), t('t_ext_label')]);
  if (wizAdaptive && !lastSimData?.adaptive_not_needed) {
    HIDDEN_BY_DEFAULT.add(t('mode_ferme'));
    // Hide "Fermé" extreme cases — the fair comparison is Adaptive vs Adaptive extremes
    HIDDEN_BY_DEFAULT.add(`${t('closed_label')} — ${t('extreme_hot')}`);
    HIDDEN_BY_DEFAULT.add(`${t('closed_label')} — ${t('extreme_cold')}`);
  }

  // Overlay traces (showlegend:false) inherit their parent curve's visibility
  const TRANSP_PARENT = {
    '_grad_ferme':         t('mode_ferme'),
    '_grad_adaptive':      t('adaptive_strategy'),
    '_grad_ferme_chaud':   `${t('closed_label')} — ${t('extreme_hot')}`,
    '_grad_ferme_froid':   `${t('closed_label')} — ${t('extreme_cold')}`,
    '_grad_adap_chaud':    `${t('adaptive_label')} — ${t('extreme_hot')}`,
    '_grad_adap_froid':    `${t('adaptive_label')} — ${t('extreme_cold')}`,
  };
  traces.forEach(tr => {
    if (tr.showlegend === false) {
      const parent = TRANSP_PARENT[tr.name];
      _traceVis[tr.name] = parent ? !HIDDEN_BY_DEFAULT.has(parent) : true;
    } else {
      _traceVis[tr.name] = !HIDDEN_BY_DEFAULT.has(tr.name);
    }
  });

  const COLOR_MAP = {
    [t('mode_ferme')]:          '#ff453a',
    [t('mode_ouvert')]:         '#2997ff',
    [t('adaptive_strategy')]:   '#ffd60a',
    [t('t_ext_label')]:         'rgba(90,200,250,0.8)',
  };

  // Only show toggle buttons for named legend traces (exclude showlegend:false overlays)
  const toggleTraces = traces.filter(tr => tr.showlegend !== false);
  const container = document.getElementById('curve-toggles');
  container.innerHTML = toggleTraces.map(tr => {
    const checked = _traceVis[tr.name];
    const color   = COLOR_MAP[tr.name] || tr.line?.color || '#86868b';
    return `<label class="curve-toggle" style="--c:${color}">
      <input type="checkbox" ${checked ? 'checked' : ''} onchange="toggleCurve('${tr.name}', this.checked)">
      <span class="curve-swatch"></span>
      <span class="curve-label">${tr.name}</span>
    </label>`;
  }).join('');

  // Apply initial visibility (re-render with only the visible traces)
  const gd = document.getElementById('plotly-main');
  const active = traces.filter(tr => _traceVis[tr.name]);
  Plotly.react(gd, active, gd.layout, { responsive: true, displaylogo: false, displayModeBar: false, scrollZoom: false });
}

function toggleCurve(name, visible) {
  _traceVis[name] = visible;
  // Sync gradient overlays to their parent curve
  const OVERLAY_CHILDREN = {
    [t('mode_ferme')]:                                  ['_grad_ferme'],
    [t('adaptive_strategy')]:                           ['_grad_adaptive'],
    [`${t('closed_label')} — ${t('extreme_hot')}`]:    ['_grad_ferme_chaud'],
    [`${t('closed_label')} — ${t('extreme_cold')}`]:   ['_grad_ferme_froid'],
    [`${t('adaptive_label')} — ${t('extreme_hot')}`]:  ['_grad_adap_chaud'],
    [`${t('adaptive_label')} — ${t('extreme_cold')}`]: ['_grad_adap_froid'],
  };
  (OVERLAY_CHILDREN[name] || []).forEach(child => { _traceVis[child] = visible; });
  const active = _allTraces.filter(tr => _traceVis[tr.name]);
  const gd = document.getElementById('plotly-main');
  Plotly.react(gd, active, gd.layout, { responsive: true, displaylogo: false, displayModeBar: false });
}

// ── Adaptive helpers ──────────────────────────────────────────────────────────

function buildRegimeBands(regimeEvents, durationH) {
  if (!regimeEvents || !regimeEvents.length) return [];
  const bands = [];
  for (let i = 0; i < regimeEvents.length; i++) {
    const start = regimeEvents[i].t_h;
    const end   = i + 1 < regimeEvents.length ? regimeEvents[i + 1].t_h : durationH;
    const mode  = regimeEvents[i].mode;
    if (mode !== 'ferme') bands.push({ start, end, mode });
  }
  return bands;
}

function renderEventLog(adaptive) {
  const card = document.getElementById('eventLogCard');
  if (!adaptive || !adaptive.regime_events || !adaptive.regime_events.length) {
    card.style.display = 'none';
    return;
  }
  card.style.display = '';

  const DOT_COLOR  = { ferme: '#86868b', ouvert: '#ff9f0a', brumisation: '#2997ff' };
  const MODE_LABEL = { ferme: t('mode_ferme'), ouvert: t('mode_ouvert'), brumisation: t('misting_label') };

  // Merge regime changes + misting details
  const items = [
    ...adaptive.regime_events.map(e => ({ t_h: e.t_h, kind: 'regime', mode: e.mode, text: e.reason })),
    ...(adaptive.misting_events || []).map(e => ({
      t_h: e.t_start_h, kind: 'misting',
      mode: 'brumisation',
      text: `${t('misting_label')} ${Math.round((e.t_end_h - e.t_start_h) * 60)} ${t('misting_event')}${e.T_trigger} °C`,
    })),
  ].sort((a, b) => a.t_h - b.t_h);

  const rows = items.map(item => {
    const h   = Math.floor(item.t_h);
    const m   = Math.round((item.t_h - h) * 60);
    const hms = `+${h}h${m.toString().padStart(2, '0')}`;
    const dot = `<span class="ev-dot" style="background:${DOT_COLOR[item.mode] || '#86868b'}"></span>`;
    const modeTag = `<span class="ev-mode" style="color:${DOT_COLOR[item.mode]}">${MODE_LABEL[item.mode] || item.mode}</span>`;
    return `<div class="ev-row">
      <span class="ev-time">${hms}</span>
      ${dot}
      ${modeTag}
      <span class="ev-text">${item.text}</span>
    </div>`;
  }).join('');

  card.innerHTML = `
    <div class="graph-title" style="margin-bottom:14px">${t('timeline_title')}</div>
    <div class="ev-list">${rows}</div>`;
}

// ── Render results ────────────────────────────────────────────────────────────
function makeTranspGradientTrace(tArr, TArr, transpScale, name) {
  const colors = TArr.map(T => {
    const f = (1 / (1 + Math.exp(-8 * (T - 39.5)))) * transpScale;
    if (f < 0.02) return 'rgba(0,0,0,0)';
    const norm = Math.min(1, (f - 0.02) / 0.98);
    const g = Math.round(159 * (1 - norm));
    const a = (0.2 + 0.75 * norm).toFixed(2);
    return `rgba(255,${g},0,${a})`;
  });
  return {
    type: 'scatter', x: tArr, y: TArr,
    mode: 'markers',
    marker: { color: colors, size: 5, opacity: 1 },
    showlegend: false,
    hoverinfo: 'skip',
    name,
  };
}

function renderResults(data) {
  lastSimData = data;
  const section = document.getElementById('results');
  section.style.display = 'block';

  // Risk banner — show adaptive result if available, else ferme
  const adaptive   = data.adaptive;
  const riskSource = adaptive ? adaptive.risk : data.risk_ferme;
  const tMaxShow   = adaptive ? adaptive.T_max : data.T_max_ferme;
  const risk       = data.risk_ferme;  // always base risk on ferme for banner color
  const banner     = document.getElementById('riskBanner');
  banner.className = `risk-banner ${riskSource}`;
  document.getElementById('riskTitle').textContent = t(`risk_${riskSource}_title`);
  document.getElementById('riskDesc').textContent  = t(`risk_${riskSource}_desc`);
  document.getElementById('riskTmax').textContent  = `${tMaxShow.toFixed(1)} °C`;

  // Extreme cases summary line in banner
  const extEl = document.getElementById('riskExtremes');
  if (extEl) {
    const chaudSeries = (adaptive && data.adaptive_chaud) ? data.adaptive_chaud : data.ferme_chaud;
    const froidSeries = (adaptive && data.adaptive_froid) ? data.adaptive_froid : data.ferme_froid;
    const stratLabel  = adaptive ? t('adaptive_label') : t('closed_label');

    if (chaudSeries || froidSeries) {
      const RISK_COLOR = { ok: '#30d158', caution: '#ff9f0a', warning: '#ff9f0a', danger: '#ff453a' };
      const RISK_ICON  = { ok: '✓', caution: '↑', warning: '⚠', danger: '✗' };
      const parts = [];
      if (chaudSeries) {
        const tm = Math.max(...chaudSeries.T_C);
        const rk = classifyRisk(tm);
        parts.push(`${t('extreme_hot')} : <span style="color:${RISK_COLOR[rk]};font-weight:600">${RISK_ICON[rk]} ${tm.toFixed(1)} °C</span>`);
      }
      if (froidSeries) {
        const tm = Math.max(...froidSeries.T_C);
        const rk = classifyRisk(tm);
        parts.push(`${t('extreme_cold')} : <span style="color:${RISK_COLOR[rk]};font-weight:600">${RISK_ICON[rk]} ${tm.toFixed(1)} °C</span>`);
      }
      extEl.innerHTML = `${t('extreme_cases')} (${stratLabel}) — ${parts.join('  ·  ')}`;
      extEl.style.display = '';
    } else {
      extEl.style.display = 'none';
    }
  }

  // Adaptive strategy note — explain what level of intervention is actually needed
  const adaptNoteEl = document.getElementById('adaptiveNotNeeded');
  if (adaptNoteEl && adaptive) {
    const mistingCount = (adaptive.misting_events || []).length;
    if (data.adaptive_not_needed) {
      adaptNoteEl.textContent = t('adaptive_not_needed_msg');
      adaptNoteEl.style.color = '#30d158';
    } else if (mistingCount === 0) {
      adaptNoteEl.textContent = t('windows_only_msg');
      adaptNoteEl.style.color = '#30d158';
    } else {
      const wUsed = adaptive.water_used_L != null ? ` ${adaptive.water_used_L.toFixed(1)} ${t('misting_water_used')}` : '';
      adaptNoteEl.textContent = `${t('misting_needed_msg')} ${mistingCount} ${t('misting_interventions')}${wUsed}`;
      adaptNoteEl.style.color = '#ff9f0a';
    }
    adaptNoteEl.style.display = '';
  } else if (adaptNoteEl) {
    adaptNoteEl.style.display = 'none';
  }

  setTimeout(() => {
    banner.classList.add('visible');
    document.getElementById('graphCard').classList.add('visible');
    document.getElementById('weatherCard').classList.add('visible');
  }, 50);

  // ── Graphe principal ───────────────────────────────────────────
  const ferme  = data.ferme;
  const ouvert = data.ouvert;

  const colorFerme    = risk === 'ok' ? '#30d158' : '#ff453a';
  const colorOuvert   = '#2997ff';
  const colorAdaptive = '#ffd60a';

  const traces = [];

  traces.push({
    x: ferme.t_h, y: ferme.T_C,
    type: 'scatter', mode: 'lines',
    name: currentLang === 'fr' ? 'Fenêtres fermées' : 'Windows closed',
    line: { color: colorFerme, width: 2 },
    hovertemplate: '%{y:.2f} °C<extra>Fermé</extra>',
  });

  traces.push(makeTranspGradientTrace(ferme.t_h, ferme.T_C, 1.0, '_grad_ferme'));

  if (ouvert) {
    traces.push({
      x: ouvert.t_h, y: ouvert.T_C,
      type: 'scatter', mode: 'lines',
      name: currentLang === 'fr' ? 'Fenêtres ouvertes' : 'Windows open',
      line: { color: colorOuvert, width: 1.5, dash: 'dash' },
      hovertemplate: '%{y:.2f} °C<extra>Ouvert</extra>',
    });
  }

  if (adaptive) {
    traces.push({
      x: adaptive.series.t_h, y: adaptive.series.T_C,
      type: 'scatter', mode: 'lines',
      name: t('adaptive_strategy'),
      line: { color: colorAdaptive, width: 2.5 },
      hovertemplate: '%{y:.2f} °C<extra>' + t('adaptive_label') + '</extra>',
    });

    traces.push(makeTranspGradientTrace(adaptive.series.t_h, adaptive.series.T_C, 1.0, '_grad_adaptive'));
  }

  // ── Cas extrêmes — enveloppe chaud/froid (tracés en pointillés, moins saturés) ──
  if (data.ferme_chaud) {
    traces.push({
      x: data.ferme_chaud.t_h, y: data.ferme_chaud.T_C,
      type: 'scatter', mode: 'lines',
      name: `${t('closed_label')} — ${t('extreme_hot')}`,
      line: { color: risk === 'ok' ? 'rgba(48,209,88,0.45)' : 'rgba(255,69,58,0.45)', width: 1, dash: 'dot' },
      hovertemplate: '%{y:.2f} °C<extra>' + t('closed_label') + ' ' + t('extreme_hot') + '</extra>',
    });
    traces.push(makeTranspGradientTrace(data.ferme_chaud.t_h, data.ferme_chaud.T_C, 0.1, '_grad_ferme_chaud'));
  }
  if (data.ferme_froid) {
    traces.push({
      x: data.ferme_froid.t_h, y: data.ferme_froid.T_C,
      type: 'scatter', mode: 'lines',
      name: `${t('closed_label')} — ${t('extreme_cold')}`,
      line: { color: risk === 'ok' ? 'rgba(48,209,88,0.25)' : 'rgba(255,69,58,0.25)', width: 1, dash: 'dot' },
      hovertemplate: '%{y:.2f} °C<extra>' + t('closed_label') + ' ' + t('extreme_cold') + '</extra>',
    });
    traces.push(makeTranspGradientTrace(data.ferme_froid.t_h, data.ferme_froid.T_C, 0.1, '_grad_ferme_froid'));
  }
  if (data.adaptive_chaud && adaptive) {
    traces.push({
      x: data.adaptive_chaud.t_h, y: data.adaptive_chaud.T_C,
      type: 'scatter', mode: 'lines',
      name: `${t('adaptive_label')} — ${t('extreme_hot')}`,
      line: { color: 'rgba(255,214,10,0.45)', width: 1.5, dash: 'dot' },
      hovertemplate: '%{y:.2f} °C<extra>' + t('adaptive_label') + ' ' + t('extreme_hot') + '</extra>',
    });
    traces.push(makeTranspGradientTrace(data.adaptive_chaud.t_h, data.adaptive_chaud.T_C, 0.1, '_grad_adap_chaud'));
  }
  if (data.adaptive_froid && adaptive) {
    traces.push({
      x: data.adaptive_froid.t_h, y: data.adaptive_froid.T_C,
      type: 'scatter', mode: 'lines',
      name: `${t('adaptive_label')} — ${t('extreme_cold')}`,
      line: { color: 'rgba(255,214,10,0.25)', width: 1.5, dash: 'dot' },
      hovertemplate: '%{y:.2f} °C<extra>' + t('adaptive_label') + ' ' + t('extreme_cold') + '</extra>',
    });
    traces.push(makeTranspGradientTrace(data.adaptive_froid.t_h, data.adaptive_froid.T_C, 0.1, '_grad_adap_froid'));
  }

  // ── Température extérieure (axe Y secondaire, droite) ────────────────────────
  const wData = data.weather;
  traces.push({
    x: wData.hours, y: wData.temps_C,
    type: 'scatter', mode: 'lines',
    name: t('t_ext_label'),
    yaxis: 'y2',
    line: { color: 'rgba(90,200,250,0.55)', width: 1.5, dash: 'dashdot' },
    hovertemplate: '%{y:.1f} °C<extra>T ext.</extra>',
  });

  // Regime bands from adaptive strategy
  const regimeBands = adaptive ? buildRegimeBands(adaptive.regime_events, routeDurationH) : [];
  const REGIME_FILL = { ouvert: 'rgba(255,159,10,0.09)', brumisation: 'rgba(41,151,255,0.14)' };

  const layout = {
    paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
    margin: { l: 50, r: 70, t: 16, b: 40 },
    font: { color: '#86868b', family: '-apple-system,sans-serif', size: 11 },
    xaxis: {
      title: { text: t('axis_time'), font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.05)', tickcolor: 'rgba(255,255,255,0.1)',
    },
    yaxis: {
      title: { text: t('axis_temp_animal'), font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.05)', tickcolor: 'rgba(255,255,255,0.1)',
    },
    yaxis2: {
      title: { text: t('axis_temp_ext'), font: { size: 10, color: 'rgba(90,200,250,0.7)' } },
      overlaying: 'y', side: 'right',
      gridcolor: 'transparent', tickcolor: 'rgba(255,255,255,0.06)',
      tickfont: { color: 'rgba(90,200,250,0.6)', size: 10 },
    },
    shapes: [
      { type: 'line', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 39.5, y1: 39.5,
        line: { color: 'rgba(255,69,58,0.5)', width: 1, dash: 'dash' } },
      { type: 'line', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 38.5, y1: 38.5,
        line: { color: 'rgba(48,209,88,0.4)', width: 1, dash: 'dot' } },
      { type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 38.0, y1: 39.5,
        fillcolor: 'rgba(48,209,88,0.04)', line: { width: 0 } },
      // Stop bands
      ...(data.stops || []).map(s => ({
        type: 'rect', xref: 'x', yref: 'paper',
        x0: s.t_arrive_h, x1: s.t_depart_h, y0: 0, y1: 1,
        fillcolor: 'rgba(255,255,255,0.05)', line: { width: 1, color: 'rgba(255,255,255,0.1)', dash: 'dot' },
        layer: 'below',
      })),
      // Adaptive regime bands
      ...regimeBands.map(b => ({
        type: 'rect', xref: 'x', yref: 'paper',
        x0: b.start, x1: b.end, y0: 0, y1: 1,
        fillcolor: REGIME_FILL[b.mode] || 'rgba(255,255,255,0.04)',
        line: { width: 0 }, layer: 'below',
      })),
    ],
    annotations: [
      { xref: 'paper', yref: 'y', x: 1.01, y: 39.5, text: t('axis_limit'), showarrow: false, font: { color: 'rgba(255,69,58,0.7)', size: 10 } },
      { xref: 'paper', yref: 'y', x: 1.01, y: 38.5, text: t('axis_normal'), showarrow: false, font: { color: 'rgba(48,209,88,0.7)', size: 10 } },
      ...(data.stops || []).map(s => ({
        xref: 'x', yref: 'paper',
        x: (s.t_arrive_h + s.t_depart_h) / 2, y: 0.97,
        text: `${t('stop_chart')} ${s.duration_h}h`, showarrow: false,
        font: { color: 'rgba(255,255,255,0.35)', size: 9 },
      })),
    ],
    hovermode: 'x unified',
    hoverlabel: {
      bgcolor: '#1c1c1e',
      bordercolor: 'rgba(255,255,255,0.12)',
      font: { color: '#e6edf3', size: 11, family: '-apple-system,sans-serif' },
    },
    legend: { bgcolor: 'rgba(0,0,0,0)', bordercolor: 'rgba(255,255,255,0.1)', borderwidth: 1,
              font: { color: '#e6edf3', size: 10 }, x: 0, y: 1, yanchor: 'top' },
  };

  Plotly.react('plotly-main', traces, layout, { responsive: true, displaylogo: false, displayModeBar: false, scrollZoom: false });
  buildCurveToggles(traces);

  // ── Bilan eau — affiché sous le graphe si stratégie adaptative + données eau ──
  const waterCard = document.getElementById('waterCard');
  if (waterCard) waterCard.remove();  // remove previous if any
  if (adaptive && adaptive.water_used_L !== undefined && adaptive.available_water_L !== null) {
    const wUsed  = adaptive.water_used_L.toFixed(1);
    const wAvail = adaptive.available_water_L.toFixed(0);
    const wLeft  = adaptive.water_remaining_L !== null ? adaptive.water_remaining_L.toFixed(1) : '—';
    const pct    = adaptive.available_water_L > 0
      ? Math.min(100, Math.round(adaptive.water_used_L / adaptive.available_water_L * 100)) : 0;
    const barColor = pct > 80 ? '#ff453a' : pct > 50 ? '#ff9f0a' : '#30d158';
    const card = document.createElement('div');
    card.id = 'waterCard';
    card.style.cssText = 'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 18px;margin-top:12px';
    card.innerHTML = `
      <div style="font-size:0.78rem;color:#86868b;margin-bottom:8px">${t('water_reserve_label')}</div>
      <div style="display:flex;align-items:center;gap:14px">
        <div style="flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:6px;overflow:hidden">
          <div style="width:${pct}%;height:100%;background:${barColor};border-radius:4px;transition:width .4s"></div>
        </div>
        <div style="font-size:0.82rem;color:#e6edf3;white-space:nowrap">${wUsed} / ${wAvail} L ${t('water_used_of')}</div>
      </div>
      <div style="font-size:0.72rem;color:#86868b;margin-top:6px">${wLeft} L ${t('water_remaining')}</div>`;
    document.getElementById('graphCard').insertAdjacentElement('afterend', card);
  }

  // ── Graphe réservoir + message eau — uniquement si brumisation active ──────
  const prevWCC = document.getElementById('waterChartCard');
  if (prevWCC) prevWCC.remove();

  if (adaptive && adaptive.misting_events && adaptive.misting_events.length > 0
      && adaptive.available_water_L !== null) {

    // Courbe en escalier du niveau du réservoir
    const xData = [0];
    const yData = [adaptive.available_water_L];
    let lvl = adaptive.available_water_L;
    for (const me of adaptive.misting_events) {
      xData.push(me.t_start_h);
      lvl = Math.max(0, lvl - me.water_L);
      yData.push(lvl);
    }
    xData.push(routeDurationH);
    yData.push(lvl);

    const isShortage = (adaptive.water_shortfall_L || 0) > 0.01;
    const shortfall  = (adaptive.water_shortfall_L || 0).toFixed(1);
    const remaining  = (adaptive.water_remaining_L || 0).toFixed(1);

    const msgHtml = isShortage
      ? `<div style="padding:10px 14px;border-radius:10px;background:rgba(255,69,58,0.1);border:1px solid rgba(255,69,58,0.22);color:#ff453a;font-size:0.82rem;font-weight:500;margin-bottom:10px">
           ${t('water_shortage')} <strong>${shortfall} L</strong> ${t('water_shortage_suf')}
         </div>`
      : `<div style="padding:10px 14px;border-radius:10px;background:rgba(48,209,88,0.07);border:1px solid rgba(48,209,88,0.18);color:#30d158;font-size:0.82rem;font-weight:500;margin-bottom:10px">
           ${t('water_ok')} <strong>${remaining} L</strong> ${t('water_ok_suf')}
         </div>`;

    const wcc = document.createElement('div');
    wcc.id = 'waterChartCard';
    wcc.style.cssText = 'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 18px;margin-top:12px';
    wcc.innerHTML = `
      <div style="font-size:0.78rem;color:#86868b;margin-bottom:10px">${t('water_tank_title')}</div>
      ${msgHtml}
      <div id="plotly-reservoir" style="height:160px"></div>`;

    const anchor = document.getElementById('waterCard') || document.getElementById('graphCard');
    anchor.insertAdjacentElement('afterend', wcc);

    const lineColor = isShortage ? '#ff453a' : '#2997ff';
    const fillColor = isShortage ? 'rgba(255,69,58,0.08)' : 'rgba(41,151,255,0.1)';
    Plotly.react('plotly-reservoir',
      [{
        x: xData, y: yData,
        type: 'scatter', mode: 'lines',
        fill: 'tozeroy', fillcolor: fillColor,
        line: { color: lineColor, width: 2, shape: 'hv' },
        hovertemplate: '%{y:.1f} L<extra>Réserve</extra>',
      }],
      {
        paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
        margin: { l: 46, r: 16, t: 4, b: 34 },
        font: { color: '#86868b', family: '-apple-system,sans-serif', size: 10 },
        xaxis: { title: { text: t('axis_time'), font: { size: 10 } },
                 gridcolor: 'rgba(255,255,255,0.05)', tickcolor: 'rgba(255,255,255,0.08)' },
        yaxis: { title: { text: 'L', font: { size: 10 } }, rangemode: 'nonnegative',
                 gridcolor: 'rgba(255,255,255,0.05)', tickcolor: 'rgba(255,255,255,0.08)' },
        shapes: [{ type: 'line', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: 0, y1: 0,
                   line: { color: 'rgba(255,69,58,0.35)', width: 1, dash: 'dash' } }],
        hovermode: 'x unified',
        hoverlabel: { bgcolor: '#1c1c1e', bordercolor: 'rgba(255,255,255,0.12)',
                      font: { color: '#e6edf3', size: 11 } },
        showlegend: false,
      },
      { responsive: true, displaylogo: false, displayModeBar: false }
    );
  }

  // Eau illimitée : afficher uniquement la quantité totale utilisée
  const prevUnlimCard = document.getElementById('waterUnlimitedCard');
  if (prevUnlimCard) prevUnlimCard.remove();
  if (adaptive && adaptive.available_water_L === null && adaptive.water_used_L > 0) {
    const card = document.createElement('div');
    card.id = 'waterUnlimitedCard';
    card.style.cssText = 'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:12px 18px;margin-top:12px;font-size:0.82rem;color:#86868b';
    card.innerHTML = `${t('water_used_unlimited')} <strong style="color:#e6edf3">${adaptive.water_used_L.toFixed(1)} L</strong>`;
    const anchor = document.getElementById('graphCard');
    if (anchor) anchor.insertAdjacentElement('afterend', card);
  }

  // Event log
  renderEventLog(adaptive);

  // Scroll right panel to show results (below the map)
  setTimeout(() => {
    const rp  = document.getElementById('rightPanel');
    const res = document.getElementById('results');
    if (rp && res) rp.scrollTo({ top: res.offsetTop, behavior: 'smooth' });
  }, 150);


  // Météo — données horaires réelles (Open-Meteo) ou fallback
  const w = data.weather;
  const avgTemp = (w.temps_C.reduce((a,b)=>a+b,0) / w.temps_C.length).toFixed(1);
  const avgRH   = (w.rh_pct.reduce((a,b)=>a+b,0)  / w.rh_pct.length).toFixed(0);
  const avgVent = (w.wind_kmh.reduce((a,b)=>a+b,0) / w.wind_kmh.length).toFixed(1);

  document.getElementById('wStatTemp').textContent = `${avgTemp} °C`;
  document.getElementById('wStatRH').textContent   = `${avgRH} %`;
  document.getElementById('wStatVent').textContent = `${avgVent} km/h`;

  // Source pill
  const pill = document.getElementById('weatherSourcePill');
  if (pill) {
    pill.style.display = '';
    pill.textContent   = w.source === 'open-meteo' ? `Open-Meteo (${currentLang === 'fr' ? 'réel' : 'live'})` : (currentLang === 'fr' ? 'Données estimées' : 'Estimated data');
    pill.style.color   = w.source === 'open-meteo' ? '#30d158' : '#ff9f0a';
    pill.style.background    = w.source === 'open-meteo' ? 'rgba(48,209,88,0.1)' : 'rgba(255,159,10,0.1)';
    pill.style.borderColor   = w.source === 'open-meteo' ? 'rgba(48,209,88,0.3)' : 'rgba(255,159,10,0.3)';
  }

  // Graphe météo — 3 courbes : T, humidité, vent
  const truckSpeed = data.avg_speed_kmh;

  const tickLabels = w.hour_labels;
  // Show only every Nth label to avoid crowding
  const step = Math.max(1, Math.ceil(w.hours.length / 12));
  const tickVals = w.hours.filter((_, i) => i % step === 0);
  const tickText = tickLabels.filter((_, i) => i % step === 0);

  const traceT = {
    x: w.hours, y: w.temps_C,
    type: 'scatter', mode: 'lines+markers',
    name: 'T ext. (°C)',
    line: { color: '#ff9f0a', width: 1.5 }, marker: { size: 3 },
    hovertemplate: '%{y:.1f} °C<extra>T ext.</extra>',
  };
  const traceH = {
    x: w.hours, y: w.rh_pct,
    type: 'scatter', mode: 'lines+markers',
    name: 'Humidité (%)',
    yaxis: 'y3',
    line: { color: '#5e5ce6', width: 1.5, dash: 'dot' }, marker: { size: 3 },
    hovertemplate: '%{y:.0f}%<extra>Humidité</extra>',
  };
  const traceV = {
    x: w.hours, y: w.wind_kmh,
    type: 'scatter', mode: 'lines+markers',
    name: 'Vent ambiant (km/h)',
    yaxis: 'y2',
    line: { color: '#2997ff', width: 1.5, dash: 'dot' }, marker: { size: 3 },
    hovertemplate: '%{y:.1f} km/h<extra>Vent ambiant</extra>',
  };
  const traceS = {
    x: w.hours, y: w.truck_speed_kmh,
    type: 'scatter', mode: 'lines',
    name: 'Vitesse camion (km/h)',
    yaxis: 'y2',
    line: { color: '#30d158', width: 2 },
    hovertemplate: '%{y:.0f} km/h<extra>Camion</extra>',
  };

  const wLayout = {
    paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
    margin: { l: 45, r: 80, t: 10, b: 35 },
    font: { color: '#86868b', family: '-apple-system,sans-serif', size: 10 },
    xaxis: {
      title: { text: 'Heure de départ + h', font: { size: 10 } },
      tickvals: tickVals, ticktext: tickText,
      gridcolor: 'rgba(255,255,255,0.04)',
    },
    yaxis: {
      title: { text: '°C', font: { size: 10 }, standoff: 4 },
      gridcolor: 'rgba(255,255,255,0.04)',
    },
    yaxis2: {
      title: { text: 'km/h', font: { size: 10 }, standoff: 4 },
      overlaying: 'y', side: 'right',
      gridcolor: 'rgba(255,255,255,0)', showgrid: false,
    },
    yaxis3: {
      title: { text: '%', font: { size: 10 }, standoff: 4 },
      overlaying: 'y', side: 'right',
      anchor: 'free', position: 1.0,
      range: [0, 100],
      gridcolor: 'rgba(255,255,255,0)', showgrid: false,
      tickfont: { color: '#5e5ce6', size: 9 },
    },
    hovermode: 'x unified',
    hoverlabel: {
      bgcolor: '#1c1c1e',
      bordercolor: 'rgba(255,255,255,0.12)',
      font: { color: '#e6edf3', size: 11, family: '-apple-system,sans-serif' },
    },
    legend: { bgcolor: 'rgba(0,0,0,0)', font: { color: '#e6edf3', size: 9 },
              orientation: 'h', x: 0, y: -0.25 },
  };

  Plotly.react('plotly-weather', [traceT, traceH, traceV, traceS], wLayout, { responsive: true, displaylogo: false, displayModeBar: false, scrollZoom: false });
}

// ── Alert ─────────────────────────────────────────────────────────────────────
function showAlert(msg) {
  const el = document.getElementById('alertError');
  el.textContent = msg;
  el.style.display = 'block';
}

function clearAlert() {
  const el = document.getElementById('alertError');
  el.textContent = '';
  el.style.display = 'none';
}

// ── Simulation loading animation (Mix A+C: orb + circuit lines) ──────────────
let _simAnimId = null, _simStatusTimer = null;

function startSimAnimation() {
  const overlay = document.getElementById('simLoading');
  overlay.classList.add('active');

  const canvas  = document.getElementById('simLoadCanvas');
  const ctx     = canvas.getContext('2d');
  const W = canvas.width  = overlay.clientWidth  || window.innerWidth;
  const H = canvas.height = overlay.clientHeight || window.innerHeight;
  const cx = W / 2, cy = H / 2;

  // ── Circuit lines (Option C): L-shaped paths from edges → center ──
  const NCIRCUIT = 18;
  const circuits = [];
  for (let i = 0; i < NCIRCUIT; i++) {
    const side = i % 4;
    let sx, sy;
    if      (side === 0) { sx = (0.15 + Math.random() * 0.7) * W; sy = 0; }
    else if (side === 1) { sx = W;  sy = (0.15 + Math.random() * 0.7) * H; }
    else if (side === 2) { sx = (0.15 + Math.random() * 0.7) * W; sy = H; }
    else                 { sx = 0;  sy = (0.15 + Math.random() * 0.7) * H; }

    // L-shaped waypoints: edge → elbow → center
    const elbow = Math.random() > 0.5
      ? { x: cx, y: sy }    // horizontal first
      : { x: sx, y: cy };   // vertical first

    const isGreen  = Math.random() > 0.5;
    const baseAlpha = 0.35 + Math.random() * 0.3;
    circuits.push({
      pts:   [{ x: sx, y: sy }, elbow, { x: cx, y: cy }],
      prog:  Math.random() * 0.3,           // stagger start
      speed: 0.0015 + Math.random() * 0.002,
      color: isGreen ? '#4ADE80' : '#29ADFF',
      alpha: baseAlpha,
      width: 0.7 + Math.random() * 0.8,
      totalLen: 0,
    });
    const c = circuits[circuits.length - 1];
    for (let k = 1; k < c.pts.length; k++) {
      const dx = c.pts[k].x - c.pts[k-1].x;
      const dy = c.pts[k].y - c.pts[k-1].y;
      c.totalLen += Math.sqrt(dx * dx + dy * dy);
    }
  }

  // ── Particles: floating data nodes (Option A aesthetic) ──
  const NPARTS = 55;
  const parts = Array.from({ length: NPARTS }, () => ({
    x: Math.random() * W, y: Math.random() * H,
    vx: (Math.random() - 0.5) * 0.25,
    vy: -Math.random() * 0.4 - 0.05,
    r: 1 + Math.random() * 1.5,
    color: Math.random() > 0.5 ? '#29ADFF' : '#4ADE80',
    life: Math.random(),
  }));

  function drawCircuit(c) {
    const drawLen = c.prog * c.totalLen;
    let rem = drawLen, started = false;
    ctx.save();
    ctx.globalAlpha = c.alpha;
    ctx.strokeStyle = c.color;
    ctx.lineWidth   = c.width;
    ctx.shadowBlur  = 6; ctx.shadowColor = c.color;
    ctx.beginPath();
    for (let k = 1; k < c.pts.length; k++) {
      const p0 = c.pts[k - 1], p1 = c.pts[k];
      const dx = p1.x - p0.x, dy = p1.y - p0.y;
      const segLen = Math.sqrt(dx * dx + dy * dy);
      if (rem <= 0) break;
      if (!started) { ctx.moveTo(p0.x, p0.y); started = true; }
      if (rem >= segLen) {
        ctx.lineTo(p1.x, p1.y); rem -= segLen;
      } else {
        const t = rem / segLen;
        ctx.lineTo(p0.x + dx * t, p0.y + dy * t);

        // Glowing head dot
        const hx = p0.x + dx * t, hy = p0.y + dy * t;
        ctx.stroke(); ctx.beginPath();
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 14;
        ctx.arc(hx, hy, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = c.color; ctx.fill();
        break;
      }
    }
    ctx.stroke();
    ctx.restore();
    c.prog = Math.min(1, c.prog + c.speed);
    if (c.prog >= 1) c.prog = 0;   // loop
  }

  function frame() {
    _simAnimId = requestAnimationFrame(frame);
    ctx.clearRect(0, 0, W, H);

    // Faint hex grid
    ctx.save();
    ctx.strokeStyle = 'rgba(41,173,255,0.04)';
    ctx.lineWidth = 0.5;
    const gs = 48;
    for (let x = 0; x < W; x += gs) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = 0; y < H; y += gs) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    ctx.restore();

    // Circuit lines converging to center
    circuits.forEach(drawCircuit);

    // Particle network
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      p.x += p.vx; p.y += p.vy; p.life += 0.004;
      if (p.y < -10 || p.life > 1) {
        p.x = Math.random() * W; p.y = H + 5; p.life = 0;
      }
      const a = Math.sin(p.life * Math.PI) * 0.55;
      ctx.save();
      ctx.globalAlpha = a;
      ctx.fillStyle = p.color;
      ctx.shadowBlur = 4; ctx.shadowColor = p.color;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
      ctx.restore();

      // Connect nearby particles
      for (let j = i + 1; j < parts.length; j++) {
        const q = parts[j];
        const dx = p.x - q.x, dy = p.y - q.y;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < 90) {
          ctx.save();
          ctx.globalAlpha = 0.1 * (1 - d / 90);
          ctx.strokeStyle = '#29ADFF'; ctx.lineWidth = 0.4;
          ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke();
          ctx.restore();
        }
      }
    }
  }
  frame();

  // Cycling status messages
  const msgs = [
    'Récupération météo…',
    'Calcul thermique RK4…',
    'Simulation adaptative…',
    'Analyse des risques…',
    'Génération du rapport…',
  ];
  let mi = 0;
  const statusEl = document.getElementById('simLoadStatus');
  _simStatusTimer = setInterval(() => {
    mi = (mi + 1) % msgs.length;
    if (statusEl) { statusEl.style.opacity = 0; setTimeout(() => { statusEl.textContent = msgs[mi]; statusEl.style.opacity = 1; }, 200); }
  }, 1400);
}

function stopSimAnimation() {
  if (_simAnimId)      { cancelAnimationFrame(_simAnimId); _simAnimId = null; }
  if (_simStatusTimer) { clearInterval(_simStatusTimer); _simStatusTimer = null; }
  const overlay = document.getElementById('simLoading');
  if (overlay) overlay.classList.remove('active');
}

// ── Animated canvas background ────────────────────────────────────────────────
function initBackground() {
  const canvas = document.getElementById('bg');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // Orbs: normalized positions, RGB, radius, velocity
  const orbs = [
    { x: 0.18, y: 0.28, r: 0.60, rgb: [12,  86, 178],  vx:  0.00022, vy:  0.00015 },
    { x: 0.82, y: 0.62, r: 0.54, rgb: [68,  48, 198],  vx: -0.00018, vy:  0.00023 },
    { x: 0.54, y: 0.84, r: 0.45, rgb: [0,   76, 108],  vx:  0.00014, vy: -0.00020 },
    { x: 0.74, y: 0.11, r: 0.38, rgb: [14, 118,  88],  vx: -0.00026, vy:  0.00010 },
    { x: 0.07, y: 0.72, r: 0.32, rgb: [84,  38, 168],  vx:  0.00019, vy: -0.00024 },
  ];

  let scrollY = 0;
  window.addEventListener('scroll', () => { scrollY = window.scrollY; }, { passive: true });

  function frame(ts) {
    ctx.fillStyle = '#050510';
    ctx.fillRect(0, 0, W, H);

    const scrollProg = Math.min(1, scrollY / Math.max(1, window.innerHeight));

    orbs.forEach((o, i) => {
      // Sinusoidal drift + base velocity
      o.x += o.vx + Math.sin(ts * 0.00038 + i * 1.3) * 0.000075;
      o.y += o.vy + Math.cos(ts * 0.00031 + i * 0.9) * 0.000075;

      // Soft bounce at edges
      if (o.x < -0.14) { o.x = -0.14; o.vx =  Math.abs(o.vx); }
      if (o.x >  1.14) { o.x =  1.14; o.vx = -Math.abs(o.vx); }
      if (o.y < -0.14) { o.y = -0.14; o.vy =  Math.abs(o.vy); }
      if (o.y >  1.14) { o.y =  1.14; o.vy = -Math.abs(o.vy); }

      // Orbs drift upward on scroll, giving a parallax-like shift
      const px  = o.x * W;
      const py  = (o.y - scrollProg * 0.22) * H;
      const rad = o.r * Math.min(W, H) * 0.76;

      // Slightly reduce opacity as user scrolls into the app
      const alpha = 0.175 - scrollProg * 0.04;

      const [r, g, b] = o.rgb;
      const grad = ctx.createRadialGradient(px, py, 0, px, py, rad);
      grad.addColorStop(0,    `rgba(${r},${g},${b},${alpha})`);
      grad.addColorStop(0.42, `rgba(${r},${g},${b},${alpha * 0.28})`);
      grad.addColorStop(1,    'rgba(0,0,0,0)');

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(px, py, rad, 0, Math.PI * 2);
      ctx.fill();
    });

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
}

// ── Enter app (unlock scroll + scroll to app panel) ───────────────────────────
function enterApp() {
  document.body.classList.remove('locked');
  requestAnimationFrame(() => {
    document.getElementById('appScreen').scrollIntoView({ behavior: 'smooth' });
    // Leaflet needs invalidateSize when its container becomes truly visible
    setTimeout(() => { if (map) map.invalidateSize(); }, 700);
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(currentTheme);
  initBackground();
  initMap();
  setupCitySearch('city_depart', 'sug_depart', onFromSelected);
  setupCitySearch('city_arrivee', 'sug_arrivee', onToSelected);
  setLang('fr');
  updateBreedNote();
});
