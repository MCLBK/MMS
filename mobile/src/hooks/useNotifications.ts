import {useEffect, useRef, useCallback, useState} from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const WS_URL = 'ws://10.0.2.2:8000';

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
}

export function useNotifications(userId: string | undefined) {
  const ws = useRef<WebSocket | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retries = useRef(0);

  const connect = useCallback(() => {
    if (!userId) return;

    try {
      ws.current = new WebSocket(`${WS_URL}/ws/notifications?user_id=${userId}`);

      ws.current.onopen = () => {
        retries.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === 'notification') {
            const notif: Notification = {
              id: data.data?.id || Date.now().toString(),
              type: data.data?.type || 'system',
              title: data.data?.title || 'Notification',
              message: data.data?.message || '',
              timestamp: new Date().toISOString(),
            };
            setNotifications((prev) => [notif, ...prev].slice(0, 50));
            setUnreadCount((prev) => prev + 1);
          }
        } catch {}
      };

      ws.current.onclose = () => {
        if (retries.current < 10) {
          const delay = Math.min(1000 * Math.pow(2, retries.current), 30000);
          reconnectTimer.current = setTimeout(() => {
            retries.current++;
            connect();
          }, delay);
        }
      };

      ws.current.onerror = () => {};
    } catch {}
  }, [userId]);

  const markAllRead = useCallback(() => {
    setUnreadCount(0);
  }, []);

  useEffect(() => {
    connect();
    return () => {
      ws.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  return {notifications, unreadCount, markAllRead};
}
