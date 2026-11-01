"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import {
  LayoutDashboard,
  Building2,
  Users,
  Package,
  Truck,
  MapPin,
  BarChart3,
  Bell,
  Settings,
  LogOut,
  MessageSquare,
  Shield,
  Menu,
  X,
  Brain,
} from "lucide-react";
import { useState } from "react";
import { clsx } from "clsx";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  roles?: string[];
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Entreprises", href: "/dashboard/companies", icon: Building2, roles: ["super_admin"] },
  { label: "Utilisateurs", href: "/dashboard/users", icon: Users },
  { label: "Commandes", href: "/dashboard/orders", icon: Package },
  { label: "Livreurs", href: "/dashboard/couriers", icon: Truck },
  { label: "Suivi GPS", href: "/dashboard/tracking", icon: MapPin },
  { label: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { label: "Notifications", href: "/dashboard/notifications", icon: Bell },
  { label: "Assistant IA", href: "/dashboard/assistant", icon: MessageSquare },
  { label: "Insights IA", href: "/dashboard/insights", icon: Brain },
  { label: "Audit", href: "/dashboard/audit", icon: Shield, roles: ["super_admin"] },
  { label: "Parametres", href: "/dashboard/settings", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isLoading, isAuthenticated, fetchUser, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg dark:bg-bg-dark">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-3 border-accent border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-500 font-display">Chargement...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) return null;

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-bg dark:bg-bg-dark flex">
      {/* Sidebar overlay (mobile) */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          "fixed lg:sticky top-0 left-0 h-screen w-64 bg-white dark:bg-surface-dark",
          "border-r border-gray-200 dark:border-gray-700 flex flex-col z-50",
          "transition-transform duration-200 lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-gray-200 dark:border-gray-700">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Truck className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-base text-primary dark:text-white">
              MMS<span className="text-accent">Express</span>
            </span>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setSidebarOpen(false)}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                         text-gray-600 dark:text-gray-300
                         hover:bg-gray-100 dark:hover:bg-surface-dark-alt
                         hover:text-primary dark:hover:text-white
                         transition-colors duration-150"
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {item.label}
            </Link>
          ))}
        </nav>

        {/* User */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-sm font-display font-bold text-primary dark:text-accent">
                {user.first_name[0]}
                {user.last_name[0]}
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-display font-semibold truncate text-gray-900 dark:text-white">
                {user.first_name} {user.last_name}
              </p>
              <p className="text-xs text-gray-500 truncate">{user.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm font-medium
                       text-gray-500 hover:text-error hover:bg-error-light dark:hover:bg-error/10
                       transition-colors duration-150"
          >
            <LogOut className="w-4 h-4" />
            Deconnexion
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-16 bg-white/80 dark:bg-bg-dark/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 flex items-center px-4 sm:px-6 gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex-1" />
          <button className="relative p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-accent rounded-full" />
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
