"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";

interface DashboardStats {
  total_orders: number;
  orders_today: number;
  in_transit: number;
  completed_today: number;
  pending: number;
  failed: number;
  total_couriers: number;
  available_couriers: number;
  avg_delivery_time_min: number | null;
  completion_rate: number | null;
}

interface OrdersByStatus {
  status: string;
  count: number;
}

interface DailyStats {
  date: string;
  created: number;
  completed: number;
  failed: number;
}

export function useDashboardStats(companyId: string | undefined) {
  return useQuery({
    queryKey: ["analytics", "dashboard", companyId],
    queryFn: () =>
      api.get<DashboardStats>(
        `/companies/${companyId}/analytics/dashboard`
      ),
    enabled: !!companyId,
    refetchInterval: 30_000,
  });
}

export function useOrdersByStatus(companyId: string | undefined) {
  return useQuery({
    queryKey: ["analytics", "orders-by-status", companyId],
    queryFn: () =>
      api.get<OrdersByStatus[]>(
        `/companies/${companyId}/analytics/orders-by-status`
      ),
    enabled: !!companyId,
  });
}

export function useDailyStats(companyId: string | undefined, days = 7) {
  return useQuery({
    queryKey: ["analytics", "daily", companyId, days],
    queryFn: () =>
      api.get<DailyStats[]>(
        `/companies/${companyId}/analytics/daily?days=${days}`
      ),
    enabled: !!companyId,
  });
}

export type { DashboardStats, OrdersByStatus, DailyStats };
