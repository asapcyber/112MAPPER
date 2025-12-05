// frontend/src/App.tsx
import React, { useEffect, useMemo, useState } from 'react'
import {
  MapContainer,
  TileLayer,
  GeoJSON,
} from 'react-leaflet'
import type { LatLngExpression } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { fetchCalls, fetchRegionsNear, type Call, type Region } from './api'

type Metric = 'incidents' | 'crime_level' | 'e33_percent'

type BuurtFeatureProps = {
  BUURTNAAM?: string
  GM_NAAM?: string
  [key: string]: any
}

type BuurtFeature = GeoJSON.Feature<GeoJSON.Geometry, BuurtFeatureProps>
type BuurtCollection = GeoJSON.FeatureCollection<GeoJSON.Geometry, BuurtFeatureProps>

const DEFAULT_CENTER: LatLngExpression = [53.2194, 6.5665] // Binnenstad Groningen

// Crime level → color
function colorForCrimeLevel(level: number) {
  const colors = ['#16a34a', '#84cc16', '#f59e0b', '#f97316', '#ef4444']
  const idx = Math.min(Math.max(level - 1, 0), 4)
  return colors[idx]
}

// Crime type → categorical
const CRIME_TYPE_COLORS: Record<string, string> = {
  drugs: '#22c55e',
  robberies: '#3b82f6',
  violent: '#ef4444',
  other: '#a855f7',
}

// E33 percentage → scale
function colorForE33(p: number) {
  if (p > 0.4) return '#7f1d1d'
  if (p > 0.25) return '#b91c1c'
  if (p > 0.15) return '#f97316'
  if (p > 0.05) return '#facc15'
  return '#22c55e'
}

function colorForRegion(r: Region, metric: Metric) {
  if (metric === 'crime_level') return colorForCrimeLevel(r.crime_level)
  if (metric === 'e33_percent') return colorForE33(r.e33_percent)
  const key = (r.prevalent_crime_type || 'other').toLowerCase()
  return CRIME_TYPE_COLORS[key] || CRIME_TYPE_COLORS.other
}

function strokeWeightForIncidents(n: number) {
  if (n >= 40) return 4
  if (n >= 25) return 3
  if (n >= 10) return 2
  return 1
}

export default function App() {
  const [calls, setCalls] = useState<Call[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [regions, setRegions] = useState<Region[]>([])
  const [metric, setMetric] = useState<Metric>('incidents')
  const [month, setMonth] = useState<string>('2025-08')
  const [crimeType, setCrimeType] = useState<string>('')
  const [buurten, setBuurten] = useState<BuurtCollection | null>(null)

  // Load calls
  useEffect(() => {
    fetchCalls().then(setCalls).catch(console.error)
  }, [])

  // Load Groningen buurten GeoJSON (from public folder)
  useEffect(() => {
    fetch('/geo/groningen_buurten.geojson')
      .then(res => res.json())
      .then((data: BuurtCollection) => {
        // optional: filter to municipality Groningen
        const filtered: BuurtCollection = {
          type: 'FeatureCollection',
          features: data.features.filter(f => {
            const gm = f.properties?.GM_NAAM || ''
            return gm.toLowerCase().includes('groningen')
          }),
        }
        setBuurten(filtered)
      })
      .catch(err => {
        console.error('Failed to load buurten geojson', err)
        setBuurten(null)
      })
  }, [])

  const selectedCall = useMemo(
    () => calls.find(c => c.id === selectedId) ?? null,
    [calls, selectedId]
  )

  // Fetch regions near the selected call
  useEffect(() => {
    async function load() {
      if (!selectedCall || selectedCall.lat == null || selectedCall.lon == null) {
        setRegions([])
        return
      }
      const rows = await fetchRegionsNear(selectedCall.lat, selectedCall.lon, {
        radius_km: 6,
        month_year: month || undefined,
        crime_type: crimeType || undefined,
      })
      setRegions(rows)
    }
    load().catch(console.error)
  }, [selectedCall, month, crimeType])

  const center: LatLngExpression =
    selectedCall?.lat && selectedCall?.lon
      ? [selectedCall.lat, selectedCall.lon]
      : DEFAULT_CENTER

  // Helper: find matching buurt feature for a region
  const findBuurtForRegion = (name: string): BuurtFeature | null => {
    if (!buurten) return null
    const lower = name.toLowerCase()
    const feat = buurten.features.find(
      f => (f.properties?.BUURTNAAM || '').toLowerCase() === lower
    ) as BuurtFeature | undefined
    return feat || null
  }

  return (
    <div
      style={{
        padding: 16,
        fontFamily:
          'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      }}
    >
      <header
        style={{
          marginBottom: 12,
          paddingBottom: 8,
          borderBottom: '1px solid #e5e7eb',
          color: '#001e61',
        }}
      >
        <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>
          Groningen 112 – Crime & E33 Intelligence Map
        </h1>
        <p style={{ margin: '4px 0 0', fontSize: 12, color: '#4b5563' }}>
          Kies een 112-melding en bekijk buurtrisico’s, delicttype en mentale-crisis (E33) concentraties.
        </p>
      </header>

      {/* Control panel */}
      <div
        style={{
          marginBottom: 12,
          padding: 8,
          borderRadius: 8,
          border: '1px solid #e5e7eb',
          background: '#f9fafb',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 8,
            alignItems: 'center',
          }}
        >
          <label style={{ fontSize: 12, fontWeight: 600 }}>112-call:</label>
          <select
            value={selectedId ?? ''}
            onChange={e =>
              setSelectedId(e.target.value ? Number(e.target.value) : null)
            }
            style={{
              fontSize: 12,
              padding: '4px 8px',
              borderRadius: 6,
              border: '1px solid #d4d4d8',
              minWidth: 220,
            }}
          >
            <option value="">— Selecteer melding —</option>
            {calls.map(c => (
              <option key={c.id} value={c.id}>
                #{c.id} — {c.address}
              </option>
            ))}
          </select>

          <label style={{ fontSize: 12, fontWeight: 600 }}>Visualisatie:</label>
          <select
            value={metric}
            onChange={e => setMetric(e.target.value as Metric)}
            style={{
              fontSize: 12,
              padding: '4px 8px',
              borderRadius: 6,
              border: '1px solid #d4d4d8',
            }}
          >
            <option value="incidents">
              Delicttype (kleur) & incidenten (dikte)
            </option>
            <option value="crime_level">Crimeniveau (kleur)</option>
            <option value="e33_percent">E33 mentale-crisismeldingen (%)</option>
          </select>

          <label style={{ fontSize: 12, fontWeight: 600 }}>Maand:</label>
          <input
            value={month}
            onChange={e => setMonth(e.target.value)}
            placeholder="YYYY-MM"
            style={{
              fontSize: 12,
              padding: '4px 8px',
              borderRadius: 6,
              border: '1px solid #d4d4d8',
              width: 90,
            }}
          />

          <label style={{ fontSize: 12, fontWeight: 600 }}>Delicttype:</label>
          <input
            value={crimeType}
            onChange={e => setCrimeType(e.target.value)}
            placeholder="(leeg = alle)"
            style={{
              fontSize: 12,
              padding: '4px 8px',
              borderRadius: 6,
              border: '1px solid #d4d4d8',
              width: 140,
            }}
          />
        </div>

        <p style={{ margin: '6px 0 0', fontSize: 11, color: '#6b7280' }}>
          Polygonen tonen buurten rond de geselecteerde melding. Kleur en lijndikte laten risico
          en concentratie van incidenten en E33-meldingen zien.
        </p>
      </div>

      {/* Map + legend */}
      <div
        style={{
          borderRadius: 10,
          border: '1px solid #e5e7eb',
          background: '#ffffff',
          padding: 8,
        }}
      >
        <div style={{ height: 520, borderRadius: 8, overflow: 'hidden' }}>
          <MapContainer
            center={center}
            zoom={13}
            scrollWheelZoom
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="© OpenStreetMap"
            />

            {buurten &&
              regions.map(r => {
                const feat = findBuurtForRegion(r.name)
                if (!feat) return null

                const fillColor = colorForRegion(r, metric)
                const weight = strokeWeightForIncidents(r.incident_count)

                return (
                  <GeoJSON
                    key={r.id}
                    data={feat}
                    style={{
                      color: fillColor,
                      weight,
                      fillColor,
                      fillOpacity: 0.35,
                    }}
                    eventHandlers={{
                      add: e => {
                        e.target.bindTooltip(
                          `
<b>${r.name}</b><br/>
Maand: ${r.month_year}<br/>
Incidenten: ${r.incident_count}<br/>
E33: ${(r.e33_percent * 100).toFixed(1)}%<br/>
Delicttype: ${r.prevalent_crime_type}<br/>
Crimeniveau: ${r.crime_level}/5
                          `,
                          { sticky: true }
                        )
                      },
                    }}
                  />
                )
              })}
          </MapContainer>
        </div>

        {/* Legend */}
        <div
          style={{
            marginTop: 10,
            display: 'flex',
            flexWrap: 'wrap',
            gap: 24,
            fontSize: 12,
            color: '#4b5563',
          }}
        >
          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>
              Crimeniveau (kleur)
            </div>
            {[1, 2, 3, 4, 5].map(l => (
              <div
                key={l}
                style={{ display: 'flex', alignItems: 'center', gap: 6 }}
              >
                <span
                  style={{
                    width: 16,
                    height: 10,
                    borderRadius: 2,
                    backgroundColor: colorForCrimeLevel(l),
                  }}
                />
                <span>Niveau {l}</span>
              </div>
            ))}
          </div>

          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>
              Delicttype (kleur)
            </div>
            {[
              ['drugs', 'Drugs / overlast'],
              ['robberies', 'Diefstal / beroving'],
              ['violent', 'Geweld / agressie'],
              ['other', 'Overig / gemengd'],
            ].map(([key, label]) => (
              <div
                key={key}
                style={{ display: 'flex', alignItems: 'center', gap: 6 }}
              >
                <span
                  style={{
                    width: 16,
                    height: 10,
                    borderRadius: 2,
                    backgroundColor: CRIME_TYPE_COLORS[key],
                  }}
                />
                <span>{label}</span>
              </div>
            ))}
          </div>

          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>
              E33 mentale-crisis (%) – kleur
            </div>
            {[0.02, 0.08, 0.16, 0.30, 0.45].map(v => (
              <div
                key={v}
                style={{ display: 'flex', alignItems: 'center', gap: 6 }}
              >
                <span
                  style={{
                    width: 16,
                    height: 10,
                    borderRadius: 2,
                    backgroundColor: colorForE33(v),
                  }}
                />
                <span>{Math.round(v * 100)}%</span>
              </div>
            ))}
          </div>

          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>
              Incidenten (lijndikte)
            </div>
            <div>• Dunne rand: weinig incidenten</div>
            <div>• Dikke rand: veel incidenten</div>
          </div>
        </div>
      </div>
    </div>
  )
}
