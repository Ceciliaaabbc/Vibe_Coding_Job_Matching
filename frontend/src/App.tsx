import { BriefcaseBusiness, FileText, Gauge, Globe2, Inbox, Send } from "lucide-react";
import type { ElementType } from "react";
import { useState } from "react";
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
