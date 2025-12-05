// frontend/src/api.ts
export type Call = {
  id: number
  address: string
  transcript: string
  lat: number
  lon: number
  is_e33: boolean
}

export type Region = {
  id: number
  name: string
  center_lat: number
  center_lon: number
  crime_level: number
  incident_count: number
  e33_count: number
  e33_percent: number
  month_year: string
  prevalent_crime_type: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

export async function fetchCalls(): Promise<Call[]> {
  const res = await fetch(`${API_BASE}/calls`)
  if (!res.ok) throw new Error(`Failed to fetch calls: ${res.status}`)
  return res.json()
}

type RegionFilter = {
  radius_km?: number
  month_year?: string
  crime_type?: string
}

export async function fetchRegionsNear(
  lat: number,
  lon: number,
  filters: RegionFilter = {}
): Promise<Region[]> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
  })

  if (filters.radius_km) params.set('radius_km', String(filters.radius_km))
  if (filters.month_year) params.set('month_year', filters.month_year)
  if (filters.crime_type) params.set('crime_type', filters.crime_type)

  const res = await fetch(`${API_BASE}/regions/near?${params.toString()}`)
  if (!res.ok) throw new Error(`Failed to fetch regions: ${res.status}`)
  return res.json()
}
