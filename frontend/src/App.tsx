import React, { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'
import type { LatLngExpression } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { fetchCalls, fetchRegionsNear, type Call, type Region } from './api'

const DEFAULT_CENTER: LatLngExpression = [52.3728, 4.8936] // Amsterdam center

function colorForCrimeLevel(level:number){
  // 1..5 -> green to red
  const colors = ['#16a34a','#84cc16','#f59e0b','#f97316','#ef4444']
  return colors[Math.min(Math.max(level-1,0),4)]
}

function radiusForIncidents(n:number){
  // scale marker size by incident count
  const r = 6 + Math.sqrt(Math.max(n, 1))
  return Math.min(r, 22)
}

export default function App(){
  const [calls, setCalls] = useState<Call[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [regions, setRegions] = useState<Region[]>([])
  const [metric, setMetric] = useState<'incidents'|'crime_level'>('incidents')
  const [month, setMonth] = useState<string>('2025-08')
  const [crimeType, setCrimeType] = useState<string>('')

  useEffect(() => {
    fetchCalls().then(setCalls).catch(console.error)
  }, [])

  const selectedCall = useMemo(() =>
    calls.find(c => c.id === selectedId) ?? null, [calls, selectedId])

  useEffect(() => {
    async function load() {
      if (!selectedCall || selectedCall.lat == null || selectedCall.lon == null) {
        setRegions([])
        return
      }
      const rows = await fetchRegionsNear(selectedCall.lat, selectedCall.lon, {
        radius_km: 3,
        month_year: month || undefined,
        crime_type: crimeType || undefined,
      })
      setRegions(rows)
    }
    load().catch(console.error)
  }, [selectedCall, month, crimeType])

  const center: LatLngExpression = selectedCall?.lat && selectedCall?.lon
    ? [selectedCall.lat, selectedCall.lon]
    : DEFAULT_CENTER

  return (
    <div style={{padding:16}}>
      <h2 style={{margin:'4px 0 12px', color:'#001e61'}}>City Safety Map (Demo)</h2>

      <div className="panel" style={{marginBottom:12}}>
        <div className="row" style={{marginBottom:8}}>
          <label className="label">Kies 112-call:</label>
          <select
            className="select"
            value={selectedId ?? ''}
            onChange={e => setSelectedId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">— Selecteer —</option>
            {calls.map(c => (
              <option key={c.id} value={c.id}>
                #{c.id} — {c.address}
              </option>
            ))}
          </select>

          <label className="label">Heatmap:</label>
          <select className="select" value={metric} onChange={e => setMetric(e.target.value as any)}>
            <option value="incidents"># 112-incidenten</option>
            <option value="crime_level">Crimeniveau</option>
          </select>

          <label className="label">Maand:</label>
          <input
            className="input"
            placeholder="YYYY-MM"
            value={month}
            onChange={e => setMonth(e.target.value)}
          />

          <label className="label">Delicttype:</label>
          <input
            className="input"
            placeholder="(leeg = alle)"
            value={crimeType}
            onChange={e => setCrimeType(e.target.value)}
          />
        </div>
        <div className="legend">
          • Kleur = crimeniveau (groen → rood). • Grootte = aantal incidenten. • Filters passen data live aan.
        </div>
      </div>

      <div className="panel">
        <div style={{height:520, borderRadius:10, overflow:'hidden'}}>
          <MapContainer center={center} zoom={13} scrollWheelZoom={true} style={{height:'100%', width:'100%'}}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="© OpenStreetMap"
            />
            {regions.map(r => {
              const color = colorForCrimeLevel(r.crime_level)
              const radius = metric === 'incidents'
                ? radiusForIncidents(r.incident_count)
                : 6 + (r.crime_level * 2)
              return (
                <CircleMarker
                  key={r.id}
                  center={[r.center_lat, r.center_lon]}
                  pathOptions={{color, fillColor: color, fillOpacity: 0.25}}
                  radius={radius}
                >
                  <Tooltip direction="top" opacity={0.9}>
                    <div>
                      <div><b>{r.name}</b> ({r.month_year})</div>
                      <div>Crimeniveau: {r.crime_level} / 5</div>
                      <div>Incidenten: {r.incident_count}</div>
                      <div>Type: {r.prevalent_crime_type}</div>
                    </div>
                  </Tooltip>
                </CircleMarker>
              )
            })}
          </MapContainer>
        </div>
      </div>
    </div>
  )
}
