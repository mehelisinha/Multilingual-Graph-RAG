import type { ReactNode } from "react";

import { Navbar } from "./Navbar";

interface PageWrapperProps {
  children: ReactNode;
  showNavbar?: boolean;
}

export function PageWrapper({ children, showNavbar = true }: PageWrapperProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      {showNavbar ? <Navbar /> : null}
      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>
    </div>
  );
}
