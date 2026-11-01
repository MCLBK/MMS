"use client";

import { useState } from "react";
import { useOrders, useCreateOrder } from "@/hooks/use-orders";
import { DataTable } from "@/components/ui/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Tabs } from "@/components/ui/tabs";
import {
  Package,
  Plus,
  Search,
  MapPin,
  Clock,
} from "lucide-react";
import { useForm } from "react-hook-form";
import {
  ORDER_STATUS_LABELS,
  ORDER_STATUS_VARIANTS,
  PRIORITY_LABELS,
  PRIORITY_VARIANTS,
} from "@/constants";
import type { OrderListItem } from "@/types";

const DEMO_COMPANY_ID = "00000000-0000-0000-0000-000000000001";

const STATUS_TABS = [
  { value: "all", label: "Toutes" },
  { value: "draft", label: "Brouillon" },
  { value: "pending", label: "En attente" },
  { value: "in_transit", label: "En transit" },
  { value: "delivered", label: "Livrees" },
  { value: "completed", label: "Terminees" },
];

interface OrderForm {
  customer_name: string;
  customer_phone: string;
  pickup_address: string;
  delivery_address: string;
  priority: string;
  special_instructions: string;
}

export default function OrdersPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  const { data, isLoading } = useOrders(
    DEMO_COMPANY_ID,
    page,
    20,
    statusFilter === "all" ? undefined : statusFilter,
    search || undefined
  );

  const createOrder = useCreateOrder(DEMO_COMPANY_ID);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<OrderForm>();

  const onSubmit = async (formData: OrderForm) => {
    await createOrder.mutateAsync({
      new_customer: {
        name: formData.customer_name,
        phone: formData.customer_phone,
      },
      pickup_address: formData.pickup_address,
      delivery_address: formData.delivery_address,
      priority: formData.priority || "normal",
      special_instructions: formData.special_instructions || null,
      items: [],
    });
    setShowCreate(false);
    reset();
  };

  const columns = [
    {
      key: "reference",
      header: "Reference",
      render: (o: OrderListItem) => (
        <span className="font-mono font-semibold text-primary dark:text-accent text-xs">
          {o.reference}
        </span>
      ),
    },
    {
      key: "customer_name",
      header: "Client",
      render: (o: OrderListItem) => (
        <span className="font-medium text-gray-900 dark:text-white">
          {o.customer_name}
        </span>
      ),
    },
    {
      key: "status",
      header: "Statut",
      render: (o: OrderListItem) => (
        <Badge variant={ORDER_STATUS_VARIANTS[o.status] as any}>
          {ORDER_STATUS_LABELS[o.status]}
        </Badge>
      ),
    },
    {
      key: "priority",
      header: "Priorite",
      render: (o: OrderListItem) => (
        <Badge variant={PRIORITY_VARIANTS[o.priority] as any}>
          {PRIORITY_LABELS[o.priority]}
        </Badge>
      ),
    },
    {
      key: "pickup_address",
      header: "Enlevement",
      render: (o: OrderListItem) => (
        <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 max-w-[200px] truncate">
          <MapPin className="w-3.5 h-3.5 flex-shrink-0 text-success" />
          <span className="truncate">{o.pickup_address}</span>
        </div>
      ),
    },
    {
      key: "delivery_address",
      header: "Livraison",
      render: (o: OrderListItem) => (
        <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 max-w-[200px] truncate">
          <MapPin className="w-3.5 h-3.5 flex-shrink-0 text-error" />
          <span className="truncate">{o.delivery_address}</span>
        </div>
      ),
    },
    {
      key: "created_at",
      header: "Date",
      render: (o: OrderListItem) => (
        <div className="flex items-center gap-1.5 text-gray-500 text-xs">
          <Clock className="w-3.5 h-3.5" />
          {new Date(o.created_at).toLocaleDateString("fr-FR", {
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display font-bold text-2xl text-gray-900 dark:text-white">
            Commandes
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {data?.total ?? 0} commande{(data?.total ?? 0) > 1 ? "s" : ""} au total
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle commande
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <Tabs
          tabs={STATUS_TABS}
          value={statusFilter}
          onChange={(v) => {
            setStatusFilter(v);
            setPage(1);
          }}
        />
        <div className="relative w-full sm:w-72 ml-auto">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="input-field pl-10 text-sm"
          />
        </div>
      </div>

      <DataTable
        columns={columns}
        data={data?.items || []}
        keyField="id"
        page={page}
        totalPages={data?.total_pages || 1}
        onPageChange={setPage}
        isLoading={isLoading}
        emptyIcon={<Package className="w-12 h-12" />}
        emptyMessage="Aucune commande"
        emptyDescription="Creez votre premiere commande de livraison"
      />

      <Modal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        title="Nouvelle commande"
        description="Creez une commande de livraison"
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div className="space-y-1">
            <h3 className="font-display font-semibold text-sm text-gray-900 dark:text-white">
              Client
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Nom du client"
                {...register("customer_name", { required: "Nom requis" })}
                error={errors.customer_name?.message}
              />
              <Input
                label="Telephone"
                {...register("customer_phone", { required: "Telephone requis" })}
                error={errors.customer_phone?.message}
              />
            </div>
          </div>

          <div className="space-y-1">
            <h3 className="font-display font-semibold text-sm text-gray-900 dark:text-white">
              Adresses
            </h3>
            <Input
              label="Adresse d'enlevement"
              {...register("pickup_address", { required: "Adresse requise" })}
              error={errors.pickup_address?.message}
            />
            <Input
              label="Adresse de livraison"
              {...register("delivery_address", { required: "Adresse requise" })}
              error={errors.delivery_address?.message}
            />
          </div>

          <Select
            label="Priorite"
            options={[
              { value: "low", label: "Faible" },
              { value: "normal", label: "Normale" },
              { value: "high", label: "Haute" },
              { value: "urgent", label: "Urgente" },
            ]}
            defaultValue="normal"
            {...register("priority")}
          />

          <Textarea
            label="Instructions speciales"
            placeholder="Ex: Ne pas sonner, appeler le client..."
            {...register("special_instructions")}
          />

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowCreate(false)}
            >
              Annuler
            </Button>
            <Button type="submit" isLoading={createOrder.isPending}>
              Creer la commande
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
