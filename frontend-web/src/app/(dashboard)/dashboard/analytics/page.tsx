"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import {
  useDashboardStats,
  useOrdersByStatus,
  useDailyStats,
} from "@/hooks/use-analytics";
import { StatCard } from "@/components/ui/stat-card";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs } from "@/components/ui/tabs";
import {
  Package,
  Truck,
  CheckCircle,
  AlertTriangle,
  Clock,
  Users,
  Percent,
} from "lucide-react";
import { ORDER_STATUS_LABELS } from "@/constants";

const DailyTrendChart = dynamic(
  () => import("./charts").then((mod) => mod.DailyTrendChart),
  { ssr: false, loading: () => <div className="h-72 flex items-center justify-center text-gray-400 text-sm">Chargement...</div> }
);

const StatusPieChart = dynamic(
  () => import("./charts").then((mod) => mod.StatusPieChart),
  { ssr: false, loading: () => <div className="h-72 flex items-center justify-center text-gray-400 text-sm">Chargement...</div> }
);

const DEMO_COMPANY_ID = "00000000-0000-0000-0000-000000000001";

const PERIOD_TABS = [
  { value: "7", label: "7 jours" },
  { value: "14", label: "14 jours" },
  { value: "30", label: "30 jours" },
];

export default function AnalyticsPage() {
  const [period, setPeriod] = useState("7");
  const { data: stats } = useDashboardStats(DEMO_COMPANY_ID);
  const { data: byStatus } = useOrdersByStatus(DEMO_COMPANY_ID);
  const { data: daily } = useDailyStats(DEMO_COMPANY_ID, parseInt(period));

  const pieData =
    byStatus?.map((s) => ({
      name: ORDER_STATUS_LABELS[s.status] || s.status,
      value: s.count,
    })) || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display font-bold text-2xl text-gray-900 dark:text-white">
          Analytics
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Tableau de bord et indicateurs de performance
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total commandes"
          value={stats?.total_orders ?? "—"}
          change={stats ? `${stats.orders_today} aujourd'hui` : undefined}
          trend="up"
          icon={<Package className="w-5 h-5" />}
        />
        <StatCard
          label="En transit"
          value={stats?.in_transit ?? "—"}
          icon={<Truck className="w-5 h-5" />}
          iconColor="text-accent bg-accent/10"
        />
        <StatCard
          label="Livreurs disponibles"
          value={
            stats ? `${stats.available_couriers}/${stats.total_couriers}` : "—"
          }
          icon={<Users className="w-5 h-5" />}
          iconColor="text-secondary bg-secondary/10"
        />
        <StatCard
          label="Taux de completion"
          value={stats?.completion_rate ? `${stats.completion_rate}%` : "—"}
          icon={<Percent className="w-5 h-5" />}
          iconColor="text-success bg-success/10"
        />
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Tendances quotidiennes</CardTitle>
            <Tabs tabs={PERIOD_TABS} value={period} onChange={setPeriod} />
          </CardHeader>
          <DailyTrendChart data={daily || []} />
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Répartition par statut</CardTitle>
            <Badge variant="secondary">{pieData.length} statuts</Badge>
          </CardHeader>
          <StatusPieChart data={pieData} />
        </Card>
      </div>

      {/* Summary cards */}
      <div className="grid sm:grid-cols-3 gap-4">
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-success/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-success" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Terminees aujourd&apos;hui</p>
              <p className="font-display font-bold text-xl text-gray-900 dark:text-white tabular-nums">
                {stats?.completed_today ?? "—"}
              </p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-warning/10 flex items-center justify-center">
              <Clock className="w-5 h-5 text-warning" />
            </div>
            <div>
              <p className="text-sm text-gray-500">En attente</p>
              <p className="font-display font-bold text-xl text-gray-900 dark:text-white tabular-nums">
                {stats?.pending ?? "—"}
              </p>
            </div>
          </div>
        </Card>
        <Card padding="md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-error/10 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-error" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Echecs</p>
              <p className="font-display font-bold text-xl text-gray-900 dark:text-white tabular-nums">
                {stats?.failed ?? "—"}
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
