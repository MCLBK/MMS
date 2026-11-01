"use client";

import { useState } from "react";
import { useCouriers } from "@/hooks/use-couriers";
import { DataTable } from "@/components/ui/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";
import { StatCard } from "@/components/ui/stat-card";
import {
  Truck,
  Plus,
  Star,
  Package,
  Users,
  Zap,
} from "lucide-react";
import {
  VEHICLE_TYPE_LABELS,
  COURIER_STATUS_LABELS,
  COURIER_STATUS_VARIANTS,
} from "@/constants";
import type { CourierListItem } from "@/types";

const DEMO_COMPANY_ID = "00000000-0000-0000-0000-000000000001";

const STATUS_TABS = [
  { value: "all", label: "Tous" },
  { value: "available", label: "Disponibles" },
  { value: "busy", label: "Occupes" },
  { value: "offline", label: "Hors ligne" },
];

export default function CouriersPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("all");

  const { data: couriers, isLoading } = useCouriers(
    DEMO_COMPANY_ID,
    page,
    20,
    statusFilter === "all" ? undefined : statusFilter
  );

  const available = couriers?.filter((c) => c.status === "available").length ?? 0;
  const busy = couriers?.filter((c) => c.status === "busy").length ?? 0;
  const total = couriers?.length ?? 0;

  const columns = [
    {
      key: "user_name",
      header: "Livreur",
      render: (c: CourierListItem) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
            <Truck className="w-4 h-4 text-accent" />
          </div>
          <div>
            <p className="font-display font-semibold text-gray-900 dark:text-white">
              {c.user_name}
            </p>
            <p className="text-xs text-gray-500">
              {VEHICLE_TYPE_LABELS[c.vehicle_type]}
            </p>
          </div>
        </div>
      ),
    },
    {
      key: "status",
      header: "Statut",
      render: (c: CourierListItem) => (
        <Badge variant={COURIER_STATUS_VARIANTS[c.status] as any}>
          {COURIER_STATUS_LABELS[c.status]}
        </Badge>
      ),
    },
    {
      key: "rating",
      header: "Note",
      render: (c: CourierListItem) => (
        <div className="flex items-center gap-1.5">
          <Star className="w-3.5 h-3.5 text-yellow-500 fill-yellow-500" />
          <span className="font-semibold tabular-nums">{c.rating.toFixed(1)}</span>
        </div>
      ),
    },
    {
      key: "total_deliveries",
      header: "Livraisons",
      render: (c: CourierListItem) => (
        <span className="font-semibold tabular-nums">
          {c.total_deliveries}
        </span>
      ),
    },
    {
      key: "is_active",
      header: "Actif",
      render: (c: CourierListItem) => (
        <Badge variant={c.is_active ? "success" : "default"}>
          {c.is_active ? "Oui" : "Non"}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display font-bold text-2xl text-gray-900 dark:text-white">
            Livreurs
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Gerez votre flotte de livreurs
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Ajouter un livreur
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Total livreurs"
          value={total}
          icon={<Users className="w-5 h-5" />}
        />
        <StatCard
          label="Disponibles"
          value={available}
          icon={<Zap className="w-5 h-5" />}
          iconColor="text-success bg-success/10"
        />
        <StatCard
          label="En course"
          value={busy}
          icon={<Package className="w-5 h-5" />}
          iconColor="text-warning bg-warning/10"
        />
      </div>

      <Tabs
        tabs={STATUS_TABS}
        value={statusFilter}
        onChange={(v) => {
          setStatusFilter(v);
          setPage(1);
        }}
      />

      <DataTable
        columns={columns}
        data={couriers || []}
        keyField="id"
        isLoading={isLoading}
        emptyIcon={<Truck className="w-12 h-12" />}
        emptyMessage="Aucun livreur"
        emptyDescription="Ajoutez votre premier livreur a la flotte"
      />
    </div>
  );
}
