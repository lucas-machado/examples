import { Outlet } from "react-router-dom";
import "./App.css";
import NavBar from "./NavBar";

function App() {
  return (
    <>
      <NavBar />
      <div id="main">
        <Outlet />
      </div>
    </>
  );
}

export default App;
