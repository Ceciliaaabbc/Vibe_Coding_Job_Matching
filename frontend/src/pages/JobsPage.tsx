import { ExternalLink, Plus, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Job, Resume } from "../types";

export function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobId, setJobId] = useState("");
  const [resumeId, setResumeId] = useState("");
  const [keywords, setKeywords] = useState("AI Agent Engineer");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");

  async function loadData() {
    const [jobsResponse, resumesResponse] = await Promise.all([api.get<Job[]>("/jobs"), api.get<Resume[]>("/resumes")]);
    setJobs(jobsResponse.data);
    setResumes(resumesResponse.data);
    if (!resumeId && resumesResponse.data[0]) setResumeId(resumesResponse.data[0].id);
  }

  useEffect(() => {
    loadData().then(async () => {
      const response = await api.get<Job[]>("/jobs");
      if (response.data.length === 0) {
        await discoverJobs();
      }
    });
  }, []);

  async function discoverJobs() {
    setLoading(true);
    setResult("Fetching real jobs from public sources: Remotive, Arbeitnow, RemoteOK, and The Muse.");
    try {
      const response = await api.post<Job[]>("/jobs/discover", { keywords, limit: 50 });
      await loadData();
      setResult(`Loaded ${response.data.length} real jobs from public sources. Click Fetch More Jobs to expand the list.`);
    } catch (error) {
      setResult("Public job source is unavailable or returned no usable data. No fake jobs were loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function importJob(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const response = await api.post("/jobs/import-text", {
      company: data.get("company"),
      title: data.get("title"),
      location: data.get("location"),
      url: data.get("url") || null,
      raw_description: data.get("raw_description"),
    });
    setJobId(response.data.id);
    setResult(`Imported job: ${response.data.company} - ${response.data.title}`);
    await loadData();
  }

  async function matchJob() {
    if (!jobId || !resumeId) {
      setResult("Select both a job and a resume to run matching. You can browse jobs without a resume.");
      return;
    }
    const response = await api.post(`/jobs/${jobId}/match/${resumeId}`);
    const reasons = response.data.match.reasons?.join(" ") ?? "";
    setResult(`Score: ${response.data.match.score}/100. Application: ${response.data.application_id}. ${reasons}`);
  }

  function useJobForMatch(job: Job) {
    setJobId(job.id);
    setResult(`Selected ${job.company} - ${job.title} for resume matching.`);
  }

  return (
    <section>
      <header className="page-header">
        <h1>Jobs</h1>
        <p>Browse jobs first. Resume matching is optional and only runs after you upload/select a resume.</p>
      </header>

      <div className="panel inline-panel">
        <label className="field">
          <span>Search keywords</span>
          <input value={keywords} onChange={(event) => setKeywords(event.target.value)} />
        </label>
        <button className="primary-button" type="button" onClick={discoverJobs} disabled={loading}>
          <Sparkles size={18} />
          {loading ? "Loading..." : "Fetch More Jobs"}
        </button>
      </div>

      <form className="panel form-grid" onSubmit={importJob}>
        <label className="field">
          <span>Company</span>
          <input name="company" required />
        </label>
        <label className="field">
          <span>Title</span>
          <input name="title" required />
        </label>
        <label className="field">
          <span>Location</span>
          <input name="location" />
        </label>
        <label className="field">
          <span>URL</span>
          <input name="url" type="url" />
        </label>
        <label className="field full">
          <span>Job Description</span>
          <textarea name="raw_description" required minLength={20} rows={10} />
        </label>
        <button className="primary-button" type="submit">
          <Plus size={18} />
          Import JD
        </button>
      </form>

      <div className="panel inline-panel">
        <label className="field">
          <span>Job ID</span>
          <select value={jobId} onChange={(event) => setJobId(event.target.value)}>
            <option value="">Select a job</option>
            {jobs.map((job) => (
              <option value={job.id} key={job.id}>
                {job.company} - {job.title}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Resume ID</span>
          <select value={resumeId} onChange={(event) => setResumeId(event.target.value)}>
            <option value="">Select a resume</option>
            {resumes.map((resume) => (
              <option value={resume.id} key={resume.id}>
                {resume.file_name}
              </option>
            ))}
          </select>
        </label>
        <button className="secondary-button" onClick={matchJob} type="button">
          <Sparkles size={18} />
          Match
        </button>
      </div>

      {result && <p className="notice">{result}</p>}

      <div className="list job-list">
        <div className="list-heading">
          <strong>{jobs.length} jobs</strong>
          <span>Visible before resume upload</span>
        </div>
        {jobs.map((job) => (
          <article className="list-row" key={job.id}>
            <div>
              <strong>
                {job.company} · {job.title}
              </strong>
              <span>{job.location || "Location not specified"}</span>
            </div>
            <div className="row-actions">
              <button className="secondary-button" type="button" onClick={() => useJobForMatch(job)}>
                Use for Match
              </button>
              {job.url ? (
                <a className="primary-button" href={job.url} rel="noreferrer">
                  <ExternalLink size={18} />
                  Apply
                </a>
              ) : (
                <button className="primary-button" type="button" disabled>
                  <ExternalLink size={18} />
                  Apply
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
