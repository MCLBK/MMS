"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { CourierPosition } from "@/hooks/use-tracking";

interface MapViewProps {
  positions: CourierPosition[];
}

const STATUS_COLORS: Record<string, string> = {
  available: "#22C55E",
  busy: "#F59E0B",
  offline: "#94A3B8",
};

function createCourierIcon(status: string) {
  const color = STATUS_COLORS[status] || STATUS_COLORS.offline;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
    <circle cx="16" cy="16" r="14" fill="${color}" stroke="white" stroke-width="3"/>
    <circle cx="16" cy="16" r="5" fill="white"/>
  </svg>`;

  return L.divIcon({
    html: svg,
    className: "",
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -18],
  });
}

export default function MapView({ positions }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const markersRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    mapInstance.current = L.map(mapRef.current, {
      center: [5.3484, -4.0167],
      zoom: 13,
      zoomControl: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 19,
    }).addTo(mapInstance.current);

    markersRef.current = L.layerGroup().addTo(mapInstance.current);

    return () => {
      mapInstance.current?.remove();
      mapInstance.current = null;
    };
  }, []);

  useEffect(() => {
    if (!markersRef.current || !mapInstance.current) return;
    markersRef.current.clearLayers();

    positions.forEach((p) => {
      const marker = L.marker([p.latitude, p.longitude], {
        icon: createCourierIcon(p.status),
      });
      marker.bindPopup(
        `<div style="font-family:sans-serif;font-size:13px;">
          <strong>${p.courier_name}</strong><br/>
          ${p.status === "available" ? "Disponible" : p.status === "busy" ? "En course" : "Hors ligne"}
          ${p.speed_kmh != null ? `<br/>${p.speed_kmh} km/h` : ""}
          ${p.battery_level != null ? `<br/>Batterie: ${p.battery_level}%` : ""}
        </div>`
      );
      markersRef.current!.addLayer(marker);
    });

    if (positions.length > 0) {
      const bounds = L.latLngBounds(
        positions.map((p) => [p.latitude, p.longitude] as L.LatLngTuple)
      );
      mapInstance.current.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
    }
  }, [positions]);

  return <div ref={mapRef} className="w-full h-full" />;
}
