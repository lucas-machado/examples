import { NavLink } from "react-router-dom";
import { useAuthStore } from "./auth/useAuthStore";

const NavBar = () => {
  const token = useAuthStore((s) => s.token);
  const logout = useAuthStore((s) => s.logout);

  return (
    <nav
      className="navbar navbar-expand-lg"
      style={{ background: "#f0f0f0", marginBottom: "1rem" }}
    >
      <div
        className="container-fluid"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <a className="navbar-brand" href="#">
          My App
        </a>
        <div id="navbarNav">
          <ul
            className="navbar-nav"
            style={{
              display: "flex",
              gap: "1rem",
              listStyle: "none",
              margin: 0,
              padding: 0,
            }}
          >
            <li className="nav-item">
              <NavLink className="nav-link" to={"/"}>
                Home{" "}
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/moments">
                Moments
              </NavLink>
            </li>
            <li className="nav-item">
              {!token ? (
                <NavLink className="nav-link" to="/login">
                  Login
                </NavLink>
              ) : (
                <p onClick={() => logout()}>Logout</p>
              )}
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
