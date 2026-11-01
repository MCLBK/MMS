"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";
import type { PaginatedOrders, OrderDetail } from "@/types";

export function useOrders(
  companyId: string | undefined,
  page = 1,
  pageSize = 20,
  status?: string,
  search?: string
) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (status) params.set("status", status);
  if (search) params.set("search", search);

  return useQuery({
    queryKey: ["orders", companyId, page, pageSize, status, search],
    queryFn: () =>
      api.get<PaginatedOrders>(
        `/companies/${companyId}/orders?${params.toString()}`
      ),
    enabled: !!companyId,
  });
}

export function useOrder(companyId: string | undefined, orderId: string | undefined) {
  return useQuery({
    queryKey: ["order", companyId, orderId],
    queryFn: () =>
      api.get<OrderDetail>(`/companies/${companyId}/orders/${orderId}`),
    enabled: !!companyId && !!orderId,
  });
}

export function useCreateOrder(companyId: string | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.post<OrderDetail>(`/companies/${companyId}/orders`, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["orders", companyId] }),
  });
}

export function useTransitionOrder(companyId: string | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      orderId,
      newStatus,
      reason,
    }: {
      orderId: string;
      newStatus: string;
      reason?: string;
    }) =>
      api.post<OrderDetail>(
        `/companies/${companyId}/orders/${orderId}/transition`,
        { new_status: newStatus, reason }
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["orders", companyId] });
      qc.invalidateQueries({ queryKey: ["order", companyId] });
    },
  });
}
