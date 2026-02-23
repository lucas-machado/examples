import { ReactNode, useReducer } from "react";
import authReducer from "./auth/authReducer";
import AuthContext from "./auth/authContext";

interface Props {
  children: ReactNode;
}

export default function AuthProvider({ children }: Props) {
  const [user, dispatch] = useReducer(authReducer, "");

  return (
    <AuthContext.Provider value={{ user, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
}
