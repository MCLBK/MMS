"use client";

import { useMemo } from "react";
import dynamic from "next/dynamic";
import { useLivePositions, type CourierPosition } from "@/hooks/use-tracking";
import { StatCard } from "@/components/ui/stat-card";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import {
  MapPin,
  Truck,
  Battery,
  Gauge,
  Users,
  Wifi,
} from "lucide-react";
import { COURIER_STATUS_LABELS, COURIER_STATUS_VARIANTS } from "@/constants";

const DEMO_COMPANY_ID = "00000000-0000-0000-0000-000000000001";

const MapView = dynamic(() => import("./map-view"), { ssr: false });

export default function TrackingPage() {
  const { data: positions, isLoading } = useLivePositions(DEMO_COMPANY_ID);

  const available = positions?.filter((p) => p.status === "available").length ?? 0;
  const busy = positions?.filter((p) => p.status === "busy").length ?? 0;
  const total = positions?.length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display font-bold text-2xl text-gray-900 dark:text-white">
          Suivi GPS
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Positions en temps reel de vos livreurs
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Livreurs en ligne"
          value={total}
          icon={<Users className="w-5 h-5" />}
        />
        <StatCard
          label="Disponibles"
          value={available}
          icon={<Wifi className="w-5 h-5" />}
          iconColor="text-success bg-success/10"
        />
        <StatCard
          label="En course"
          value={busy}
          icon={<Truck className="w-5 h-5" />}
          iconColor="text-warning bg-warning/10"
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Carte en direct</CardTitle>
              <Badge variant="accent">Rafraichissement 5s</Badge>
            </CardHeader>
            <div className="h-[500px] rounded-b-[10px] overflow-hidden">
              <MapView positions={positions || []} />
            </div>
          </Card>
        </div>

        {/* Courier list */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Livreurs</CardTitle>
              <Badge variant="default">{total}</Badge>
            </CardHeader>
            <div className="max-h-[500px] overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
              {(!positions || positions.length === 0) && (
                <div className="p-8 text-center text-gray-400">
                  <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Aucun livreur en ligne</p>
                </div>
              )}
              {positions?.map((p) => (
                <div
                  key={p.courier_id}
                  className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-surface-dark-alt transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-display font-semibold text-sm text-gray-900 dark:text-white">
                      {p.courier_name}
                    </span>
                    <Badge
                      variant={
                        (COURIER_STATUS_VARIANTS[p.status] as any) || "default"
                      }
                    >
                      {COURIER_STATUS_LABELS[p.status] || p.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {p.latitude.toFixed(4)}, {p.longitude.toFixed(4)}
                    </span>
                    {p.speed_kmh != null && (
                      <span className="flex items-center gap-1">
                        <Gauge className="w-3 h-3" />
                        {p.speed_kmh} km/h
                      </span>
                    )}
                    {p.battery_level != null && (
                      <span className="flex items-center gap-1">
                        <Battery className="w-3 h-3" />
                        {p.battery_level}%
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
