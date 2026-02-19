import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { TodoList } from "./components/TodoList";
import { LoginScreen } from "./components/LoginScreen";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!localStorage.getItem("token")) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  const navigate = useNavigate();

  const handleLogin = (token: string) => {
    localStorage.setItem("token", token);
    navigate("/");
  };

  return (
    <Routes>
      <Route path="/login" element={<LoginScreen onLogin={handleLogin} />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <TodoList />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
