import { useEffect, useMemo, useState } from 'react';
import {
  Activity, AlertTriangle, Archive, ArrowUpRight, BadgeCheck, Bell, BookOpen,
  Camera, CarFront, CheckCircle2, ChevronDown, ClipboardList, Clock3, FileSearch,
  Fingerprint, Gauge, LayoutDashboard, LocateFixed, Map, Menu, Navigation2,
  Route, Search, Settings, Shield, ShieldAlert, Users, X,
} from 'lucide-react';
import './command-center.css';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
type Health = 'checking' | 'online' | 'offline';
type Section = 'Overview' | 'Traffic Routes' | 'Police Records' | 'Case Management' | 'Evidence Registry' | 'Live Operations' | 'Departments' | 'Audit Trail';

const navigation: { label: Section; icon: typeof Activity }[] = [
  { label: 'Overview', icon: LayoutDashboard },
  { label: 'Traffic Routes', icon: Route },
  { label: 'Police Records', icon: Fingerprint },
  { label: 'Case Management', icon: ClipboardList },
  { label: 'Evidence Registry', icon: Archive },
  { label: 'Live Operations', icon: Camera },
  { label: 'Departments', icon: Users },
  { label: 'Audit Trail', icon: FileSearch },
];

const areas = [
  { name: 'Ayeyarwady', my: 'ဧရာဝတီတိုင်းဒေသကြီး', kind: 'Region' },
  { name: 'Bago', my: 'ပဲခူးတိုင်းဒေသကြီး', kind: 'Region' },
  { name: 'Magway', my: 'မကွေးတိုင်းဒေသကြီး', kind: 'Region' },
  { name: 'Mandalay', my: 'မန္တလေးတိုင်းဒေသကြီး', kind: 'Region' },
  { name: 'Sagaing', my: 'စစ်ကိုင်းတိုင်းဒေသကြီး', kind: 'Region' },
  { name: 'Tanintharyi', my: 'တနင်္သာရီတိုင်းဒေသကြီး', kind: 'Region' },
  { name: 'Yangon', my: 'ရန်ကုန်တိုင်းဒေသကြီး', kind: 'Region' },
  { name: 'Chin', my: 'ချင်းပြည်နယ်', kind: 'State' },
  { name: 'Kachin', my: 'ကချင်ပြည်နယ်', kind: 'State' },
  { name: 'Kayah', my: 'ကယားပြည်နယ်', kind: 'State' },
  { name: 'Kayin', my: 'ကရင်ပြည်နယ်', kind: 'State' },
  { name: 'Mon', my: 'မွန်ပြည်နယ်', kind: 'State' },
  { name: 'Rakhine', my: 'ရခိုင်ပြည်နယ်', kind: 'State' },
  { name: 'Shan', my: 'ရှမ်းပြည်နယ်', kind: 'State' },
  { name: 'Naypyidaw', my: 'နေပြည်တော် ပြည်ထောင်စုနယ်မြေ', kind: 'Territory' },
];

const sectionInfo: Record<Section, { eyebrow: string; title: string; description: string }> = {
  Overview: { eyebrow: 'NATIONAL COMMAND / OVERVIEW', title: 'Public Safety Overview', description: 'A unified workspace for authorized, accountable public-safety operations.' },
  'Traffic Routes': { eyebrow: 'TRAFFIC OPERATIONS / ROUTE PREVIEW', title: 'Myanmar Route Operations', description: 'A visual route-planning preview for Myanmar. Map, route, and traffic indicators are illustrative demo data.' },
  'Police Records': { eyebrow: 'RESTRICTED / RMS', title: 'Person & Citizen Records', description: 'Organization-scoped records. Access is permission-gated and audited.' },
  'Case Management': { eyebrow: 'RESTRICTED / WORKFLOW', title: 'Criminal Case Management', description: 'Assignments, investigation notes, approvals, and case status in one workflow.' },
  'Evidence Registry': { eyebrow: 'RESTRICTED / CUSTODY', title: 'Evidence Registry', description: 'Register evidence metadata and maintain an append-only custody history.' },
  'Live Operations': { eyebrow: 'NATIONAL COVERAGE / STREAMS', title: 'Live Operations', description: 'Administrative coverage is listed; no camera or video provider is connected.' },
  Departments: { eyebrow: 'ORGANIZATION / DIRECTORY', title: 'Departments & Stations', description: 'Connect authorized organizations, departments, and stations to the platform.' },
  'Audit Trail': { eyebrow: 'GOVERNANCE / AUDIT', title: 'Access & Audit Trail', description: 'Review recorded access and workflow actions within your authorized organization.' },
};

function App() {
  const [health, setHealth] = useState<Health>('checking');
  const [active, setActive] = useState<Section>('Overview');
  const [selectedArea, setSelectedArea] = useState(areas[0].name);
  const [query, setQuery] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API}/health/live`, { signal: controller.signal })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error('API health check failed')))
      .then((data: { status: string }) => setHealth(data.status === 'alive' ? 'online' : 'offline'))
      .catch((error: unknown) => {
        if (error instanceof Error && error.name !== 'AbortError') setHealth('offline');
      });
    return () => controller.abort();
  }, []);

  const filteredAreas = useMemo(() => areas.filter((area) =>
    `${area.name} ${area.my} ${area.kind}`.toLowerCase().includes(query.trim().toLowerCase()),
  ), [query]);
  const page = sectionInfo[active];

  function navigate(section: Section) {
    setActive(section);
    setMobileOpen(false);
  }

  return (
    <div className="command-shell">
      {mobileOpen && <button className="command-scrim" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}
      <aside className={`command-sidebar ${mobileOpen ? 'is-open' : ''}`}>
        <div className="command-brand">
          <div className="command-brand-mark"><Shield size={22} /></div>
          <div><strong>APEXIVEAI</strong><span>PUBLIC SAFETY</span></div>
          <button className="command-close" aria-label="Close navigation" onClick={() => setMobileOpen(false)}><X size={18} /></button>
        </div>
        <div className="command-workspace">
          <span className="command-eyebrow">WORKSPACE</span>
          <button className="command-workspace-select">National Coordination <ChevronDown size={14} /></button>
        </div>
        <nav className="command-nav" aria-label="Main navigation">
          <span className="command-nav-label">OPERATIONS</span>
          {navigation.map(({ label, icon: Icon }) => (
            <button key={label} className={`command-nav-item ${active === label ? 'active' : ''}`} onClick={() => navigate(label)}>
              <Icon size={17} /><span>{label}</span>
              {label === 'Evidence Registry' && <i className="command-nav-dot" />}
            </button>
          ))}
        </nav>
        <div className="command-sidebar-bottom">
          <div className="command-secure-note">
            <Shield size={17} />
            <div><b>Restricted workspace</b><small>Use authorized accounts only</small></div>
          </div>
          <div className="command-user"><div className="command-avatar">DV</div><div><b>Development workspace</b><small>Local demo · no identity provider</small></div><Settings size={15} /></div>
        </div>
      </aside>

      <main className="command-main">
        <header className="command-topbar">
          <button className="command-menu" aria-label="Open navigation" onClick={() => setMobileOpen(true)}><Menu size={20} /></button>
          <div className="command-breadcrumb">National Coordination <span>/</span> <b>{active}</b></div>
          <div className="command-top-actions">
            <div className={`command-connection ${health}`}><i />API {health === 'checking' ? 'Checking' : health === 'online' ? 'Connected' : 'Offline'}</div>
            <button className="command-icon-button" aria-label="Search"><Search size={18} /></button>
            <button className="command-icon-button" aria-label="Notifications"><Bell size={18} /></button>
            <div className="command-top-avatar">DV</div>
          </div>
        </header>

        <section className="command-content">
          <div className="command-page-heading">
            <div><div className="command-eyebrow">{page.eyebrow}</div><h1>{page.title}</h1><p>{page.description}</p></div>
            <div className="command-classification"><ShieldAlert size={14} /> DEMO · NO REAL RECORDS</div>
          </div>

          {active === 'Traffic Routes' ? (
            <TrafficRoutes />
          ) : active === 'Overview' || active === 'Live Operations' ? (
            <Overview
              active={active}
              health={health}
              selectedArea={selectedArea}
              onSelectArea={setSelectedArea}
              filteredAreas={filteredAreas}
              query={query}
              onQueryChange={setQuery}
            />
          ) : (
            <FeaturePage section={active} onNavigate={navigate} />
          )}

          <footer className="command-footer">
            <span>© 2026 APEXIVEAI COMPANY., LTD.</span>
            <span>FOUNDATION BUILD 0.1.0 <i /> AUTHENTICATION & STREAM PROVIDER NOT CONFIGURED</span>
          </footer>
        </section>
      </main>
    </div>
  );
}

function Overview({
  active, health, selectedArea, onSelectArea, filteredAreas, query, onQueryChange,
}: {
  active: Section;
  health: Health;
  selectedArea: string;
  onSelectArea: (area: string) => void;
  filteredAreas: typeof areas;
  query: string;
  onQueryChange: (value: string) => void;
}) {
  return (
    <>
      <section className="command-welcome">
        <div className="command-welcome-copy">
          <div className="command-welcome-tag"><i /> NATIONWIDE ADMINISTRATIVE COVERAGE</div>
          <h2>One platform. <span>Accountable coordination.</span></h2>
          <p>All 7 regions, 7 states, and Naypyidaw are represented in the directory.</p>
        </div>
        <div className="command-welcome-art" aria-hidden="true">
          <div className="command-orbit orbit-a" /><div className="command-orbit orbit-b" />
          <div className="command-shield-large"><Shield size={48} /></div>
          <i className="command-orbit-point point-a" /><i className="command-orbit-point point-b" />
        </div>
      </section>

      <div className="command-section-title">
        <div><h2>{active === 'Live Operations' ? 'Live stream readiness' : 'National operations'}</h2><p>System connection status, not operational activity or live location data.</p></div>
        <span className="command-demo-label"><i /> DEMO / NOT CONNECTED</span>
      </div>

      <div className="command-stats">
        <Metric icon={Map} tone="blue" label="Administrative areas" value="15" detail="7 regions · 7 states · Naypyidaw" />
        <Metric icon={Activity} tone="green" label="Connected source systems" value="0" detail="No external feeds configured" />
        <Metric icon={ClipboardList} tone="purple" label="RMS records" value="—" detail="Available after authorized sign-in" />
        <Metric icon={Camera} tone="amber" label="Live video feeds" value="0" detail="Provider and approvals required" />
      </div>

      <div className="command-dashboard-grid">
        <section className="command-panel command-coverage-panel">
          <div className="command-panel-heading">
            <div><h2>Administrative coverage</h2><p>Select an area to view connection readiness.</p></div>
            <span className="command-coverage-badge"><i /> DIRECTORY READY</span>
          </div>
          <div className="command-map">
            <div className="command-map-grid" aria-hidden="true" />
            <div className="command-map-routes" aria-hidden="true">
              <svg viewBox="0 0 760 310" preserveAspectRatio="none">
                <path d="M22 236 C115 184 116 118 226 132 S342 231 422 157 577 85 730 46" />
                <path d="M58 32 C143 65 198 220 304 245 S452 188 510 99 645 76 730 192" />
                <path d="M23 130 C145 132 191 93 284 57 S444 64 512 174 644 260 734 230" />
                <path d="M147 297 C209 231 253 203 338 185 S483 233 589 167 666 131 744 112" />
              </svg>
            </div>
            <div className="command-area-grid">
              {filteredAreas.map((area, index) => (
                <button
                  key={area.name}
                  className={`command-area-node ${selectedArea === area.name ? 'selected' : ''}`}
                  onClick={() => onSelectArea(area.name)}
                  aria-pressed={selectedArea === area.name}
                >
                  <i className={`node-${index % 4}`} />
                  <span>{area.name}</span>
                  <small>{area.kind === 'Territory' ? 'Territory' : area.kind}</small>
                </button>
              ))}
              {filteredAreas.length === 0 && <div className="command-area-empty">No administrative areas match this search.</div>}
            </div>
            <div className="command-map-disclaimer"><Map size={13} /> Administrative directory · not a geographic or live-incident map</div>
          </div>
          <div className="command-selected-area">
            <div><span className="command-eyebrow">SELECTED AREA</span><strong>{areas.find((area) => area.name === selectedArea)?.my}</strong><small>{selectedArea} · {areas.find((area) => area.name === selectedArea)?.kind}</small></div>
            <span className="command-status-pill"><i /> NOT CONNECTED</span>
          </div>
        </section>

        <div className="command-side-stack">
          <section className="command-panel command-stream-panel">
            <div className="command-panel-heading"><div><h2>Stream gateway</h2><p>Authorized integration status</p></div><Camera size={17} /></div>
            <div className="command-stream-visual"><div className="command-stream-lock"><Shield size={24} /></div><div><b>No provider configured</b><span>Video is not being received or recorded.</span></div></div>
            <div className="command-stream-detail"><span>Selected area</span><b>{selectedArea}</b></div>
            <div className="command-stream-detail"><span>Stream authorization</span><b className="waiting">NOT CONFIGURED</b></div>
            <p className="command-small-note">Requires an approved provider, authenticated operators, retention policy, and customer authorization.</p>
          </section>
          <section className="command-panel command-health-panel">
            <div className="command-panel-heading"><div><h2>Platform health</h2><p>Development environment checks</p></div><span className={`command-health-badge ${health}`}><i /> {health === 'online' ? 'API ONLINE' : health === 'checking' ? 'CHECKING' : 'API OFFLINE'}</span></div>
            <HealthRow icon={Activity} label="Backend API" value={health === 'online' ? 'ONLINE' : health === 'checking' ? 'CHECKING' : 'OFFLINE'} tone={health} />
            <HealthRow icon={Shield} label="Authentication" value="NOT CONFIGURED" tone="waiting" />
            <HealthRow icon={Camera} label="Video provider" value="NOT CONFIGURED" tone="waiting" />
          </section>
        </div>
      </div>

      <section className="command-panel command-region-panel">
        <div className="command-panel-heading command-region-heading">
          <div><h2>Regions & states</h2><p>Search the complete administrative directory.</p></div>
          <label className="command-search"><Search size={15} /><input value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Search areas" /></label>
        </div>
        <div className="command-region-list">
          {filteredAreas.map((area) => (
            <button key={area.name} className={`command-region-row ${selectedArea === area.name ? 'selected' : ''}`} onClick={() => onSelectArea(area.name)}>
              <span className="command-region-icon">{area.kind === 'State' ? <Shield size={15} /> : <Map size={15} />}</span>
              <span className="command-region-name"><b>{area.name}</b><small>{area.my}</small></span>
              <span className="command-region-type">{area.kind}</span>
              <span className="command-region-status"><i /> Not connected</span>
              <ArrowUpRight size={14} />
            </button>
          ))}
        </div>
      </section>
    </>
  );
}

const routeLocations = [
  { name: 'Yangon', my: 'ရန်ကုန်', x: 322, y: 481 },
  { name: 'Naypyidaw', my: 'နေပြည်တော်', x: 354, y: 400 },
  { name: 'Mandalay', my: 'မန္တလေး', x: 375, y: 310 },
  { name: 'Bagan', my: 'ပုဂံ', x: 277, y: 367 },
  { name: 'Taunggyi', my: 'တောင်ကြီး', x: 445, y: 407 },
  { name: 'Mawlamyine', my: 'မော်လမြိုင်', x: 415, y: 559 },
  { name: 'Myitkyina', my: 'မြစ်ကြီးနား', x: 390, y: 128 },
  { name: 'Sittwe', my: 'စစ်တွေ', x: 153, y: 350 },
];

function TrafficRoutes() {
  const [origin, setOrigin] = useState('Yangon');
  const [destination, setDestination] = useState('Mandalay');
  const [alternate, setAlternate] = useState(false);
  const start = routeLocations.find((place) => place.name === origin) ?? routeLocations[0];
  const end = routeLocations.find((place) => place.name === destination) ?? routeLocations[2];
  const hasDefaultSample = origin === 'Yangon' && destination === 'Mandalay';
  const routePath = alternate
    ? `M ${start.x} ${start.y} Q 282 425 310 392 T ${end.x} ${end.y}`
    : `M ${start.x} ${start.y} Q 372 456 354 400 T ${end.x} ${end.y}`;

  function swapLocations() {
    setOrigin(destination);
    setDestination(origin);
  }

  return (
    <div className="traffic-layout">
      <section className="command-panel traffic-map-panel">
        <div className="command-panel-heading traffic-map-heading">
          <div><h2>Myanmar road network</h2><p>မြန်မာနိုင်ငံ လမ်းကြောင်းမြင်ကွင်း</p></div>
          <span className="traffic-demo-pill"><i /> DEMO MAP</span>
        </div>
        <div className="traffic-map">
          <div className="traffic-map-grid" aria-hidden="true" />
          <svg className="traffic-country" viewBox="0 0 700 700" role="img" aria-label="Illustrative map of Myanmar with a selected route">
            <path className="traffic-country-shape" d="M354 47 L390 58 L415 83 L435 110 L425 139 L451 166 L443 197 L471 226 L457 254 L475 281 L452 309 L464 340 L445 366 L459 393 L438 422 L447 452 L425 477 L431 506 L411 530 L416 557 L395 579 L405 609 L383 632 L376 671 L357 650 L349 618 L331 589 L323 557 L310 532 L303 500 L287 476 L274 449 L255 426 L243 402 L228 378 L208 362 L187 354 L168 337 L157 315 L178 298 L191 273 L214 257 L231 233 L246 207 L262 184 L276 157 L284 127 L302 100 L320 75 Z" />
            <path className="traffic-country-grid" d="M354 47 L390 58 L415 83 L435 110 L425 139 L451 166 L443 197 L471 226 L457 254 L475 281 L452 309 L464 340 L445 366 L459 393 L438 422 L447 452 L425 477 L431 506 L411 530 L416 557 L395 579 L405 609 L383 632 L376 671 L357 650 L349 618 L331 589 L323 557 L310 532 L303 500 L287 476 L274 449 L255 426 L243 402 L228 378 L208 362 L187 354 L168 337 L157 315 L178 298 L191 273 L214 257 L231 233 L246 207 L262 184 L276 157 L284 127 L302 100 L320 75 Z" />
            <g className="traffic-roads" aria-hidden="true">
              <path d="M322 481 Q352 447 354 400 T375 310 Q365 251 390 128" />
              <path d="M277 367 Q335 345 375 310 T445 407" />
              <path d="M322 481 Q365 512 415 559" />
              <path d="M322 481 Q244 437 153 350" />
              <path d="M354 400 Q402 396 445 407" />
            </g>
            <path className="traffic-route-halo" d={routePath} />
            <path className="traffic-route-line" d={routePath} />
            {routeLocations.map((place) => {
              const isSelected = place.name === origin || place.name === destination;
              return (
                <g key={place.name} className={`traffic-place ${isSelected ? 'is-selected' : ''}`}>
                  <circle cx={place.x} cy={place.y} r={isSelected ? 7 : 4} />
                  <text x={place.x + 10} y={place.y - 9}>{place.name}</text>
                </g>
              );
            })}
            <g className="traffic-endpoint" transform={`translate(${start.x} ${start.y})`}><circle r="10" /><text y="3">A</text></g>
            <g className="traffic-endpoint destination" transform={`translate(${end.x} ${end.y})`}><circle r="10" /><text y="3">B</text></g>
          </svg>
          <div className="traffic-map-compass"><Navigation2 size={17} /><span>N</span></div>
          <div className="traffic-map-legend"><span><i className="route-legend-line" /> Selected route</span><span><i className="route-legend-dot" /> City / township</span></div>
          <div className="traffic-map-note"><Map size={13} /> Schematic only · not for turn-by-turn navigation</div>
        </div>
        <div className="traffic-map-footer"><span><i /> ROUTE PREVIEW READY</span><span>Myanmar · Demo network</span></div>
      </section>

      <aside className="traffic-side">
        <section className="command-panel traffic-planner">
          <div className="command-panel-heading"><div><h2>Plan a route</h2><p>Demo route selection</p></div><LocateFixed size={17} /></div>
          <label className="traffic-select-label">FROM
            <select value={origin} onChange={(event) => setOrigin(event.target.value)}>
              {routeLocations.map((place) => <option key={place.name} value={place.name}>{place.name} · {place.my}</option>)}
            </select>
          </label>
          <button className="traffic-swap" onClick={swapLocations} aria-label="Swap route origin and destination">↕</button>
          <label className="traffic-select-label">TO
            <select value={destination} onChange={(event) => setDestination(event.target.value)}>
              {routeLocations.map((place) => <option key={place.name} value={place.name}>{place.name} · {place.my}</option>)}
            </select>
          </label>
          <div className="traffic-route-summary">
            <span><Route size={15} /> {alternate ? 'Alternative route' : 'Primary route'}</span>
            <strong>{origin} <ArrowUpRight size={14} /> {destination}</strong>
            <div><b>{hasDefaultSample ? (alternate ? '626 km' : '631 km') : 'Demo only'}</b><span>{hasDefaultSample ? 'Approx. 10 hr 40 min' : 'No verified estimate'}</span></div>
          </div>
          <button className="traffic-alternate-button" onClick={() => setAlternate((value) => !value)}>
            <Route size={14} /> {alternate ? 'Show primary route' : 'View alternative route'}
          </button>
        </section>

        <section className="command-panel traffic-condition-panel">
          <div className="command-panel-heading"><div><h2>Route conditions</h2><p>Illustrative status · not live</p></div><Gauge size={17} /></div>
          <div className="traffic-condition-score"><div><span>ROAD STATUS</span><strong>Moderate</strong></div><div className="traffic-condition-ring"><span>68</span><small>/ 100</small></div></div>
          <div className="traffic-condition-row"><span><CarFront size={14} /> Estimated traffic</span><b>Light · Demo</b></div>
          <div className="traffic-condition-row"><span><Clock3 size={14} /> Updated</span><b>Sample data</b></div>
          <p className="command-small-note">No GPS, traffic sensor, incident, or navigation provider is connected.</p>
        </section>
      </aside>

      <section className="traffic-route-options">
        <div className="command-section-title"><div><h2>Route overview</h2><p>Sample routes and coverage for visual demonstration.</p></div><span className="command-demo-label"><i /> NOT FOR DISPATCH</span></div>
        <div className="traffic-route-cards">
          <article className={`command-panel traffic-route-card ${!alternate ? 'active' : ''}`}>
            <div className="traffic-route-card-icon"><Route size={17} /></div>
            <div><span className="traffic-card-label">PRIMARY ROUTE</span><strong>{origin} <ArrowUpRight size={13} /> {destination}</strong><small>Illustrative corridor · not verified</small></div>
            <b>{hasDefaultSample ? '631 km' : '—'}</b>
          </article>
          <article className={`command-panel traffic-route-card ${alternate ? 'active' : ''}`}>
            <div className="traffic-route-card-icon alt"><Route size={17} /></div>
            <div><span className="traffic-card-label">ALTERNATIVE</span><strong>{origin} <ArrowUpRight size={13} /> {destination}</strong><small>Illustrative corridor · not verified</small></div>
            <b>{hasDefaultSample ? '626 km' : '—'}</b>
          </article>
        </div>
      </section>
    </div>
  );
}

function Metric({ icon: Icon, tone, label, value, detail }: {
  icon: typeof Activity; tone: string; label: string; value: string; detail: string;
}) {
  return <article className="command-metric"><div className={`command-metric-icon ${tone}`}><Icon size={18} /></div><span>{label}</span><b>{value}</b><small>{detail}</small></article>;
}

function HealthRow({ icon: Icon, label, value, tone }: {
  icon: typeof Activity; label: string; value: string; tone: string;
}) {
  return <div className="command-health-row"><span><Icon size={15} />{label}</span><b className={tone}>{value}</b></div>;
}

function FeaturePage({ section, onNavigate }: { section: Section; onNavigate: (section: Section) => void }) {
  const records = section === 'Police Records';
  const cases = section === 'Case Management';
  const evidence = section === 'Evidence Registry';
  const departments = section === 'Departments';
  const audit = section === 'Audit Trail';
  const items = records
    ? ['Person / citizen records', 'Organization-scoped person search', 'Case-person relationship history', 'Restricted record access and audit']
    : cases
      ? ['Create and assign cases', 'Append-only investigation entries', 'Submit for independent approval', 'Status: open → pending approval → closed / returned']
      : evidence
        ? ['Evidence item registry', 'Initial receipt and custodian hand-off', 'Transfer validation against current custodian', 'Append-only custody timeline']
        : departments
          ? ['Organization → department → station hierarchy', 'Register all 15 administrative areas', 'Connect authorized source systems', 'Scope data by organization']
          : audit
            ? ['Person and case record reads', 'Case assignment and status changes', 'Evidence and custody actions', 'Approval decisions with reviewer identity']
            : ['Selected capability'];

  return (
    <div className="command-feature-layout">
      <section className="command-panel command-feature-main">
        <div className="command-feature-heading">
          <div className="command-feature-icon"><ClipboardList size={22} /></div>
          <div><span className="command-eyebrow">PHASE 3 / POLICE RMS</span><h2>{section}</h2><p>Operational APIs are available; live records require configured OIDC sign-in and organization scope.</p></div>
        </div>
        <div className="command-empty-records">
          <div className="command-empty-icon"><BookOpen size={23} /></div>
          <b>No connected records</b>
          <span>This development workspace does not contain real citizen, case, or evidence data.</span>
          <button onClick={() => onNavigate('Overview')}>View system readiness <ArrowUpRight size={14} /></button>
        </div>
      </section>
      <aside className="command-panel command-feature-aside">
        <div className="command-panel-heading"><div><h2>Available workflow</h2><p>Implemented in the RMS API</p></div><BadgeCheck size={18} /></div>
        <ul className="command-capability-list">{items.map((item) => <li key={item}><CheckCircle2 size={15} />{item}</li>)}</ul>
        <div className="command-api-note"><AlertTriangle size={15} /><span>Do not enter real records in this unauthenticated development environment. Configure Keycloak, migrations, encrypted evidence storage, and external immutable audit archival before deployment.</span></div>
      </aside>
    </div>
  );
}

export default App;
