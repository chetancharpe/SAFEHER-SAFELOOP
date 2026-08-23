export type User = {
  id: number;
  name: string;
  email: string;
  role: "user" | "responder" | "admin";
  emergency_phrase: string;
  microphone_enabled: boolean;
};

export type RouteOption = {
  label: string;
  mode: string;
  distance_km: number;
  duration_min: number;
  risk_score: number;
  risk_level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  safety_score: number;
  lighting_factor: number;
  crowd_factor: number;
  time_factor: number;
  environment_factor: number;
  path: [number, number][];
  recommended: boolean;
  explanation: string;
  data_label: string;
};

export type Journey = {
  id: number;
  destination: string;
  selected_mode: string;
  status: string;
  distance_km: number;
  duration_min: number;
  safety_score: number;
  risk_score: number;
  risk_level: string;
};

export type EmergencyState = {
  id: number;
  status: string;
  trusted_contacts_notified: number;
  nearby_responders: Responder[];
};

export type Responder = {
  id: number;
  name: string;
  type: string;
  distance_m: number;
  eta_min: number;
  responder_score: number;
  latitude: number;
  longitude: number;
};
