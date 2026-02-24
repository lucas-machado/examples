import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "./auth/useAuthStore";

const PrivateRoutes = () => {
  const token = useAuthStore((s) => s.token);

  if (!token) return <Navigate to="/login" />;

  return <Outlet />;
};

export default PrivateRoutes;
