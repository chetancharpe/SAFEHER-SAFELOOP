import { MapContainer, Marker, Polyline, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import type { RouteOption } from "../types/api";

const icon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

export default function SafeMap({ route }: { route?: RouteOption }) {
  const path = route?.path ?? [[28.6139, 77.2090], [28.628, 77.23]];
  return (
    <MapContainer center={path[0]} zoom={14} scrollWheelZoom={false} className="h-[360px]">
      <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Polyline positions={path} color={route?.risk_level === "LOW" ? "#48f2b8" : "#ff5f6d"} weight={6} />
      <Marker position={path[0]} icon={icon}><Popup>Current location</Popup></Marker>
      <Marker position={path[path.length - 1]} icon={icon}><Popup>Destination</Popup></Marker>
    </MapContainer>
  );
}
