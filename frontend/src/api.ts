export type Call = { id:number; call_log:string; address:string; lat?:number; lon?:number }
export type Region = {
  id:number; name:string; center_lat:number; center_lon:number;
  crime_level:number; incident_count:number; month_year:string; prevalent_crime_type:string
}

const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8001'

export async function fetchCalls(): Promise<Call[]> {
  const r = await fetch(`${BASE}/calls`)
  if (!r.ok) throw new Error('calls fetch failed')
  return r.json()
}

export async function fetchRegionsNear(
  lat:number, lon:number,
  params: { radius_km?:number; month_year?:string; crime_type?:string } = {}
): Promise<Region[]> {
  const url = new URL(`${BASE}/regions/near`)
  url.searchParams.set('lat', String(lat))
  url.searchParams.set('lon', String(lon))
  if (params.radius_km) url.searchParams.set('radius_km', String(params.radius_km))
  if (params.month_year) url.searchParams.set('month_year', params.month_year)
  if (params.crime_type) url.searchParams.set('crime_type', params.crime_type)
  const r = await fetch(url)
  if (!r.ok) throw new Error('regions fetch failed')
  return r.json()
}
