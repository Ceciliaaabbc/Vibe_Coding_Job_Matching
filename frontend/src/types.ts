export type Resume = {
  id: string;
  file_name: string;
  file_type: string;
  raw_text?: string | null;
  parsed_json: Record<string, unknown>;
};

export type AuthUser = {
  id: string;
  email: string;
  name: string | null;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type CareerDirection = {
  id: string;
  name: string;
  headline: string;
  core_skills: string[];
  keywords: string[];
};

export type OptimizedResume = {
  direction: {
    id: string;
    name: string;
    headline: string;
    core_skills: string[];
  };
  resume_markdown: string;
  missing_skills: string[];
  emphasized_keywords: string[];
  project_needed: boolean;
  recommended_project: {
    name: string;
    pitch: string;
  };
  notes: string[];
};

export type GeneratedProject = {
  project_name: string;
  project_path: string;
  files: string[];
  github_pitch: string;
};

export type Job = {
  id: string;
  company: string;
  title: string;
  location: string | null;
  url: string | null;
  raw_description: string;
  parsed_jd_json: Record<string, unknown>;
};

export type MatchScore = {
  id: string;
  score: number;
  keyword_score: number;
  semantic_score: number;
  requirement_score: number;
  matched_skills_json: { items?: string[] };
  missing_skills_json: { items?: string[] };
  reasons_json: { items?: string[] };
  recommendation: string;
};

export type Material = {
  id: string;
  job_id: string;
  resume_id: string | null;
  material_type: string;
  content: string;
  version: number;
  status: string;
};

export type Application = {
  id: string;
  job_id: string;
  resume_id: string | null;
  match_score_id: string | null;
  status: string;
  confirmed_by_user: boolean;
  application_note: string | null;
};

export type ApplicationDetail = {
  application: Application;
  job: Job;
  match: MatchScore | null;
  materials: Material[];
};
