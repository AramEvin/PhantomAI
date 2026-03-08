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
}

interface Props {
  geoip: { status: string; data?: GeoData }
  target: string
}

export default function TargetMap({ geoip, target }: Props) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)

  const geo = geoip?.data
  const hasCoords = geo?.latitude && geo?.longitude

  useEffect(() => {
    if (!hasCoords || !mapRef.current) return
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove()
      mapInstanceRef.current = null
    }

    // Dynamically load Leaflet
    const loadLeaflet = async () => {
      // Load CSS
      if (!document.getElementById('leaflet-css')) {
        const link = document.createElement('link')
        link.id = 'leaflet-css'
        link.rel = 'stylesheet'
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'
        document.head.appendChild(link)
      }

      // Load JS
      if (!(window as any).L) {
        await new Promise<void>((resolve) => {
          const script = document.createElement('script')
          script.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'
          script.onload = () => resolve()
          document.head.appendChild(script)
        })
      }

      const L = (window as any).L
      if (!mapRef.current || mapInstanceRef.current) return

      // Dark tile layer
      const map = L.map(mapRef.current, {
        center: [geo.latitude, geo.longitude],
        zoom: 6,
        zoomControl: true,
        attributionControl: false,
      })

      mapInstanceRef.current = map

      // Dark map tiles (CartoDB Dark Matter — free, no API key)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
      }).addTo(map)

      // Custom purple marker
      const icon = L.divIcon({
        html: `
          <div style="
            width: 24px; height: 24px;
            background: #7c3aed;
            border: 3px solid #a78bfa;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            box-shadow: 0 0 12px rgba(124,58,237,0.8), 0 0 24px rgba(124,58,237,0.4);
          "></div>
        `,
        className: '',
        iconSize: [24, 24],
        iconAnchor: [12, 24],
        popupAnchor: [0, -28],
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
            ${geo.city ? `<div>🏙 ${geo.city}${geo.region ? ', ' + geo.region : ''}</div>` : ''}
            ${geo.country ? `<div>🌍 ${geo.country}</div>` : ''}
            ${geo.isp ? `<div>🌐 ${geo.isp}</div>` : ''}
            ${geo.asn ? `<div>🔢 ${geo.asn}</div>` : ''}
            <div style="color: #475569; margin-top: 4px; font-size: 10px;">
              ${geo.latitude?.toFixed(4)}, ${geo.longitude?.toFixed(4)}
            </div>
          </div>
        </div>
      `)

      L.marker([geo.latitude, geo.longitude], { icon })
        .addTo(map)
        .bindPopup(popup)
        .openPopup()

      // Pulse circle
      L.circle([geo.latitude, geo.longitude], {
        color: '#7c3aed',
        fillColor: '#7c3aed',
        fillOpacity: 0.08,
        weight: 1,
        radius: 50000,
      }).addTo(map)
    }

    loadLeaflet()

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [geo?.latitude, geo?.longitude])

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
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 16 }}>🌍</span>
          <span style={{ fontFamily: 'monospace', fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>
            Target Location
          </span>
        </div>
        <div style={{ display: 'flex', align: 'center', gap: 10, flexWrap: 'wrap' }}>
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

      {/* Map container */}
      <div
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
          { icon: '⏰', label: 'Timezone', value: (geo as any).timezone },
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

      {/* Popup styles injected globally */}
      <style>{`
        .phantom-popup .leaflet-popup-content-wrapper {
          background: transparent !important;
          box-shadow: none !important;
          padding: 0 !important;
        }
        .phantom-popup .leaflet-popup-content {
          margin: 0 !important;
        }
        .phantom-popup .leaflet-popup-tip-container {
          display: none !important;
        }
        .leaflet-control-zoom {
          border: 1px solid #1e1e2e !important;
          background: #12121a !important;
        }
        .leaflet-control-zoom a {
          background: #12121a !important;
          color: #a78bfa !important;
          border-bottom: 1px solid #1e1e2e !important;
        }
        .leaflet-control-zoom a:hover {
          background: #1e1e2e !important;
        }
      `}</style>
    </div>
  )
}
