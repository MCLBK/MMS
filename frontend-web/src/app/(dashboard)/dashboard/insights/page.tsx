"use client";

import { useVolumeForecast, useHotZones, type VolumeForecast, type HotZone } from "@/hooks/use-ai";
import { StatCard } from "@/components/ui/stat-card";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Brain,
  TrendingUp,
  TrendingDown,
  Minus,
  MapPin,
  Calendar,
  BarChart3,
  Flame,
  Target,
  Zap,
} from "lucide-react";

const DEMO_COMPANY_ID = "00000000-0000-0000-0000-000000000001";

const DEMAND_COLORS: Record<string, string> = {
  high: "text-error bg-error/10",
  medium: "text-warning bg-warning/10",
  low: "text-success bg-success/10",
};

const DEMAND_LABELS: Record<string, string> = {
  high: "Forte",
  medium: "Moyenne",
  low: "Faible",
};

const TREND_ICONS: Record<string, typeof TrendingUp> = {
  up: TrendingUp,
  down: TrendingDown,
  stable: Minus,
};

export default function InsightsPage() {
  const { data: forecast } = useVolumeForecast(DEMO_COMPANY_ID, 7);
  const { data: hotZones } = useHotZones(DEMO_COMPANY_ID, 7);

  const totalPredicted = forecast?.reduce((sum, f) => sum + f.predicted_orders, 0) ?? 0;
  const avgConfidence = forecast?.length
    ? Math.round(
        (forecast.reduce((sum, f) => sum + f.confidence, 0) / forecast.length) * 100
      )
    : 0;
  const trend = forecast?.[0]?.trend || "stable";
  const highDemandZones = hotZones?.filter((z) => z.demand_level === "high").length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-secondary flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-display font-bold text-2xl text-gray-900 dark:text-white">
            Insights IA
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Prédictions et analyses intelligentes
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Volume prédit (7j)"
          value={totalPredicted}
          icon={<BarChart3 className="w-5 h-5" />}
          change={trend === "up" ? "Tendance hausse" : trend === "down" ? "Tendance baisse" : "Stable"}
          trend={trend === "up" ? "up" : trend === "down" ? "down" : "neutral"}
        />
        <StatCard
          label="Confiance moyenne"
          value={`${avgConfidence}%`}
          icon={<Target className="w-5 h-5" />}
          iconColor="text-accent bg-accent/10"
        />
        <StatCard
          label="Zones chaudes"
          value={hotZones?.length ?? 0}
          icon={<Flame className="w-5 h-5" />}
          iconColor="text-error bg-error/10"
        />
        <StatCard
          label="Zones forte demande"
          value={highDemandZones}
          icon={<Zap className="w-5 h-5" />}
          iconColor="text-warning bg-warning/10"
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Volume Forecast */}
        <Card>
          <CardHeader>
            <CardTitle>
              <Calendar className="w-4 h-4 inline mr-2" />
              Prévisions de volume
            </CardTitle>
            <Badge variant="accent">7 jours</Badge>
          </CardHeader>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {forecast?.map((f) => {
              const TrendIcon = TREND_ICONS[f.trend] || Minus;
              const dayName = new Date(f.date).toLocaleDateString("fr-FR", {
                weekday: "short",
                day: "numeric",
                month: "short",
              });
              return (
                <div key={f.date} className="px-4 py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <TrendIcon
                      className={`w-4 h-4 ${
                        f.trend === "up"
                          ? "text-success"
                          : f.trend === "down"
                          ? "text-error"
                          : "text-gray-400"
                      }`}
                    />
                    <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                      {dayName}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="font-display font-bold text-lg tabular-nums text-gray-900 dark:text-white">
                      {f.predicted_orders}
                    </span>
                    <div className="w-20">
                      <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-accent rounded-full transition-all"
                          style={{ width: `${f.confidence * 100}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-gray-400 mt-0.5 text-right">
                        {Math.round(f.confidence * 100)}%
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
            {(!forecast || forecast.length === 0) && (
              <div className="p-8 text-center text-gray-400">
                <BarChart3 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Les prévisions apparaîtront avec plus de données</p>
              </div>
            )}
          </div>
        </Card>

        {/* Hot Zones */}
        <Card>
          <CardHeader>
            <CardTitle>
              <MapPin className="w-4 h-4 inline mr-2" />
              Zones à forte demande
            </CardTitle>
            <Badge variant="secondary">{hotZones?.length ?? 0} zones</Badge>
          </CardHeader>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {hotZones?.map((zone, i) => (
              <div key={i} className="px-4 py-3">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${DEMAND_COLORS[zone.demand_level] || "text-gray-500 bg-gray-100"}`}
                    >
                      {i + 1}
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      Zone {i + 1}
                    </span>
                  </div>
                  <Badge
                    variant={
                      zone.demand_level === "high"
                        ? "error"
                        : zone.demand_level === "medium"
                        ? "warning"
                        : ("success" as any)
                    }
                  >
                    {DEMAND_LABELS[zone.demand_level] || zone.demand_level}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500 ml-8">
                  <span>{zone.order_count} commandes</span>
                  <span>Rayon {zone.radius_km} km</span>
                  <span>
                    {zone.center_lat.toFixed(4)}, {zone.center_lng.toFixed(4)}
                  </span>
                </div>
              </div>
            ))}
            {(!hotZones || hotZones.length === 0) && (
              <div className="p-8 text-center text-gray-400">
                <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Pas assez de données pour identifier les zones</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
