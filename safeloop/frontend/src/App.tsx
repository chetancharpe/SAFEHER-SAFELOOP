import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./layouts/AppShell";
import DemoPage from "./pages/DemoPage";
import HomePage from "./pages/HomePage";
import InsightsPage from "./pages/InsightsPage";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import PrivacyPage from "./pages/PrivacyPage";
import RegisterPage from "./pages/RegisterPage";
import ResponderDashboard from "./pages/ResponderDashboard";
import { useAuth } from "./store/auth";

function Protected({ children, roles }: { children: React.ReactNode; roles?: string[] }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/app" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/demo" element={<DemoPage />} />
      <Route element={<Protected><AppShell /></Protected>}>
        <Route path="/app" element={<HomePage />} />
        <Route path="/insights" element={<InsightsPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/responder" element={<Protected roles={["responder", "admin"]}><ResponderDashboard /></Protected>} />
      </Route>
    </Routes>
  );
}
