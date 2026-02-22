import { useContext, useReducer } from "react";
import authReducer from "./reducers/authReducer";
import authContext from "./contexts/authContext";

const LoginStatus = () => {
  const { user, dispatch } = useContext(authContext);
  if (user)
    return (
      <>
        <div>
          <span className="mx-2">{user}</span>
          <a onClick={() => dispatch({ type: "LOGOUT" })} href="#">
            Logout
          </a>
        </div>
      </>
    );
  return (
    <div>
      <a
        onClick={() => dispatch({ type: "LOGIN", username: "mosh.hamedani" })}
        href="#"
      >
        Login
      </a>
    </div>
  );
};

export default LoginStatus;
