'use strict';

/* Wardrive Track — interfaz sin frameworks.
 * Los SSID, nombres Bluetooth y MAC siempre se insertan como textContent.
 * Los filtros son locales y no envían datos a servicios de terceros.
 */
const el = (id) => document.getElementById(id);
const number = (value) => new Intl.NumberFormat('es-ES').format(value || 0);
const FILTER_IDS = ['search', 'typeFilter', 'securityFilter', 'gpsFilter', 'signalFilter', 'sortFilter'];
const CSV_FIELDS = ['protocol', 'bssid', 'ssid', 'security', 'channel', 'rssi', 'rssi_min', 'count', 'located_count', 'lat', 'lon', 'first_seen', 'last_seen', 'address_type'];
const SECURITY_ORDER = ['OPEN', 'WEP', 'WPA', 'WPA2', 'WPA2/WPA3', 'WPA3', 'OWE', 'No determinada'];
let state = { networks: [], track: [], files: [], stats: {}, security: {} };
let map = null, layers = null, route = null, offline = false, notificationTimer = null;
let tileErrors = 0;

function notify(message, error = false) {
  const toast = el('toast');
  toast.textContent = message;
  toast.classList.toggle('error', error);
  toast.style.display = 'block';
  clearTimeout(notificationTimer);
  notificationTimer = setTimeout(() => { toast.style.display = 'none'; }, 6500);
}

async function request(path, options) {
  const response = await fetch(path, options);
  let data;
  try { data = await response.json(); } catch (_) { throw Error('El servidor devolvió una respuesta no válida'); }
  if (!response.ok) throw Error(data.error || 'Error en la operación');
  return data;
}

function filtered() {
  const q = el('search').value.trim().toLocaleLowerCase('es');
  const type = el('typeFilter').value;
  const security = el('securityFilter').value;
  const gps = el('gpsFilter').value;
  const signal = el('signalFilter').value;
  const sort = el('sortFilter').value;
  const rows = state.networks.filter((n) => {
    if (q && ![n.ssid || '', n.bssid || '', n.protocol || '', n.security || ''].some((s) => s.toLocaleLowerCase('es').includes(q))) return false;
    if (type !== 'all' && n.protocol !== type) return false;
    if (security !== 'all' && n.security !== security) return false;
    const located = n.lat !== null && n.lon !== null;
    if (gps === 'located' && !located) return false;
    if (gps === 'unlocated' && located) return false;
    if (signal === 'unknown' && n.rssi !== null) return false;
    if (signal === 'strong' && (n.rssi === null || n.rssi < -60)) return false;
    if (signal === 'medium' && (n.rssi === null || n.rssi < -80 || n.rssi >= -60)) return false;
    if (signal === 'weak' && (n.rssi === null || n.rssi >= -80)) return false;
    return true;
  });
  if (sort === 'name') rows.sort((a, b) => a.ssid.localeCompare(b.ssid, 'es'));
  else if (sort === 'count') rows.sort((a, b) => b.count - a.count);
  else if (sort === 'last') rows.sort((a, b) => (b.last_seen || '').localeCompare(a.last_seen || ''));
  else rows.sort((a, b) => (b.rssi === null ? -999 : b.rssi) - (a.rssi === null ? -999 : a.rssi));
  return rows;
}

function cell(row, value, className) {
  const td = document.createElement('td');
  if (className) td.className = className;
  if (value instanceof Node) td.appendChild(value);
  else td.textContent = String(value);
  row.appendChild(td);
  return td;
}
function chip(text, classes) {
  const span = document.createElement('span');
  span.className = classes;
  span.textContent = text;
  return span;
}
function securityClass(s) {
  if (['WEP', 'WPA'].includes(s)) return 'legacy';
  if (['WPA2', 'WPA3', 'WPA2/WPA3', 'OWE'].includes(s)) return 'modern';
  if (s === 'OPEN') return 'open';
  return 'unknown';
}

function renderRows(list) {
  const table = el('rows');
  table.replaceChildren();
  if (!list.length) {
    const tr = document.createElement('tr');
    const td = cell(tr, state.networks.length ? 'No existen coincidencias con los filtros seleccionados.' : 'No hay datos. Importa una captura o carga la demostración.', 'no-data');
    td.colSpan = 7;
    table.appendChild(tr);
  }
  for (const n of list.slice(0, 1500)) {
    const tr = document.createElement('tr');
    const identity = document.createElement('div');
    identity.appendChild(chip(n.ssid || '(sin nombre)', 'ssid'));
    identity.appendChild(chip(n.bssid, 'bssid'));
    cell(tr, identity);
    const tag = n.protocol === 'Wi-Fi' ? 'wifi' : n.protocol === 'BLE' ? 'ble' : 'bt';
    cell(tr, chip(n.protocol, 'type-pill ' + tag));
    cell(tr, chip(n.protocol === 'Wi-Fi' ? n.security : '—', 'security-pill ' + securityClass(n.security)));
    cell(tr, n.channel === null ? '—' : n.channel);
    cell(tr, n.rssi === null ? '—' : n.rssi + ' dBm', 'signal');
    cell(tr, number(n.count));
    cell(tr, chip(n.lat === null ? '— Sin GPS' : '⌖ Con GPS', 'pill ' + (n.lat === null ? 'no' : 'yes')));
    table.appendChild(tr);
  }
  el('resultCount').textContent = number(list.length) + ' identificadores visibles de ' + number(state.networks.length) +
    (list.length > 1500 ? ' · se muestran 1.500 para mantener la fluidez' : '');
}

function drawSecurity() {
  const chart = el('securityChart');
  chart.replaceChildren();
  const max = Math.max(...SECURITY_ORDER.map((s) => state.security[s] || 0), 0);
  if (!max) {
    chart.appendChild(chip('Todavía no hay redes Wi-Fi para clasificar.', 'empty-small'));
    return;
  }
  for (const label of SECURITY_ORDER) {
    const count = state.security[label] || 0;
    const wrapper = document.createElement('div');
    wrapper.className = 'security-item';
    const top = document.createElement('div');
    top.className = 'security-top';
    top.appendChild(chip(label, ''));
    top.appendChild(chip(number(count), ''));
    top.lastChild.style.fontWeight = '700';
    const rail = document.createElement('div');
    rail.className = 'security-track';
    const bar = document.createElement('div');
    bar.className = 'security-fill';
    bar.style.width = (count / max * 100).toFixed(1) + '%';
    rail.appendChild(bar);
    wrapper.append(top, rail);
    wrapper.title = label + ': ' + count + ' redes';
    chart.appendChild(wrapper);
  }
}

function initMap() {
  if (typeof L === 'undefined') { switchOffline(); return; }
  map = L.map('map', { zoomControl: false }).setView([20, 0], 2);
  L.control.zoom({ position: 'bottomright' }).addTo(map);
  const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '© OpenStreetMap contributors'
  });
  tiles.on('tileerror', () => {
    tileErrors += 1;
    if (tileErrors >= 3 && !offline) switchOffline();
  });
  tiles.addTo(map);
  layers = L.layerGroup().addTo(map);
}

function switchOffline() {
  offline = true;
  if (map) {
    map.remove();
    map = null;
  }
  el('map').style.display = 'none';
  el('offlineMap').style.display = 'block';
  drawOffline();
}

function geoPoints(list) {
  return {
    nets: list.filter((n) => n.lat !== null && n.lon !== null),
    track: state.track.filter((p) => p.lat !== null && p.lon !== null),
  };
}

function tooltip(node, label, value) {
  const p = document.createElement('div');
  p.textContent = label + ': ' + value;
  node.appendChild(p);
}

function renderMap(list) {
  const { nets, track } = geoPoints(list);
  const hasGeo = nets.length || track.length;
  el('emptyMap').style.display = hasGeo ? 'none' : 'flex';
  el('mapCount').textContent = number(nets.length) + ' marcadores visibles · GPS ±8 s';
  el('mapLabel').textContent = hasGeo ?
    number(nets.length) + ' MARCADORES · ' + number(track.length) + ' GPS' + (offline ? ' · PLANO LOCAL' : '') : 'SIN GPS';
  if (offline) { drawOffline(list); return; }
  if (!map) return;
  layers.clearLayers();
  if (route) { map.removeLayer(route); route = null; }
  if (track.length > 1) {
    route = L.polyline(track.map((p) => [p.lat, p.lon]), { color: '#f2bb72', weight: 3, opacity: 0.85 }).addTo(map);
  }
  if (track.length === 1) {
    L.circleMarker([track[0].lat, track[0].lon], { radius: 4, color: '#f2bb72' }).addTo(layers);
  }
  for (const n of nets.slice(0, 4500)) {
    const wifi = n.protocol === 'Wi-Fi';
    const point = L.circleMarker([n.lat, n.lon], {
      radius: 6, color: '#071d29', weight: 1.5, fillOpacity: 0.9,
      fillColor: wifi ? '#4ce2b9' : '#78baff'
    });
    const popup = document.createElement('div');
    const title = document.createElement('strong');
    title.textContent = n.ssid;
    popup.appendChild(title);
    tooltip(popup, 'Tecnología', n.protocol);
    tooltip(popup, 'MAC observada', n.bssid);
    if (wifi) tooltip(popup, 'Seguridad', n.security);
    tooltip(popup, 'Señal máxima', n.rssi === null ? 'No disponible' : n.rssi + ' dBm');
    tooltip(popup, 'Interpretación', 'Lugar de observación');
    point.bindPopup(popup).addTo(layers);
  }
  const locations = nets.map((p) => [p.lat, p.lon]).concat(track.map((p) => [p.lat, p.lon]));
  if (locations.length) map.fitBounds(L.latLngBounds(locations), { padding: [32, 32], maxZoom: 16 });
}

function drawOffline(list = filtered()) {
  const canvas = el('offlineMap'), ctx = canvas.getContext('2d');
  if (!ctx) return;
  const rect = canvas.getBoundingClientRect();
  const w = rect.width, h = rect.height, dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(w * dpr));
  canvas.height = Math.max(1, Math.round(h * dpr));
  ctx.scale(dpr, dpr);
  ctx.fillStyle = '#10202d'; ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = '#223e4c';
  for (let i = 0; i <= 12; i++) {
    ctx.beginPath();
    ctx.moveTo(i * w / 12, 0); ctx.lineTo(i * w / 12, h);
    ctx.moveTo(0, i * h / 12); ctx.lineTo(w, i * h / 12);
    ctx.stroke();
  }
  const { nets, track } = geoPoints(list);
  const all = [...nets, ...track];
  if (!all.length) return;
  const lats = all.map((p) => p.lat), lons = all.map((p) => p.lon);
  const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
  const centerLon = (Math.min(...lons) + Math.max(...lons)) / 2;
  const xRatio = Math.max(0.2, Math.cos(centerLat * Math.PI / 180));
  const span = Math.max((Math.max(...lons) - Math.min(...lons)) * xRatio,
    Math.max(...lats) - Math.min(...lats), 0.0005) * 1.4;
  const scale = Math.min(w, h) * 0.75 / span;
  const x = (p) => w/2 + (p.lon - centerLon) * xRatio * scale;
  const y = (p) => h/2 - (p.lat - centerLat) * scale;
  if (track.length > 1) {
    ctx.strokeStyle = '#f2bb72'; ctx.lineWidth = 3; ctx.beginPath();
    track.forEach((p, i) => i ? ctx.lineTo(x(p), y(p)) : ctx.moveTo(x(p), y(p)));
    ctx.stroke();
  }
  for (const p of nets) {
    ctx.beginPath(); ctx.arc(x(p), y(p), 6, 0, Math.PI*2);
    ctx.fillStyle = p.protocol === 'Wi-Fi' ? '#4ce2b9' : '#78baff';
    ctx.fill(); ctx.strokeStyle = '#071d29'; ctx.lineWidth = 2; ctx.stroke();
  }
  ctx.fillStyle = '#9bb4c4'; ctx.font = '11px system-ui';
  ctx.fillText('Plano esquemático · Centro GPS ' + centerLat.toFixed(5) + ', ' + centerLon.toFixed(5), 14, h - 16);
}

function renderFiles() {
  const list = el('files');
  list.replaceChildren();
  if (!state.files.length) {
    list.appendChild(chip('Sin archivos importados', 'empty-small'));
    return;
  }
  for (const f of state.files) {
    const item = document.createElement('div');
    item.className = 'file-chip';
    item.textContent = '▤ ' + f.name;
    const description = document.createElement('small');
    description.textContent = number(f.observations) + ' observaciones · ' + number(f.gps) + ' GPS';
    item.appendChild(description);
    list.appendChild(item);
  }
}

function render() {
  if (!state.app || typeof state.app.version !== 'string' || !state.app.creator) {
    notify('Esta instalación tiene un motor antiguo. Actualiza Wardrive Track y reinicia el proceso.', true);
    return;
  }
  const label = el('runtimeVersion');
  if (label) label.textContent = 'v' + state.app.version + ' · ' + state.app.creator;
  el('statNetworks').textContent = number(state.stats.networks);
  el('statWifi').textContent = number(state.stats.wifi);
  el('statBt').textContent = number((state.stats.ble || 0) + (state.stats.bluetooth || 0));
  el('statLocated').textContent = number(state.stats.located);
  el('statSights').textContent = number(state.stats.sightings);
  el('statGPS').textContent = number(state.stats.gps);
  el('statFiles').textContent = number(state.stats.files);
  renderFiles();
  drawSecurity();
  renderFiltered();
}
function renderFiltered() {
  const list = filtered();
  renderRows(list);
  renderMap(list);
}
async function sync() {
  state = await request('/api/status');
  render();
}

async function importFiles(files) {
  for (const file of files) {
    try {
      if (!/\.(pcap|pcapng|csv|log|txt)$/i.test(file.name)) throw Error('Extensión no reconocida: ' + file.name);
      if (file.size > 32 * 1024 * 1024) throw Error('Archivo superior a 32 MiB: ' + file.name);
      const report = await request('/api/import?name=' + encodeURIComponent(file.name), {
        method: 'POST', body: file, headers: { 'Content-Type': 'application/octet-stream' },
      });
      notify(file.name + ' · ' + report.observations + ' registros, ' + report.gps +
        ' GPS. ' + (report.warnings || []).join(' '));
    } catch (error) { notify(error.message, true); }
  }
  await sync();
}

function downloadBlob(filename, mime, data) {
  const blob = new Blob([data], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function safeCSV(v) {
  if (typeof v === 'number' && Number.isFinite(v)) return String(v);
  let text = v === null || v === undefined ? '' : String(v);
  if (/^[\s]*[=+\-@]/.test(text)) text = "'" + text;
  return '"' + text.replaceAll('"', '""') + '"';
}
function exportCSV(rows) {
  const lines = [CSV_FIELDS.join(',')];
  for (const row of rows) lines.push(CSV_FIELDS.map((f) => safeCSV(row[f])).join(','));
  downloadBlob('wardrive-track-filtrado.csv', 'text/csv;charset=utf-8', '\ufeff' + lines.join('\r\n'));
}
function exportGeoJSON(rows) {
  const features = [];
  for (const n of rows) {
    if (n.lat === null || n.lon === null) continue;
    const properties = {};
    for (const [key, value] of Object.entries(n)) {
      if (key !== 'lat' && key !== 'lon') properties[key] = value;
    }
    features.push({ type: 'Feature', properties,
      geometry: { type: 'Point', coordinates: [n.lon, n.lat] } });
  }
  const points = state.track.filter((p) => p.lat !== null && p.lon !== null);
  if (points.length > 1) features.push({
    type: 'Feature', properties: { kind: 'track', name: 'Recorrido GPS' },
    geometry: { type: 'LineString', coordinates: points.map((p) => [p.lon, p.lat]) }
  });
  downloadBlob('wardrive-track-filtrado.geojson', 'application/geo+json',
    JSON.stringify({ type: 'FeatureCollection', features }, null, 2));
}

el('fileInput').addEventListener('change', (ev) => {
  void importFiles(Array.from(ev.target.files));
  ev.target.value = '';
});
const drop = el('drop');
for (const event of ['dragover', 'dragenter']) drop.addEventListener(event, (ev) => {
  ev.preventDefault(); drop.classList.add('drag');
});
for (const event of ['dragleave', 'drop']) drop.addEventListener(event, (ev) => {
  ev.preventDefault(); drop.classList.remove('drag');
});
drop.addEventListener('drop', (ev) => void importFiles(Array.from(ev.dataTransfer.files)));
for (const id of FILTER_IDS) el(id).addEventListener(id === 'search' ? 'input' : 'change', renderFiltered);
el('resetBtn').addEventListener('click', () => {
  for (const id of FILTER_IDS) el(id).value = id === 'search' ? '' : id === 'sortFilter' ? 'signal' : 'all';
  renderFiltered();
});
el('demoBtn').addEventListener('click', async () => {
  if (state.files.length && !confirm('La demostración reemplazará tu sesión actual. ¿Continuar?')) return;
  try {
    await request('/api/demo', { method: 'POST' });
    await sync();
    notify('Demostración Wi-Fi + Bluetooth/BLE cargada correctamente.');
  } catch (err) { notify(err.message, true); }
});
el('clearBtn').addEventListener('click', async () => {
  if (!confirm('¿Vaciar la sesión de análisis actual?')) return;
  try {
    await request('/api/clear', { method: 'POST' });
    await sync();
    notify('Se ha vaciado la sesión.');
  } catch (err) { notify(err.message, true); }
});
el('csvBtn').addEventListener('click', () => {
  if (el('filteredExport').checked) exportCSV(filtered());
  else window.location.href = '/api/export.csv';
});
el('geoBtn').addEventListener('click', () => {
  if (el('filteredExport').checked) exportGeoJSON(filtered());
  else window.location.href = '/api/export.geojson';
});
window.addEventListener('resize', () => {
  if (offline) drawOffline();
  else if (map) map.invalidateSize();
});
initMap();
void sync().catch((err) => notify('No se pudo conectar al servicio local: ' + err.message, true));
