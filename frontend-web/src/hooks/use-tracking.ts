"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";

interface CourierPosition {
  courier_id: string;
  courier_name: string;
  latitude: number;
  longitude: number;
  speed_kmh: number | null;
  battery_level: number | null;
  recorded_at: string;
  status: string;
}

export function useLivePositions(companyId: string | undefined) {
  return useQuery({
    queryKey: ["tracking", "live", companyId],
    queryFn: () =>
      api.get<CourierPosition[]>(
        `/companies/${companyId}/tracking/live`
      ),
    enabled: !!companyId,
    refetchInterval: 5_000,
  });
}

export type { CourierPosition };
