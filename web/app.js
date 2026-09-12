// ChildGuard AI - Official Showcase & Interactive Simulator Engine

// Coordinates Matching PostGIS seed.sql & E2E Simulation
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
let isDeviceLocked = false;

// 1. Initialize Leaflet Spatial Engine
function initMap() {
  const defaultPos = [28.6145, 77.2120];

  map = L.map('map', {
    zoomControl: true,
    attributionControl: false
  }).setView(defaultPos, 15);

  // CartoDB Dark Matter tiles
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    subdomains: 'abcd'
  }).addTo(map);

  // School Polygon (Safe)
  L.polygon(GEOFENCES.school, {
    color: '#10B981',
    weight: 2,
    fillColor: '#10B981',
    fillOpacity: 0.2
  }).addTo(map).bindTooltip('🏫 School Safe Zone', { permanent: true, direction: 'center', className: 'map-label' });

  // Home Polygon (Safe)
  L.polygon(GEOFENCES.home, {
    color: '#3B82F6',
    weight: 2,
    fillColor: '#3B82F6',
    fillOpacity: 0.2
  }).addTo(map).bindTooltip('🏡 Home Safe Zone', { permanent: true, direction: 'center', className: 'map-label' });

  // Industrial Danger Zone (Prohibited)
  L.polygon(GEOFENCES.danger, {
    color: '#EF4444',
    weight: 2.5,
    dashArray: '6, 6',
    fillColor: '#EF4444',
    fillOpacity: 0.28
  }).addTo(map).bindTooltip('⚠️ Industrial Danger Zone', { permanent: true, direction: 'center', className: 'map-label danger' });

  // Custom Child Marker with High-Tech Pulse
  const childIcon = L.divIcon({
    className: 'custom-child-pin',
    html: `
      <div style="position: relative; width: 36px; height: 36px;">
        <div style="position: absolute; inset: -8px; border-radius: 50%; background: rgba(6, 182, 212, 0.4); animation: pulse-ring 1.8s infinite;"></div>
        <div style="position: absolute; inset: 0; border-radius: 50%; background: #06b6d4; border: 3px solid #ffffff; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px #06b6d4;">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" stroke-width="2.5">
            <circle cx="12" cy="7" r="4"/>
            <path d="M5.5 21a8.38 8.38 0 0 1 13 0"/>
          </svg>
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18]
  });

  childMarker = L.marker(defaultPos, { icon: childIcon }).addTo(map);
}

// 2. Update Telemetry UI
function updateTelemetry(lat, lon, speed, battery = '84%') {
  const dispCoords = document.getElementById('dispCoords');
  const dispSpeed = document.getElementById('dispSpeed');
  const dispBattery = document.getElementById('dispBattery');

  if (dispCoords) dispCoords.innerText = `${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E`;
  if (dispSpeed) dispSpeed.innerText = `${speed.toFixed(1)} m/s`;
  if (dispBattery) dispBattery.innerText = battery;

  // Move marker smoothly
  if (childMarker) childMarker.setLatLng([lat, lon]);
  if (map) map.panTo([lat, lon], { animate: true, duration: 0.8 });
}

// 3. Append Event to Live Threat Feed
function appendThreatLog(type, severity, snippet, trigger) {
  const feed = document.getElementById('threatFeed');
  if (!feed) return;

  const now = new Date();
  const timeStr = now.toTimeString().split(' ')[0];

  const logItem = document.createElement('div');
  const sevClass = severity.toLowerCase();
  logItem.className = `log-item ${sevClass}`;

  logItem.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
      <div>
        <span class="log-time">[${timeStr}]</span>
        <span class="log-tag" style="color: ${severity === 'CRITICAL' ? '#ef4444' : severity === 'HIGH' ? '#f59e0b' : '#10b981'};">${type}</span>
      </div>
      <span style="font-size: 0.65rem; font-weight: 700; padding: 0.1rem 0.4rem; border-radius: 4px; background: rgba(255,255,255,0.08); text-transform: uppercase;">${severity}</span>
    </div>
    <div style="color: #cbd5e1; font-size: 0.775rem; margin-bottom: 0.2rem;">${snippet}</div>
    <div style="font-size: 0.675rem; color: #64748b; font-family: monospace;">Condition: ${trigger}</div>
  `;

  feed.prepend(logItem);
}

// 4. Attach Scenario Simulation Handlers
function setupSimulatorEvents() {
  // Scenario 1: Inside School (Safe Zone)
  const btnSchool = document.getElementById('btnSchool');
  if (btnSchool) {
    btnSchool.addEventListener('click', () => {
      updateTelemetry(28.6145, 77.2120, 0.2, '84%');
      appendThreatLog(
        'SAFE_ZONE_NORMAL',
        'SUCCESS',
        'Device is secured inside designated School perimeter.',
        'ST_Contains(SchoolZone, Location) == TRUE'
      );
    });
  }

  // Scenario 2: Exit Perimeter (Warning)
  const btnExit = document.getElementById('btnExit');
  if (btnExit) {
    btnExit.addEventListener('click', () => {
      updateTelemetry(28.6190, 77.2180, 1.8, '83%');
      appendThreatLog(
        'SAFE_ZONE_EXIT',
        'HIGH',
        'Perimeter Breach: Aarav exited School safe zone boundaries.',
        'OutsideAllSafeZones == TRUE'
      );
    });
  }

  // Scenario 3: Danger Zone Breach (Critical Alarm)
  const btnDanger = document.getElementById('btnDanger');
  if (btnDanger) {
    btnDanger.addEventListener('click', () => {
      updateTelemetry(28.6120, 77.2340, 2.5, '81%');
      appendThreatLog(
        'DANGER_ZONE_BREACH',
        'CRITICAL',
        'CRITICAL ALERT: Child entered restricted Industrial Construction Site!',
        'ST_Contains(DangerZone, Location) == TRUE'
      );
    });
  }

  // Scenario 4: Predator Message Intercept
  const btnChat = document.getElementById('btnChat');
  if (btnChat) {
    btnChat.addEventListener('click', () => {
      appendThreatLog(
        'CHAT_SECURITY_ALARM',
        'HIGH',
        'WhatsApp Sniffer: "Hey, meet alone at the secret place after class, don\'t tell parents."',
        'Regex Match: [meet alone, secret place, don\'t tell]'
      );
    });
  }

  // Scenario 5: Silent Triple-Tap Volume SOS
  const btnSos = document.getElementById('btnSos');
  if (btnSos) {
    btnSos.addEventListener('click', () => {
      updateTelemetry(28.6145, 77.2120, 0.0, '80%');
      appendThreatLog(
        'EMERGENCY_SOS_ALARM',
        'CRITICAL',
        'PHYSICAL DISTRESS SOS: Silent panic triggered via Volume Down triple-click!',
        'HARDWARE_TRIPLE_VOLUME_TAP (<= 2000ms)'
      );
    });
  }

  // Scenario 6: Instant Remote Lock
  const btnLock = document.getElementById('btnRemoteLock');
  const lblLockStatus = document.getElementById('lblLockStatus');
  if (btnLock) {
    btnLock.addEventListener('click', () => {
      isDeviceLocked = !isDeviceLocked;
      if (isDeviceLocked) {
        if (lblLockStatus) lblLockStatus.innerText = 'Device Locked (Unlock)';
        btnLock.classList.add('critical');
        appendThreatLog(
          'REMOTE_LOCK_ENGAGED',
          'CRITICAL',
          'Command sent to child daemon: Full screen overlay locked and inputs frozen.',
          'MQTT: childguard/aarav/command/lock (PIN REQUIRED)'
        );
      } else {
        if (lblLockStatus) lblLockStatus.innerText = 'Instant Screen Lock';
        btnLock.classList.remove('critical');
        appendThreatLog(
          'REMOTE_LOCK_DISENGAGED',
          'SUCCESS',
          'Lock PIN accepted. Child device returned to normal state.',
          'MQTT: childguard/aarav/command/unlock'
        );
      }
    });
  }

  // Clear Logs
  const btnClear = document.getElementById('btnClearLogs');
  if (btnClear) {
    btnClear.addEventListener('click', () => {
      const feed = document.getElementById('threatFeed');
      if (feed) feed.innerHTML = '';
    });
  }
}

// 5. Initial Seed Logs
function populateInitialLogs() {
  appendThreatLog('DAEMON_ONLINE', 'SUCCESS', 'Android child background daemon connected to EMQX broker.', 'MQTT_HANDSHAKE_OK');
  appendThreatLog('SAFE_ZONE_NORMAL', 'SUCCESS', 'Current position verified inside School Safe Zone.', 'ST_Contains(School, Point) == TRUE');
}

// 6. Bootstrap
document.addEventListener('DOMContentLoaded', () => {
  initMap();
  setupSimulatorEvents();
  populateInitialLogs();
});
