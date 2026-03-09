import React, { useEffect, useRef } from 'react'

interface GeoData {
  ip?: string
  latitude?: number
  longitude?: number
  city?: string
  country?: string
  country_code?: string
  isp?: string
  org?: string
  asn?: string
  region?: string
  timezone?: string
}

interface Props {
  geoip: { status: string; data?: GeoData }
  target: string
}

export default function TargetMap({ geoip, target }: Props) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)

  const geo = geoip?.data
  const hasCoords = geo?.latitude != null && geo?.longitude != null

  useEffect(() => {
    if (!hasCoords || !mapRef.current) return

    const lat = geo!.latitude!
    const lng = geo!.longitude!

    const initMap = () => {
      const L = (window as any).L
      if (!L || !mapRef.current) return

      // ALWAYS destroy previous map instance before creating new one
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }

      // Also clear any leftover leaflet state on the div
      const container = mapRef.current as any
      if (container._leaflet_id) {
        delete container._leaflet_id
      }

      const map = L.map(mapRef.current, {
        center: [lat, lng],
        zoom: 6,
        zoomControl: true,
        attributionControl: false,
      })

      mapInstanceRef.current = map

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
      }).addTo(map)

      const icon = L.divIcon({
        html: `
          <div style="
            width: 22px; height: 22px;
            background: #7c3aed;
            border: 3px solid #a78bfa;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            box-shadow: 0 0 12px rgba(124,58,237,0.9), 0 0 24px rgba(124,58,237,0.5);
          "></div>
        `,
        className: '',
        iconSize: [22, 22],
        iconAnchor: [11, 22],
        popupAnchor: [0, -26],
      })

      const popup = L.popup({
        className: 'phantom-popup',
        closeButton: false,
        offset: [0, -10],
      }).setContent(`
        <div style="
          background: #12121a;
          border: 1px solid #7c3aed;
          border-radius: 8px;
          padding: 10px 14px;
          font-family: monospace;
          min-width: 180px;
        ">
          <div style="color: #a78bfa; font-size: 13px; font-weight: 700; margin-bottom: 6px;">
            📍 ${target}
          </div>
          <div style="color: #94a3b8; font-size: 11px; line-height: 1.8;">
            ${geo!.city ? `<div>🏙 ${geo!.city}${geo!.region ? ', ' + geo!.region : ''}</div>` : ''}
            ${geo!.country ? `<div>🌍 ${geo!.country}</div>` : ''}
            ${geo!.isp ? `<div>🌐 ${geo!.isp}</div>` : ''}
            ${geo!.asn ? `<div>🔢 ${geo!.asn}</div>` : ''}
            <div style="color: #475569; margin-top: 4px; font-size: 10px;">
              ${lat.toFixed(4)}, ${lng.toFixed(4)}
            </div>
          </div>
        </div>
      `)

      L.marker([lat, lng], { icon })
        .addTo(map)
        .bindPopup(popup)
        .openPopup()

      L.circle([lat, lng], {
        color: '#7c3aed',
        fillColor: '#7c3aed',
        fillOpacity: 0.08,
        weight: 1,
        radius: 50000,
      }).addTo(map)

      // Force map to recalculate size after render
      setTimeout(() => map.invalidateSize(), 100)
    }

    // Load Leaflet CSS
    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link')
      link.id = 'leaflet-css'
      link.rel = 'stylesheet'
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'
      document.head.appendChild(link)
    }

    // Load Leaflet JS then init
    if ((window as any).L) {
      initMap()
    } else {
      const existing = document.getElementById('leaflet-js')
      if (existing) {
        // Script already loading — wait for it
        existing.addEventListener('load', initMap)
      } else {
        const script = document.createElement('script')
        script.id = 'leaflet-js'
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'
        script.onload = initMap
        document.head.appendChild(script)
      }
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [target, geo?.latitude, geo?.longitude]) // ← re-run when target OR coords change

  if (!geoip || geoip.status !== 'success' || !hasCoords) {
    return (
      <div style={{
        background: '#12121a', border: '1px solid #1e1e2e',
        borderRadius: 12, padding: 24, textAlign: 'center'
      }}>
        <span style={{ fontSize: 24 }}>🗺</span>
        <p style={{ color: '#334155', fontFamily: 'monospace', fontSize: 12, marginTop: 8 }}>
          No location data available
        </p>
      </div>
    )
  }

  return (
    <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, overflow: 'hidden' }}>

      {/* Header */}
      <div style={{
        padding: '12px 16px', borderBottom: '1px solid #1e1e2e',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 16 }}>🌍</span>
          <span style={{ fontFamily: 'monospace', fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>
            Target Location
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          {geo.city && (
            <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#a78bfa' }}>
              📍 {geo.city}{geo.country ? `, ${geo.country}` : ''}
            </span>
          )}
          {geo.isp && (
            <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#475569' }}>
              · {geo.isp}
            </span>
          )}
        </div>
      </div>

      {/* Map — key forces full remount when target changes */}
      <div
        key={`${target}-${geo.latitude}-${geo.longitude}`}
        ref={mapRef}
        style={{ height: 280, width: '100%', background: '#0a0a0f' }}
      />

      {/* Info bar */}
      <div style={{
        padding: '10px 16px', borderTop: '1px solid #1e1e2e',
        display: 'flex', gap: 20, flexWrap: 'wrap'
      }}>
        {[
          { icon: '🌐', label: 'ISP', value: geo.isp },
          { icon: '🏢', label: 'Org', value: geo.org },
          { icon: '🔢', label: 'ASN', value: geo.asn },
          { icon: '⏰', label: 'Timezone', value: geo.timezone },
        ].filter(i => i.value).map(item => (
          <div key={item.label}>
            <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155', textTransform: 'uppercase' }}>
              {item.icon} {item.label}
            </div>
            <div style={{ fontSize: 12, fontFamily: 'monospace', color: '#94a3b8', marginTop: 1 }}>
              {item.value}
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .phantom-popup .leaflet-popup-content-wrapper {
          background: transparent !important;
          box-shadow: none !important;
          padding: 0 !important;
        }
        .phantom-popup .leaflet-popup-content { margin: 0 !important; }
        .phantom-popup .leaflet-popup-tip-container { display: none !important; }
        .leaflet-control-zoom {
          border: 1px solid #1e1e2e !important;
          background: #12121a !important;
        }
        .leaflet-control-zoom a {
          background: #12121a !important;
          color: #a78bfa !important;
          border-bottom: 1px solid #1e1e2e !important;
        }
        .leaflet-control-zoom a:hover { background: #1e1e2e !important; }
      `}</style>
    </div>
  )
}
