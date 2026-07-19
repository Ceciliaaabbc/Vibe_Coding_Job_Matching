import { Code2, FileText, Sparkles, Upload } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { CareerDirection, GeneratedProject, OptimizedResume, Resume } from "../types";

export function ResumePage() {
  const [message, setMessage] = useState("");
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [directions, setDirections] = useState<CareerDirection[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [directionId, setDirectionId] = useState("ai-ml");
  const [jobDescription, setJobDescription] = useState("");
  const [optimized, setOptimized] = useState<OptimizedResume | null>(null);
  const [project, setProject] = useState<GeneratedProject | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadResumeWorkbench() {
    const [resumeResponse, directionResponse] = await Promise.all([
      api.get<Resume[]>("/resumes"),
      api.get<CareerDirection[]>("/resumes/directions"),
    ]);
    setResumes(resumeResponse.data);
    setDirections(directionResponse.data);
    if (!resumeId && resumeResponse.data[0]) setResumeId(resumeResponse.data[0].id);
    if (!directionId && directionResponse.data[0]) setDirectionId(directionResponse.data[0].id);
  }

  useEffect(() => {
    loadResumeWorkbench();
  }, []);

  async function uploadResume(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const input = form.elements.namedItem("resume") as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const body = new FormData();
    body.append("file", file);
    const response = await api.post("/resumes/upload", body);
    setMessage(`Uploaded ${response.data.file_name}. Resume ID: ${response.data.id}`);
    setResumeId(response.data.id);
    await loadResumeWorkbench();
  }

  async function generateResume() {
    if (!resumeId || !directionId) {
      setMessage("Upload/select a resume and choose a direction first.");
      return;
    }
    setLoading(true);
    setProject(null);
    setMessage("Generating direction-specific resume draft.");
    try {
      const response = await api.post<OptimizedResume>("/resumes/optimize", {
        resume_id: resumeId,
        direction_id: directionId,
        job_description: jobDescription || null,
        use_llm: true,
      });
      setOptimized(response.data);
      setMessage(`Generated ${response.data.direction.name} resume draft.`);
    } finally {
      setLoading(false);
    }
  }

  async function createProject() {
    if (!directionId) return;
    const response = await api.post<GeneratedProject>("/resumes/projects", { direction_id: directionId });
    setProject(response.data);
    setMessage(`Created local project template: ${response.data.project_path}`);
  }

  return (
    <section>
      <header className="page-header">
        <h1>Resume</h1>
        <p>Upload your base resume, then generate a focused version for AI, full stack, backend, infra, data, and more.</p>
      </header>
      <form className="panel" onSubmit={uploadResume}>
        <label className="field">
          <span>Resume file</span>
          <input name="resume" type="file" accept=".pdf,.docx" data-testid="resume-file" />
        </label>
        <button className="primary-button" type="submit" data-testid="upload-resume">
          <Upload size={18} />
          Upload
        </button>
      </form>
      {message && <p className="notice">{message}</p>}

      <section className="detail-drawer resume-workbench">
        <header>
          <div>
            <h2>Directional Resume Generator</h2>
            <p>Uses standard technical resume structure and rewrites toward the selected computer-science direction.</p>
          </div>
        </header>

        <div className="form-grid">
          <label className="field">
            <span>Base resume</span>
            <select value={resumeId} onChange={(event) => setResumeId(event.target.value)}>
              <option value="">Select a resume</option>
              {resumes.map((resume) => (
                <option value={resume.id} key={resume.id}>
                  {resume.file_name}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Target direction</span>
            <select value={directionId} onChange={(event) => setDirectionId(event.target.value)}>
              {directions.map((direction) => (
                <option value={direction.id} key={direction.id}>
                  {direction.name}
                </option>
              ))}
            </select>
          </label>
          <label className="field full">
            <span>Optional job description</span>
            <textarea
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              rows={6}
              placeholder="Paste a JD here to generate a resume targeted to that specific job."
            />
          </label>
        </div>

        <div className="drawer-actions">
          <button className="primary-button" type="button" onClick={generateResume} disabled={loading}>
            <Sparkles size={18} />
            {loading ? "Generating..." : "Generate Resume"}
          </button>
          <button className="secondary-button" type="button" onClick={createProject}>
            <Code2 size={18} />
            Create Gap Project
          </button>
        </div>
      </section>

      {optimized && (
        <section className="detail-drawer resume-output">
          <header>
            <div>
              <h2>{optimized.direction.name}</h2>
              <p>{optimized.direction.headline}</p>
            </div>
            <FileText size={22} />
          </header>
          <div className="detail-columns">
            <article>
              <h3>Target Keywords</h3>
              <div className="chips">
                {optimized.emphasized_keywords.map((keyword) => (
                  <span key={keyword}>{keyword}</span>
                ))}
              </div>
              <h3>Missing / Weak Signals</h3>
              <div className="chips">
                {(optimized.missing_skills.length ? optimized.missing_skills : ["No major gaps detected"]).map((skill) => (
                  <span key={skill}>{skill}</span>
                ))}
              </div>
              <h3>Recommended Project</h3>
              <p>
                <strong>{optimized.recommended_project.name}</strong>: {optimized.recommended_project.pitch}
              </p>
              <h3>Notes</h3>
              <ul>
                {optimized.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </article>
            <article>
              <h3>Resume Draft</h3>
              <textarea className="resume-markdown" value={optimized.resume_markdown} readOnly rows={24} />
            </article>
          </div>
        </section>
      )}

      {project && (
        <section className="notice">
          Created <strong>{project.project_name}</strong> at <code>{project.project_path}</code>. Files: {project.files.join(", ")}.
        </section>
      )}
    </section>
  );
}
