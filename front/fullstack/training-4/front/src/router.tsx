import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import ErrorPage from "./ErrorPage";
import HomePage from "./HomePage";
import LoginPage from "./LoginPage";
import PrivateRoutes from "./PrivateRoutes";
import MomentsPage from "./MomentsPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "login", element: <LoginPage /> },
      {
        element: <PrivateRoutes />,
        children: [
          {
            path: "moments",
            element: <MomentsPage />,
          },
        ],
      },
    ],
  },
]);

export default router;
