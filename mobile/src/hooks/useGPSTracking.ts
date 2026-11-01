import {useEffect, useRef, useState, useCallback} from 'react';
import {Platform, PermissionsAndroid} from 'react-native';
import Geolocation from '@react-native-community/geolocation';
import {api} from '../services/api';

interface Position {
  latitude: number;
  longitude: number;
  speed: number | null;
  heading: number | null;
  accuracy: number | null;
  timestamp: number;
}

export function useGPSTracking(companyId: string, courierId: string, intervalMs = 10000) {
  const [position, setPosition] = useState<Position | null>(null);
  const [isTracking, setIsTracking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const watchId = useRef<number | null>(null);
  const sendInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const latestPosition = useRef<Position | null>(null);

  const requestPermission = useCallback(async () => {
    if (Platform.OS === 'android') {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        {
          title: 'Position GPS',
          message: 'MMS Express a besoin de votre position pour le suivi des livraisons.',
          buttonPositive: 'Autoriser',
          buttonNegative: 'Refuser',
        },
      );
      return granted === PermissionsAndroid.RESULTS.GRANTED;
    }
    return true;
  }, []);

  const sendPosition = useCallback(
    async (pos: Position) => {
      try {
        await api.post(`/companies/${companyId}/tracking/positions`, {
          courier_id: courierId,
          latitude: pos.latitude,
          longitude: pos.longitude,
          speed_kmh: pos.speed ? pos.speed * 3.6 : null,
          heading: pos.heading,
          accuracy: pos.accuracy,
          recorded_at: new Date(pos.timestamp).toISOString(),
        });
      } catch {
        // Silently fail — will retry on next interval
      }
    },
    [companyId, courierId],
  );

  const startTracking = useCallback(async () => {
    const hasPermission = await requestPermission();
    if (!hasPermission) {
      setError('Permission GPS refusee');
      return;
    }

    setIsTracking(true);
    setError(null);

    watchId.current = Geolocation.watchPosition(
      (pos) => {
        const p: Position = {
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          speed: pos.coords.speed,
          heading: pos.coords.heading,
          accuracy: pos.coords.accuracy,
          timestamp: pos.timestamp,
        };
        setPosition(p);
        latestPosition.current = p;
      },
      (err) => setError(err.message),
      {enableHighAccuracy: true, distanceFilter: 20, interval: 5000},
    );

    sendInterval.current = setInterval(() => {
      if (latestPosition.current) {
        sendPosition(latestPosition.current);
      }
    }, intervalMs);
  }, [requestPermission, sendPosition, intervalMs]);

  const stopTracking = useCallback(() => {
    if (watchId.current !== null) {
      Geolocation.clearWatch(watchId.current);
      watchId.current = null;
    }
    if (sendInterval.current) {
      clearInterval(sendInterval.current);
      sendInterval.current = null;
    }
    setIsTracking(false);
  }, []);

  useEffect(() => {
    return () => stopTracking();
  }, [stopTracking]);

  return {position, isTracking, error, startTracking, stopTracking};
}
