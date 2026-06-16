import { ExternalLink, Search } from "lucide-react";
import { useMemo, useState } from "react";

type HiringResource = {
  name: string;
  region: string;
  mode: "Public API" | "Link-only";
  description: string;
  url: string;
  buildSearchUrl?: (query: string) => string;
};

const hiringResources: HiringResource[] = [
  {
    name: "Remotive",
    region: "Global remote",
    mode: "Public API",
    description: "Real remote jobs imported into the Jobs list through the public API.",
    url: "https://remotive.com/remote-jobs",
    buildSearchUrl: (query) => `https://remotive.com/remote-jobs?search=${encodeURIComponent(query)}`,
  },
  {
    name: "Arbeitnow",
    region: "Europe / remote",
    mode: "Public API",
    description: "Real jobs imported into the Jobs list through the public job-board API.",
    url: "https://www.arbeitnow.com/jobs",
  },
  {
    name: "RemoteOK",
    region: "Global remote",
    mode: "Public API",
    description: "Real remote jobs imported into the Jobs list through the public API.",
    url: "https://remoteok.com/",
    buildSearchUrl: (query) => `https://remoteok.com/remote-${encodeURIComponent(query.replace(/\s+/g, "-"))}-jobs`,
  },
  {
    name: "The Muse",
    region: "Global",
    mode: "Public API",
    description: "Real jobs imported into the Jobs list through the public jobs API.",
    url: "https://www.themuse.com/search/jobs",
    buildSearchUrl: (query) => `https://www.themuse.com/search/jobs?keyword=${encodeURIComponent(query)}`,
  },
  {
    name: "电鸭",
    region: "China remote / community",
    mode: "Link-only",
    description: "Remote-work community with verification on job pages; open manually, no scraping or CAPTCHA bypass.",
    url: "https://eleduck.com/jobs-channel",
  },
  {
    name: "Fiverr",
    region: "Global freelance",
    mode: "Link-only",
    description: "Freelance marketplace. Open searches manually and apply through Fiverr account flow.",
    url: "https://www.fiverr.com/",
    buildSearchUrl: (query) => `https://www.fiverr.com/search/gigs?query=${encodeURIComponent(query)}`,
  },
  {
    name: "BOSS直聘",
    region: "China",
    mode: "Link-only",
    description: "Login/chat-based hiring platform. Open search manually; the agent will not bypass login or risk controls.",
    url: "https://www.zhipin.com/",
    buildSearchUrl: (query) => `https://www.zhipin.com/web/geek/job?query=${encodeURIComponent(query)}`,
  },
  {
    name: "猎聘",
    region: "China",
    mode: "Link-only",
    description: "Professional hiring platform. Open search manually; no unauthorized scraping.",
    url: "https://www.liepin.com/",
    buildSearchUrl: (query) => `https://www.liepin.com/zhaopin/?key=${encodeURIComponent(query)}`,
  },
  {
    name: "牛客网",
    region: "China campus / tech",
    mode: "Link-only",
    description: "Tech recruiting and interview-prep platform. Open search manually; no automated application.",
    url: "https://www.nowcoder.com/",
    buildSearchUrl: (query) => `https://www.nowcoder.com/search/all?query=${encodeURIComponent(query)}`,
  },
];

export function ResourcesPage() {
  const [query, setQuery] = useState("AI Agent Engineer");
  const encodedResources = useMemo(
    () =>
      hiringResources.map((resource) => ({
        ...resource,
        searchUrl: resource.buildSearchUrl ? resource.buildSearchUrl(query) : resource.url,
      })),
    [query],
  );

  return (
    <section>
      <header className="page-header">
        <h1>Hiring Resources</h1>
        <p>Use public APIs where allowed. For login, CAPTCHA, or risk-controlled platforms, open the official site manually.</p>
      </header>

      <div className="panel resource-search">
        <label className="field">
          <span>Search keywords</span>
          <input value={query} onChange={(event) => setQuery(event.target.value)} />
        </label>
      </div>

      <div className="resource-grid">
        {encodedResources.map((resource) => (
          <article className="resource-card" key={resource.name}>
            <header>
              <div>
                <h2>{resource.name}</h2>
                <span>{resource.region}</span>
              </div>
              <strong className={resource.mode === "Public API" ? "source-badge api" : "source-badge link"}>
                {resource.mode}
              </strong>
            </header>
            <p>{resource.description}</p>
            <div className="row-actions">
              <a className="secondary-button" href={resource.url} rel="noreferrer">
                <ExternalLink size={18} />
                Open
              </a>
              <a className="primary-button" href={resource.searchUrl} rel="noreferrer">
                <Search size={18} />
                Search
              </a>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
