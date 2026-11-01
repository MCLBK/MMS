"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";
import type { CourierListItem, CourierDetail } from "@/types";

export function useCouriers(
  companyId: string | undefined,
  page = 1,
  pageSize = 20,
  status?: string
) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  if (status) params.set("status", status);

  return useQuery({
    queryKey: ["couriers", companyId, page, pageSize, status],
    queryFn: () =>
      api.get<CourierListItem[]>(
        `/companies/${companyId}/couriers?${params.toString()}`
      ),
    enabled: !!companyId,
  });
}

export function useCourier(companyId: string | undefined, courierId: string | undefined) {
  return useQuery({
    queryKey: ["courier", companyId, courierId],
    queryFn: () =>
      api.get<CourierDetail>(`/companies/${companyId}/couriers/${courierId}`),
    enabled: !!companyId && !!courierId,
  });
}

export function useCreateCourier(companyId: string | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.post<CourierDetail>(`/companies/${companyId}/couriers`, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["couriers", companyId] }),
  });
}

export function useUpdateCourier(companyId: string | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      courierId,
      data,
    }: {
      courierId: string;
      data: Record<string, unknown>;
    }) =>
      api.patch<CourierDetail>(
        `/companies/${companyId}/couriers/${courierId}`,
        data
      ),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["couriers", companyId] }),
  });
}
