import React, { Dispatch } from "react";
import { AuthAction } from "./authReducer";

interface AuthContextType {
  user: string;
  dispatch: Dispatch<AuthAction>;
}

export default React.createContext<AuthContextType>({} as AuthContextType);
