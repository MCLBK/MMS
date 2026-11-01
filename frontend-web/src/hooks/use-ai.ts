"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";

interface ScoringResult {
  courier_id: string;
  courier_name: string;
  score: number;
  confidence: number;
  estimated_arrival_min: number;
  distance_km: number;
  factors: Record<string, unknown>;
}

interface ScoringResponse {
  order_id: string;
  candidates: ScoringResult[];
  model_version: string;
}

interface PredictionTimeResponse {
  estimated_minutes: number;
  confidence: number;
  factors: Record<string, unknown>;
}

interface VolumeForecast {
  date: string;
  predicted_orders: number;
  confidence: number;
  trend: string;
}

interface HotZone {
  center_lat: number;
  center_lng: number;
  radius_km: number;
  order_count: number;
  avg_delivery_time_min: number | null;
  demand_level: string;
}

interface RiskResponse {
  risk_score: number;
  risk_level: string;
  factors: string[];
  recommendations: string[];
}

interface ChatResponse {
  message: string;
  context: Record<string, unknown>;
  source: string;
  suggestions: string[];
}

export function useAIScoring(companyId: string) {
  return useMutation({
    mutationFn: (orderId: string) =>
      api.post<ScoringResponse>(`/companies/${companyId}/ai/scoring`, {
        order_id: orderId,
      }),
  });
}

export function useDeliveryTimePrediction(companyId: string) {
  return useMutation({
    mutationFn: (params: {
      pickup_lat?: number;
      pickup_lng?: number;
      delivery_lat?: number;
      delivery_lng?: number;
      priority?: string;
      weight_kg?: number;
    }) => api.post<PredictionTimeResponse>(`/companies/${companyId}/ai/predict-time`, params),
  });
}

export function useVolumeForecast(companyId: string | undefined, days = 7) {
  return useQuery({
    queryKey: ["ai", "forecast", companyId, days],
    queryFn: () =>
      api.get<VolumeForecast[]>(`/companies/${companyId}/ai/forecast?days=${days}`),
    enabled: !!companyId,
  });
}

export function useHotZones(companyId: string | undefined, days = 7) {
  return useQuery({
    queryKey: ["ai", "hot-zones", companyId, days],
    queryFn: () =>
      api.get<HotZone[]>(`/companies/${companyId}/ai/hot-zones?days=${days}`),
    enabled: !!companyId,
  });
}

export function useRiskAssessment(companyId: string) {
  return useMutation({
    mutationFn: (orderId: string) =>
      api.post<RiskResponse>(`/companies/${companyId}/ai/risk`, {
        order_id: orderId,
      }),
  });
}

export function useAIChat(companyId: string) {
  return useMutation({
    mutationFn: (params: {
      message: string;
      conversation_history?: Array<{ role: string; content: string }>;
    }) => api.post<ChatResponse>(`/companies/${companyId}/ai/chat`, params),
  });
}

export type {
  ScoringResult,
  ScoringResponse,
  PredictionTimeResponse,
  VolumeForecast,
  HotZone,
  RiskResponse,
  ChatResponse,
};
