import { Link, useLocation } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { Button } from "../ui/Button";

const navItems = [
  { to: "/", label: "Search" },
  { to: "/graph", label: "Graph Explorer" },
  { to: "/documents", label: "Documents" },
  { to: "/admin", label: "Admin" },
];

export function Navbar() {
  const location = useLocation();
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-8">
          <Link to="/" className="text-lg font-semibold text-brand-700">
            Multilingual Graph RAG
          </Link>
          <nav className="hidden items-center gap-4 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={`text-sm font-medium transition hover:text-brand-600 ${location.pathname === item.to ? "text-brand-600" : "text-slate-600"}`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="hidden text-sm text-slate-600 sm:inline">{user.email}</span>
              <Button variant="secondary" onClick={() => void logout()}>
                Logout
              </Button>
            </>
          ) : null}
        </div>
      </div>
    </header>
  );
}
