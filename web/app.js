'use strict';

/* Wardrive Track: interfaz web y consumo de la API HTTP local.
 * Nunca se introducen SSID/BSSID sin escapar mediante innerHTML.
 */
let state = { networks: [], track: [], files: [], stats: {} };
let map = null, markers = null, trackLayer = null, offline = false, toastTimer = null;
const byId = (id) => document.getElementById(id);
const fmt = (value) => new Intl.NumberFormat('es-ES').format(value || 0);

function notify(message, error = false) {
  const el = byId('toast');
  el.textContent = message;
  el.classList.toggle('error', error);
  el.style.display = 'block';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.style.display = 'none'; }, 5500);
}
async function request(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Error de conexión');
  return data;
}
function download(path) { window.location.href = path; }

function setupMap() {
  if (typeof L === 'undefined') {
    offline = true;
    byId('offlineMap').style.display = 'block';
    byId('mapLabel').textContent = 'PLANO OFFLINE · GPS';
    return;
  }
  map = L.map('map', { zoomControl: false, attributionControl: true }).setView([20, 0], 2);
  L.control.zoom({ position: 'bottomright' }).addTo(map);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  markers = L.layerGroup().addTo(map);
}
function dataPoints() {
  return {
    nets: state.networks.filter((n) => n.lat !== null && n.lon !== null),
    points: state.track.filter((p) => p.lat !== null && p.lon !== null)
  };
}
function updateMap() {
  const { nets, points } = dataPoints();
  const hasGeo = nets.length > 0 || points.length > 0;
  byId('emptyMap').style.display = hasGeo ? 'none' : 'flex';
  byId('mapLabel').textContent = hasGeo ?
    fmt(nets.length) + ' REDES · ' + fmt(points.length) + ' GPS' + (offline ? ' · PLANO OFFLINE' : '') :
    'SIN COORDENADAS';
  if (offline) { drawOffline(); return; }
  if (!map) return;
  markers.clearLayers();
  if (trackLayer) { map.removeLayer(trackLayer); trackLayer = null; }
  if (points.length > 1) {
    trackLayer = L.polyline(points.map((p) => [p.lat, p.lon]), {
      color: '#67adf5', weight: 3, opacity: 0.85
    }).addTo(map);
  }
  if (points.length === 1) {
    L.circleMarker([points[0].lat, points[0].lon], {
      radius: 5, color: '#67adf5'
    }).addTo(markers);
  }
  for (const n of nets.slice(0, 4500)) {
    const marker = L.circleMarker([n.lat, n.lon], {
      radius: 6, fillColor: '#41e4b0', color: '#092e2d', weight: 1.5, fillOpacity: 0.88
    });
    const popup = document.createElement('div');
    const heading = document.createElement('strong');
    heading.textContent = n.ssid;
    popup.appendChild(heading);
    for (const pair of [
      ['BSSID', n.bssid],
      ['Señal', n.rssi === null ? 'Sin dato' : String(n.rssi) + ' dBm'],
      ['Observaciones', String(n.count)],
      ['Ubicación', 'Punto de observación GPS']
    ]) {
      const detail = document.createElement('div');
      detail.textContent = pair[0] + ': ' + pair[1];
      popup.appendChild(detail);
    }
    marker.bindPopup(popup).addTo(markers);
  }
  const all = nets.map((n) => [n.lat, n.lon]).concat(points.map((p) => [p.lat, p.lon]));
  if (all.length) map.fitBounds(L.latLngBounds(all), { padding: [35, 35], maxZoom: 16 });
}
function drawOffline() {
  const canvas = byId('offlineMap');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * dpr));
  canvas.height = Math.max(1, Math.floor(rect.height * dpr));
  ctx.scale(dpr, dpr);
  const w = rect.width, h = rect.height;
  ctx.fillStyle = '#10202d';
  ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = '#1e3847';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 12; i++) {
    const x = i * w / 12, y = i * h / 12;
    ctx.beginPath();
    ctx.moveTo(x, 0); ctx.lineTo(x, h);
    ctx.moveTo(0, y); ctx.lineTo(w, y);
    ctx.stroke();
  }
  const { nets, points } = dataPoints();
  const all = nets.concat(points);
  if (!all.length) return;
  let minLat = Infinity, maxLat = -Infinity, minLon = Infinity, maxLon = -Infinity;
  for (const p of all) {
    minLat = Math.min(minLat, p.lat); maxLat = Math.max(maxLat, p.lat);
    minLon = Math.min(minLon, p.lon); maxLon = Math.max(maxLon, p.lon);
  }
  const centerLat = (minLat + maxLat) / 2, centerLon = (minLon + maxLon) / 2;
  const cos = Math.max(0.2, Math.cos(centerLat * Math.PI / 180));
  const span = Math.max((maxLon - minLon) * cos, maxLat - minLat, 0.0005) * 1.35;
  const scale = Math.min(w, h) / span * 0.72;
  const fx = (p) => w / 2 + (p.lon - centerLon) * cos * scale;
  const fy = (p) => h / 2 - (p.lat - centerLat) * scale;
  if (points.length > 1) {
    ctx.beginPath();
    points.forEach((p, i) => { if (i === 0) ctx.moveTo(fx(p), fy(p)); else ctx.lineTo(fx(p), fy(p)); });
    ctx.strokeStyle = '#6caef4'; ctx.lineWidth = 2.5; ctx.stroke();
  }
  for (const p of nets) {
    ctx.beginPath(); ctx.arc(fx(p), fy(p), 6, 0, Math.PI * 2);
    ctx.fillStyle = '#41e4b0'; ctx.fill();
    ctx.strokeStyle = '#082d2a'; ctx.lineWidth = 2; ctx.stroke();
  }
  ctx.fillStyle = '#8fa9b8'; ctx.font = '11px system-ui';
  ctx.fillText('Lat ' + centerLat.toFixed(5) + ' · Lon ' + centerLon.toFixed(5) + ' | Plano esquemático', 16, h - 16);
}
function renderRows() {
  const query = byId('search').value.trim().toLowerCase();
  const filter = byId('filter').value;
  const matched = state.networks.filter((n) =>
    (n.ssid.toLowerCase().includes(query) || n.bssid.toLowerCase().includes(query)) &&
    (filter === 'all' || (filter === 'located' ? n.lat !== null : n.lat === null))
  );
  const rows = byId('rows');
  rows.replaceChildren();
  if (!matched.length) {
    const tr = document.createElement('tr'), td = document.createElement('td');
    td.colSpan = 5; td.className = 'no-data';
    td.textContent = state.networks.length ? 'No hay resultados para este filtro.' : 'Todavía no hay redes. Importa un archivo para comenzar.';
    tr.appendChild(td); rows.appendChild(tr);
  }
  for (const n of matched.slice(0, 1000)) {
    const tr = document.createElement('tr');
    const name = document.createElement('td');
    const ssid = document.createElement('span'), bssid = document.createElement('span');
    ssid.className = 'ssid'; ssid.textContent = n.ssid;
    bssid.className = 'bssid'; bssid.textContent = n.bssid;
    name.append(ssid, bssid); tr.appendChild(name);
    const channel = document.createElement('td');
    channel.textContent = n.channel === null ? '—' : String(n.channel);
    tr.appendChild(channel);
    const signal = document.createElement('td');
    signal.className = 'signal';
    signal.textContent = n.rssi === null ? '—' : String(n.rssi) + ' dBm';
    tr.appendChild(signal);
    const count = document.createElement('td');
    count.textContent = fmt(n.count);
    tr.appendChild(count);
    const location = document.createElement('td');
    const pill = document.createElement('span');
    pill.className = 'pill ' + (n.lat !== null ? 'yes' : 'no');
    pill.textContent = n.lat !== null ? '⌖ GPS observado' : '— Sin GPS';
    location.appendChild(pill); tr.appendChild(location);
    rows.appendChild(tr);
  }
  byId('resultCount').textContent = fmt(matched.length) + ' redes encontradas' +
    (matched.length > 1000 ? ' · mostrando primeras 1.000' : '');
}
function refresh() {
  byId('statNetworks').textContent = fmt(state.stats.networks);
  byId('statLocated').textContent = fmt(state.stats.located);
  byId('statSights').textContent = fmt(state.stats.sightings);
  byId('statGPS').textContent = fmt(state.stats.gps);
  const list = byId('files'); list.replaceChildren();
  if (!state.files.length) {
    const empty = document.createElement('span');
    empty.className = 'empty-small'; empty.textContent = 'Sin archivos importados';
    list.appendChild(empty);
  }
  for (const f of state.files) {
    const div = document.createElement('div'), detail = document.createElement('small');
    div.className = 'file-chip'; div.textContent = '▤ ' + f.name;
    detail.textContent = fmt(f.observations) + ' observaciones · ' + fmt(f.gps) + ' puntos GPS';
    div.appendChild(detail); list.appendChild(div);
  }
  renderRows(); updateMap();
}
async function sync() { state = await request('/api/status'); refresh(); }
async function upload(files) {
  for (const file of files) {
    try {
      const extension = file.name.toLowerCase().split('.').pop();
      if (!['pcap', 'pcapng', 'log', 'txt', 'csv'].includes(extension)) throw Error(file.name + ': extensión no válida');
      if (file.size > 32 * 1024 * 1024) throw Error(file.name + ': máximo 32 MiB');
      const result = await request('/api/import?name=' + encodeURIComponent(file.name), {
        method: 'POST', body: file, headers: { 'Content-Type': 'application/octet-stream' }
      });
      notify(file.name + ': ' + result.observations + ' observaciones, ' + result.gps +
        ' GPS. ' + result.warnings.join(' '));
    } catch (error) { notify(error.message, true); }
  }
  await sync();
}
byId('fileInput').addEventListener('change', (event) => {
  upload(Array.from(event.target.files));
  event.target.value = '';
});
const zone = byId('drop');
for (const type of ['dragenter', 'dragover']) {
  zone.addEventListener(type, (event) => {
    event.preventDefault(); zone.classList.add('drag');
  });
}
for (const type of ['dragleave', 'drop']) {
  zone.addEventListener(type, (event) => {
    event.preventDefault(); zone.classList.remove('drag');
  });
}
zone.addEventListener('drop', (event) => upload(Array.from(event.dataTransfer.files)));
byId('demoBtn').addEventListener('click', async () => {
  if (state.files.length && !confirm('La demostración sustituirá los archivos de esta sesión. ¿Continuar?')) return;
  try {
    await request('/api/demo', { method: 'POST' }); await sync();
    notify('Demostración cargada: CSV, log GPS y PCAP sintéticos.');
  } catch (error) { notify(error.message, true); }
});
byId('clearBtn').addEventListener('click', async () => {
  if (!confirm('¿Borrar los datos importados de esta sesión local?')) return;
  try {
    await request('/api/clear', { method: 'POST' }); await sync(); notify('Sesión limpiada');
  } catch (error) { notify(error.message, true); }
});
byId('csvBtn').addEventListener('click', () => download('/api/export.csv'));
byId('geoBtn').addEventListener('click', () => download('/api/export.geojson'));
byId('search').addEventListener('input', renderRows);
byId('filter').addEventListener('change', renderRows);
window.addEventListener('resize', () => {
  if (offline) drawOffline(); else if (map) map.invalidateSize();
});
setupMap();
sync().catch((error) => notify('No se pudo establecer conexión local: ' + error.message, true));
