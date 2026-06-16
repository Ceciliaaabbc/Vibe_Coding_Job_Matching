import { Check, X } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Application, ApplicationDetail, Material } from "../types";

export function PendingPage() {
  const [items, setItems] = useState<Application[]>([]);
  const [detail, setDetail] = useState<ApplicationDetail | null>(null);
  const [draft, setDraft] = useState("");

  async function load() {
    const response = await api.get<Application[]>("/applications/pending");
    setItems(response.data);
  }

  async function confirm(id: string) {
    await api.post(`/applications/${id}/confirm`);
    setDetail(null);
    await load();
  }

  async function skip(id: string) {
    await api.post(`/applications/${id}/skip`);
    setDetail(null);
    await load();
  }

  async function openDetail(id: string) {
    const response = await api.get<ApplicationDetail>(`/applications/${id}`);
    setDetail(response.data);
    setDraft(response.data.materials.find((item) => item.material_type === "cover_letter")?.content ?? "");
  }

  async function saveMaterial(material: Material) {
    const response = await api.put<Material>(`/materials/${material.id}`, { content: draft });
    setDetail((current) => {
      if (!current) return current;
      return {
        ...current,
        materials: current.materials.map((item) => (item.id === material.id ? response.data : item)),
      };
    });
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <section>
      <header className="page-header">
        <h1>Pending Confirmation</h1>
        <p>Every application must be reviewed here before it can be marked as applied.</p>
      </header>

      <div className="list">
        {items.map((item) => (
          <article className="list-row clickable" key={item.id} onClick={() => openDetail(item.id)}>
            <div>
              <strong>{item.job_id}</strong>
              <span>{item.application_note ?? "Review match reasons and materials before confirming."}</span>
            </div>
            <div className="row-actions">
              <button
                className="icon-button confirm"
                onClick={(event) => {
                  event.stopPropagation();
                  confirm(item.id);
                }}
                title="Confirm application"
              >
                <Check size={18} />
              </button>
              <button
                className="icon-button skip"
                onClick={(event) => {
                  event.stopPropagation();
                  skip(item.id);
                }}
                title="Skip application"
              >
                <X size={18} />
              </button>
            </div>
          </article>
        ))}
        {items.length === 0 && <p className="empty-state">No jobs are waiting for confirmation.</p>}
      </div>

      {detail && (
        <section className="detail-drawer">
          <header>
            <div>
              <h2>
                {detail.job.company} · {detail.job.title}
              </h2>
              <p>{detail.job.location || "Location not specified"}</p>
            </div>
            {detail.job.url && (
              <a href={detail.job.url} target="_blank" rel="noreferrer">
                Open job
              </a>
            )}
          </header>

          {detail.match && (
            <div className="score-grid">
              <span>Overall {detail.match.score}</span>
              <span>Keyword {detail.match.keyword_score}</span>
              <span>Semantic {detail.match.semantic_score}</span>
              <span>Requirements {detail.match.requirement_score}</span>
            </div>
          )}

          <div className="detail-columns">
            <article>
              <h3>Match Reasons</h3>
              <ul>
                {(detail.match?.reasons_json.items ?? []).map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
              <h3>Missing Skills</h3>
              <div className="chips">
                {(detail.match?.missing_skills_json.items ?? []).map((skill) => (
                  <span key={skill}>{skill}</span>
                ))}
              </div>
            </article>

            <article>
              <h3>Cover Letter</h3>
              <textarea rows={13} value={draft} onChange={(event) => setDraft(event.target.value)} />
              {detail.materials[0] && (
                <button className="secondary-button" type="button" onClick={() => saveMaterial(detail.materials[0])}>
                  Save Draft
                </button>
              )}
            </article>
          </div>

          <div className="drawer-actions">
            <button className="primary-button" onClick={() => confirm(detail.application.id)} type="button">
              <Check size={18} />
              Confirm Applied
            </button>
            <button className="secondary-button danger" onClick={() => skip(detail.application.id)} type="button">
              <X size={18} />
              Skip
            </button>
          </div>
        </section>
      )}
    </section>
  );
}
