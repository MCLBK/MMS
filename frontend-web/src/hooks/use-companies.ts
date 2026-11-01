"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";
import type { Company } from "@/types";

export function useCompanies(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["companies", page, pageSize],
    queryFn: () =>
      api.get<Company[]>(`/companies?page=${page}&page_size=${pageSize}`),
  });
}

export function useCompany(id: string | undefined) {
  return useQuery({
    queryKey: ["company", id],
    queryFn: () => api.get<Company>(`/companies/${id}`),
    enabled: !!id,
  });
}

export function useCreateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Company>) => api.post<Company>("/companies", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies"] }),
  });
}

export function useUpdateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Company> }) =>
      api.patch<Company>(`/companies/${id}`, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies"] }),
  });
}
