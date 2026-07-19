import { BriefcaseBusiness, FileText, Gauge, Globe2, Inbox, Send } from "lucide-react";
import type { ElementType } from "react";
import { useEffect, useState } from "react";
import { api } from "./api/client";
import type { AuthUser } from "./types";
import { AuthPage } from "./pages/AuthPage";
import { DashboardPage } from "./pages/DashboardPage";
import { JobsPage } from "./pages/JobsPage";
import { PendingPage } from "./pages/PendingPage";
import { ResourcesPage } from "./pages/ResourcesPage";
import { ResumePage } from "./pages/ResumePage";

type View = "dashboard" | "resume" | "jobs" | "resources" | "pending";

const navItems: Array<{ id: View; label: string; icon: ElementType }> = [
  { id: "dashboard", label: "Dashboard", icon: Gauge },
  { id: "resume", label: "Resume", icon: FileText },
  { id: "jobs", label: "Jobs", icon: BriefcaseBusiness },
  { id: "resources", label: "Resources", icon: Globe2 },
  { id: "pending", label: "Pending", icon: Inbox },
];

export function App() {
  const [view, setView] = useState<View>("dashboard");
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("job-agent-token")) {
      setCheckingAuth(false);
      return;
    }
    api.get<AuthUser>("/auth/me")
      .then((response) => setUser(response.data))
      .catch(() => localStorage.removeItem("job-agent-token"))
      .finally(() => setCheckingAuth(false));
  }, []);

  if (checkingAuth) return <main className="main-content"><p>Checking authentication...</p></main>;
  if (!user) return <AuthPage onAuthenticated={setUser} />;

  function logout() {
    localStorage.removeItem("job-agent-token");
    setUser(null);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Send size={22} />
          <span>Job Agent</span>
        </div>
        <nav>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                className={view === item.id ? "nav-item active" : "nav-item"}
                key={item.id}
                onClick={() => setView(item.id)}
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
        <div>
          <small>{user.email}</small>
          <button className="nav-item" type="button" onClick={logout}>Sign out</button>
        </div>
      </aside>

      <main className="main-content">
        {view === "dashboard" && <DashboardPage />}
        {view === "resume" && <ResumePage />}
        {view === "jobs" && <JobsPage />}
        {view === "resources" && <ResourcesPage />}
        {view === "pending" && <PendingPage />}
      </main>
    </div>
  );
}
