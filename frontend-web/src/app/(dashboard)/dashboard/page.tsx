"use client";

import Link from "next/link";
import {
  Package,
  Truck,
  CheckCircle,
  AlertTriangle,
  Clock,
  TrendingUp,
  ArrowRight,
  Plus,
  MapPin,
  Building2,
  Users,
  Zap,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/ui/stat-card";
import { useAuthStore } from "@/store/auth";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-gray-900 dark:text-white">
            Bonjour, {user?.first_name}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Voici un apercu de vos operations de livraison.
          </p>
        </div>
        <Link href="/dashboard/orders">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Nouvelle commande
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Livraisons en cours"
          value="—"
          icon={<Truck className="w-5 h-5" />}
          iconColor="text-accent bg-accent/10"
        />
        <StatCard
          label="Terminees aujourd'hui"
          value="—"
          icon={<CheckCircle className="w-5 h-5" />}
          iconColor="text-success bg-success/10"
        />
        <StatCard
          label="En attente"
          value="—"
          icon={<Clock className="w-5 h-5" />}
          iconColor="text-warning bg-warning/10"
        />
        <StatCard
          label="Incidents"
          value="—"
          icon={<AlertTriangle className="w-5 h-5" />}
          iconColor="text-error bg-error/10"
        />
      </div>

      {/* Quick actions */}
      <div className="grid sm:grid-cols-3 gap-4">
        {[
          {
            title: "Entreprises",
            desc: "Gerez les entreprises clientes",
            icon: Building2,
            href: "/dashboard/companies",
            color: "text-primary bg-primary/10",
          },
          {
            title: "Livreurs",
            desc: "Suivez votre flotte de livreurs",
            icon: Users,
            href: "/dashboard/couriers",
            color: "text-accent bg-accent/10",
          },
          {
            title: "Suivi GPS",
            desc: "Carte en temps reel",
            icon: MapPin,
            href: "/dashboard/tracking",
            color: "text-success bg-success/10",
          },
        ].map((action) => (
          <Link key={action.href} href={action.href}>
            <div className="bg-white dark:bg-surface-dark border border-gray-200 dark:border-gray-700 rounded-[10px] p-5 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 group cursor-pointer">
              <div className="flex items-center gap-4">
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${action.color}`}>
                  <action.icon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-display font-semibold text-gray-900 dark:text-white group-hover:text-primary dark:group-hover:text-accent transition-colors">
                    {action.title}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{action.desc}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-accent transition-colors" />
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Content cards */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Dernieres commandes</CardTitle>
            <Badge variant="accent">Temps reel</Badge>
          </CardHeader>
          <div className="flex items-center justify-center h-48 text-gray-400 dark:text-gray-500">
            <div className="text-center">
              <Package className="w-10 h-10 mx-auto mb-3 opacity-50" />
              <p className="text-sm">Les commandes apparaitront ici</p>
              <p className="text-xs text-gray-400 mt-1">
                Connectez le backend pour voir les donnees
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Performances</CardTitle>
            <Badge variant="secondary">7 derniers jours</Badge>
          </CardHeader>
          <div className="flex items-center justify-center h-48 text-gray-400 dark:text-gray-500">
            <div className="text-center">
              <TrendingUp className="w-10 h-10 mx-auto mb-3 opacity-50" />
              <p className="text-sm">Graphiques de performance</p>
              <p className="text-xs text-gray-400 mt-1">
                Les analytics seront disponibles avec les donnees
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Activity timeline placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Activite recente</CardTitle>
        </CardHeader>
        <div className="space-y-4 p-1">
          {[
            { icon: Zap, text: "Systeme initialise et pret", time: "Maintenant", color: "text-success" },
            { icon: Building2, text: "Configuration multi-tenant active", time: "Systeme", color: "text-primary" },
            { icon: Truck, text: "Module attribution IA charge", time: "Systeme", color: "text-accent" },
          ].map((event, i) => (
            <div key={i} className="flex items-center gap-4 py-2">
              <div className={`w-8 h-8 rounded-full bg-gray-100 dark:bg-surface-dark-alt flex items-center justify-center flex-shrink-0`}>
                <event.icon className={`w-4 h-4 ${event.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 dark:text-gray-300">{event.text}</p>
              </div>
              <span className="text-xs text-gray-400 flex-shrink-0">{event.time}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
