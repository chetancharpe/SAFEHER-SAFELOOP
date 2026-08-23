import { render, screen } from "@testing-library/react";
import RouteCard from "./RouteCard";

test("shows estimated environmental risk and safety score", () => {
  render(<RouteCard selected={false} onSelect={() => undefined} route={{
    label: "SAFELOOP ROUTE",
    mode: "safeloop",
    distance_km: 2.7,
    duration_min: 21,
    risk_score: 29,
    risk_level: "LOW",
    safety_score: 71,
    lighting_factor: 0.8,
    crowd_factor: 0.7,
    time_factor: 0.7,
    environment_factor: 0.8,
    path: [[0,0], [1,1]],
    recommended: true,
    explanation: "Lower estimated environmental risk.",
    data_label: "Demo environmental data"
  }} />);
  expect(screen.getByText("SAFELOOP ROUTE")).toBeInTheDocument();
  expect(screen.getByText("LOW")).toBeInTheDocument();
  expect(screen.getByText("71/100")).toBeInTheDocument();
});
