import { Navigate, Outlet } from "react-router-dom";
import { isAuthenticated, useAuthStore } from "./auth/useAuthStore";

const PrivateRoutes = () => {
  if (!isAuthenticated()) return <Navigate to="/login" />;

  return <Outlet />;
};

export default PrivateRoutes;
