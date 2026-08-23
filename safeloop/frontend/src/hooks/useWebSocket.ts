import { useEffect, useState } from "react";
import { wsUrl } from "../services/api";

export function useWebSocket() {
  const [events, setEvents] = useState<{ event: string; payload: any }[]>([]);

  useEffect(() => {
    const socket = new WebSocket(wsUrl);
    socket.onmessage = (message) => {
      setEvents((current) => [...current.slice(-10), JSON.parse(message.data)]);
    };
    return () => socket.close();
  }, []);

  return events;
}
