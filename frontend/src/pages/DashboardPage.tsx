import { useEffect, useState } from "react";
import { api } from "../api/client";

type Summary = {
  total_jobs: number;
  high_match_pending: number;
  applied: number;
  interviewing: number;
  interview_rate: number;
};

export function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    api.get<Summary>("/dashboard/summary").then((response) => setSummary(response.data));
  }, []);

  const items = [
    ["Jobs Found", summary?.total_jobs ?? 0],
    ["Pending", summary?.high_match_pending ?? 0],
    ["Applied", summary?.applied ?? 0],
    ["Interviewing", summary?.interviewing ?? 0],
    ["Interview Rate", `${summary?.interview_rate ?? 0}%`],
  ];

  return (
    <section>
      <header className="page-header">
        <h1>Dashboard</h1>
        <p>Track discovered jobs, confirmation queue, applications, and interview progress.</p>
      </header>
      <div className="metric-grid">
        {items.map(([label, value]) => (
          <article className="metric-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}

