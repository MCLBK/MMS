"use client";

import { useState } from "react";
import { useCompanies, useCreateCompany } from "@/hooks/use-companies";
import { DataTable } from "@/components/ui/data-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { Building2, Plus, MapPin } from "lucide-react";
import { useForm } from "react-hook-form";
import type { Company } from "@/types";

interface CompanyForm {
  name: string;
  slug: string;
  address: string;
  city: string;
  country: string;
  phone: string;
  email: string;
}

export default function CompaniesPage() {
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const { data: companies, isLoading } = useCompanies(page);
  const createCompany = useCreateCompany();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CompanyForm>();

  const onSubmit = async (formData: CompanyForm) => {
    await createCompany.mutateAsync(formData);
    setShowCreate(false);
    reset();
  };

  const columns = [
    {
      key: "name",
      header: "Nom",
      render: (c: Company) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Building2 className="w-4 h-4 text-primary" />
          </div>
          <div>
            <p className="font-display font-semibold text-gray-900 dark:text-white">
              {c.name}
            </p>
            <p className="text-xs text-gray-500">{c.slug}</p>
          </div>
        </div>
      ),
    },
    {
      key: "city",
      header: "Ville",
      render: (c: Company) => (
        <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
          <MapPin className="w-3.5 h-3.5" />
          <span>{c.city || "—"}, {c.country || "—"}</span>
        </div>
      ),
    },
    {
      key: "is_active",
      header: "Statut",
      render: (c: Company) => (
        <Badge variant={c.is_active ? "success" : "error"}>
          {c.is_active ? "Active" : "Inactive"}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display font-bold text-2xl text-gray-900 dark:text-white">
            Entreprises
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Gerez les entreprises de la plateforme
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle entreprise
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={companies || []}
        keyField="id"
        isLoading={isLoading}
        emptyIcon={<Building2 className="w-12 h-12" />}
        emptyMessage="Aucune entreprise"
        emptyDescription="Creez votre premiere entreprise pour commencer"
      />

      <Modal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        title="Nouvelle entreprise"
        description="Ajoutez une entreprise a la plateforme MMS Express"
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Nom"
              {...register("name", { required: "Nom requis" })}
              error={errors.name?.message}
            />
            <Input
              label="Slug"
              {...register("slug", {
                required: "Slug requis",
                pattern: {
                  value: /^[a-z0-9-]+$/,
                  message: "Minuscules, chiffres et tirets uniquement",
                },
              })}
              error={errors.slug?.message}
            />
          </div>
          <Input label="Adresse" {...register("address")} />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Ville" {...register("city")} />
            <Input label="Pays" {...register("country")} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Telephone" {...register("phone")} />
            <Input label="Email" type="email" {...register("email")} />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowCreate(false)}
            >
              Annuler
            </Button>
            <Button type="submit" isLoading={createCompany.isPending}>
              Creer
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
