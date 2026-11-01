"use client";

import { useEffect, useRef, useCallback, useState } from "react";

interface WSMessage {
  event: string;
  data: Record<string, unknown>;
  channel?: string;
  timestamp?: string;
}

type EventHandler = (data: Record<string, unknown>) => void;

interface UseWebSocketOptions {
  url: string;
  enabled?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (msg: WSMessage) => void;
}

export function useWebSocket({
  url,
  enabled = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 10,
  onMessage,
}: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef<Map<string, Set<EventHandler>>>(new Map());
  const reconnectCountRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  const [isConnected, setIsConnected] = useState(false);

  const on = useCallback((event: string, handler: EventHandler) => {
    if (!handlersRef.current.has(event)) {
      handlersRef.current.set(event, new Set());
    }
    handlersRef.current.get(event)!.add(handler);

    return () => {
      handlersRef.current.get(event)?.delete(handler);
    };
  }, []);

  const send = useCallback((type: string, data?: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, data }));
    }
  }, []);

  useEffect(() => {
    if (!enabled || !url) return;

    let disposed = false;

    function connect() {
      if (disposed) return;

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        reconnectCountRef.current = 0;
      };

      ws.onmessage = (evt) => {
        try {
          const msg: WSMessage = JSON.parse(evt.data);
          onMessage?.(msg);

          const handlers = handlersRef.current.get(msg.event);
          if (handlers) {
            handlers.forEach((h) => h(msg.data));
          }

          const wildcard = handlersRef.current.get("*");
          if (wildcard) {
            wildcard.forEach((h) => h({ event: msg.event, ...msg.data }));
          }
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;

        if (!disposed && reconnectCountRef.current < maxReconnectAttempts) {
          reconnectCountRef.current++;
          reconnectTimerRef.current = setTimeout(connect, reconnectInterval);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30_000);

    return () => {
      disposed = true;
      clearInterval(pingInterval);
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [url, enabled, reconnectInterval, maxReconnectAttempts, onMessage]);

  return { isConnected, on, send };
}

function getWsBase() {
  if (process.env.NEXT_PUBLIC_WS_URL) return process.env.NEXT_PUBLIC_WS_URL;
  if (typeof window === "undefined") return "ws://localhost:8000";
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}`;
}
const WS_BASE = getWsBase();

export function useNotificationSocket(userId: string | undefined, companyId: string | undefined) {
  const url = userId
    ? `${WS_BASE}/ws/notifications?user_id=${userId}${companyId ? `&company_id=${companyId}` : ""}`
    : "";

  return useWebSocket({ url, enabled: !!userId });
}

export function useTrackingSocket(companyId: string | undefined) {
  const url = companyId ? `${WS_BASE}/ws/tracking?company_id=${companyId}` : "";
  return useWebSocket({ url, enabled: !!companyId });
}

export function useOrderSocket(orderId: string | undefined) {
  const url = orderId ? `${WS_BASE}/ws/order/${orderId}` : "";
  return useWebSocket({ url, enabled: !!orderId });
}
