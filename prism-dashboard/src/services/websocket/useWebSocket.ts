import { useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';
import { useAlertStore } from '../../stores/alertStore';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/v1/connect';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const addLiveAlert = useAlertStore((state) => state.addLiveAlert);

  useEffect(() => {
    const token = localStorage.getItem('prism_token');
    const connectUrl = token ? `${WS_URL}?token=${token}` : WS_URL;

    const ws = new WebSocket(connectUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      // Subscribe to alert and incident channels
      ws.send(JSON.stringify({ type: 'subscribe', channel: 'alerts' }));
      ws.send(JSON.stringify({ type: 'subscribe', channel: 'incidents' }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'NEW_ALERT' && data.alert) {
          addLiveAlert(data.alert);
          if (data.alert.severity === 'CRITICAL' || data.alert.severity === 'HIGH') {
            toast.error(`🚨 ${data.alert.severity} Alert: ${data.alert.src_ip} ➔ ${data.alert.dst_ip}:${data.alert.dst_port}`, {
              description: `Risk Score: ${data.alert.risk_score} | Method: ${data.alert.detection_method}`,
              duration: 6000,
            });
          }
        } else if (data.type === 'INCIDENT_UPDATE') {
          toast.info(`📋 Incident Updated: ${data.incident?.title || 'Incident'}`, {
            description: `Status: ${data.incident?.status}`,
          });
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = (err) => {
      console.error('WebSocket Error:', err);
      setIsConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [addLiveAlert]);

  return { isConnected };
}
