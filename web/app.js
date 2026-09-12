// ChildGuard AI - Web Command Center & Live Simulator Controller

// Coordinates Matching PostGIS seed.sql
const GEOFENCES = {
  school: [
    [28.6130, 77.2090],
    [28.6130, 77.2150],
    [28.6180, 77.2150],
    [28.6180, 77.2090]
  ],
  home: [
    [28.6200, 77.2200],
    [28.6200, 77.2260],
    [28.6250, 77.2260],
    [28.6250, 77.2200]
  ],
  danger: [
    [28.6100, 77.2300],
    [28.6100, 77.2380],
    [28.6150, 77.2380],
    [28.6150, 77.2300]
  ]
};

let map;
let childMarker;
let threatCount = 0;

// Initialize Leaflet Map
function initMap() {
  const defaultPos = [28.6145, 77.2120];

  map = L.map('map', {
    zoomControl: true,
    attributionControl: false
  }).setView(defaultPos, 15);

  // CartoDB Dark Matter Tiles for sleek dark aesthetics
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    subdomains: 'abcd'
  }).addTo(map);

  // Render 1: School Safe Zone
  L.polygon(GEOFENCES.school, {
    color: '#10B981',
    weight: 2,
    fillColor: '#10B981',
    fillOpacity: 0.18
  }).addTo(map).bindTooltip('🏫 Delhi Public School (Safe Zone)', { permanent: true, direction: 'center', className: 'map-label' });

  // Render 2: Home Safe Zone
  L.polygon(GEOFENCES.home, {
    color: '#3B82F6',
    weight: 2,
    fillColor: '#3B82F6',
    fillOpacity: 0.18
  }).addTo(map).bindTooltip('🏡 Home Neighborhood (Safe Zone)', { permanent: true, direction: 'center', className: 'map-label' });

  // Render 3: Industrial Danger Zone
  L.polygon(GEOFENCES.danger, {
    color: '#EF4444',
    weight: 2.5,
    dashArray: '6, 6',
    fillColor: '#EF4444',
    fillOpacity: 0.25
  }).addTo(map).bindTooltip('⚠️ Industrial Construction Site (Danger Zone)', { permanent: true, direction: 'center', className: 'map-label danger' });

  // Custom Child Marker with Pulse
  const childIcon = L.divIcon({
    className: 'child-marker-container',
    html: `
      <div class="child-pulse-ring"></div>
      <div class="child-marker-icon">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#FFF" stroke-width="2.5">
          <circle cx="12" cy="7" r="4"/>
          <path d="M5.5 21a8.38 8.38 0 0 1 13 0"/>
        </svg>
      </div>
      <div class="child-marker-label">Aarav</div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20]
  });

  childMarker = L.marker(defaultPos, { icon: childIcon }).addTo(map);
}

// Update Telemetry Displays
function updateTelemetry(lat, lon, speed, battery = '84%') {
  document.getElementById('dispCoords').innerText = `${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E`;
  document.getElementById('dispSpeed').innerText = `${speed.toFixed(1)} m/s`;
  document.getElementById('dispBattery').innerText = battery;

  // Move map marker smoothly
  childMarker.setLatLng([lat, lon]);
  map.panTo([lat, lon]);
}

// Add Threat Card to Feed
function pushThreatAlert(type, severity, snippet, trigger) {
  threatCount++;
  document.getElementById('threatCount').innerText = `${threatCount} Alerts`;

  const emptyState = document.getElementById('emptyState');
  if (emptyState) {
    emptyState.style.display = 'none';
  }

  const list = document.getElementById('threatsList');
  const card = document.createElement('div');
  const isCritical = severity === 'CRITICAL';
  card.className = `threat-item ${isCritical ? 'critical' : 'high'}`;

  const now = new Date();
  const timeStr = now.toTimeString().split(' ')[0];

  card.innerHTML = `
    <div class="threat-icon">${isCritical ? '🚨' : '⚠️'}</div>
    <div class="threat-body">
      <div class="threat-top">
        <span class="threat-type">${type}</span>
        <span class="severity-pill ${severity.toLowerCase()}">${severity}</span>
      </div>
      <div class="threat-snippet">${snippet}</div>
      <div class="threat-time">Trigger: ${trigger} • ${timeStr}</div>
    </div>
  `;

  list.prepend(card);
}

// Attach Interactive Simulation Handlers
function setupEventListeners() {
  // 1. Walk Inside School (Safe)
  document.getElementById('simSchool').addEventListener('click', () => {
    updateTelemetry(28.6145, 77.2120, 0.4);
  });

  // 2. Exit Safe Zone
  document.getElementById('simExit').addEventListener('click', () => {
    updateTelemetry(28.6190, 77.2180, 1.8);
    pushThreatAlert(
      'SAFE_ZONE_EXIT',
      'HIGH',
      'Child is outside designated safe zones (school and home perimeters).',
      'OutsideAllSafeZones == TRUE'
    );
  });

  // 3. Enter Danger Zone
  document.getElementById('simDanger').addEventListener('click', () => {
    updateTelemetry(28.6120, 77.2340, 2.3);
    pushThreatAlert(
      'DANGER_ZONE_BREACH',
      'CRITICAL',
      'Child entered restricted danger zone: Industrial Construction Site!',
      'ST_Contains(DangerZone, Location) == TRUE'
    );
  });

  // 4. Simulate Predator Chat
  document.getElementById('simChat').addEventListener('click', () => {
    pushThreatAlert(
      'CHAT_SECURITY_ALARM',
      'HIGH',
      'WhatsApp: "Hey, meet alone at the secret place after class, don\'t tell parents."',
      'Keyword match: [meet alone, secret place, don\'t tell]'
    );
  });

  // 5. Trigger Hardware SOS Sequence
  document.getElementById('simSos').addEventListener('click', () => {
    updateTelemetry(28.6145, 77.2120, 0.0, '78%');
    pushThreatAlert(
      'EMERGENCY_SOS_ALARM',
      'CRITICAL',
      'EMERGENCY: Silent panic signal triggered via physical button triple-tap!',
      'HARDWARE_TRIPLE_VOLUME_TAP'
    );
  });

  // Remote Lock Modal
  const lockModal = document.getElementById('lockModal');
  document.getElementById('btnRemoteLock').addEventListener('click', () => {
    lockModal.style.display = 'flex';
  });

  document.getElementById('btnDismissLock').addEventListener('click', () => {
    lockModal.style.display = 'none';
  });
}

// Bootstrap on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initMap();
  setupEventListeners();
});
