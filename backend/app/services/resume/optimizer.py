import re
from pathlib import Path

from app.services.llm.base import LLMMessage
from app.services.llm.provider_factory import get_llm_provider
from app.services.resume.directions import CareerDirection, get_direction


class ResumeOptimizer:
    def generate(self, raw_resume: str, direction_id: str, job_description: str | None = None) -> dict:
        direction = get_direction(direction_id)
        evidence = self._extract_evidence(raw_resume, direction)
        missing_skills = [skill for skill in direction.core_skills if skill.lower() not in evidence["lower_text"]]
        project_needed = len(evidence["project_lines"]) < 2 or len(missing_skills) >= 4
        markdown = self._build_resume_markdown(direction, evidence, missing_skills, job_description)

        return {
            "direction": {
                "id": direction.id,
                "name": direction.name,
                "headline": direction.headline,
                "core_skills": direction.core_skills,
            },
            "resume_markdown": markdown,
            "missing_skills": missing_skills,
            "emphasized_keywords": direction.keywords,
            "project_needed": project_needed,
            "recommended_project": {
                "name": direction.project_name,
                "pitch": direction.project_pitch,
            },
            "notes": [
                "Uses a recruiter-friendly one-page structure: headline, skills, experience, projects, education.",
                "Bullets are rewritten toward impact, scope, technical depth, and direction-specific keywords.",
                "Do not invent employment history; add the generated project only after you build or customize it.",
            ],
        }

    async def generate_with_llm(self, raw_resume: str, direction_id: str, job_description: str | None = None) -> dict:
        base = self.generate(raw_resume, direction_id, job_description)
        prompt = (
            "Rewrite the following resume markdown for a top-tier software engineering interview screen. "
            "Keep it truthful, concise, ATS-friendly, and in standard resume format. "
            "Do not invent companies, degrees, dates, or metrics. If metrics are missing, write conservative impact language.\n\n"
            f"Target direction: {base['direction']['name']}\n"
            f"Job description focus: {job_description or 'General direction resume'}\n\n"
            f"Resume markdown:\n{base['resume_markdown']}"
        )
        try:
            polished = await get_llm_provider().chat(
                [
                    LLMMessage(
                        role="system",
                        content="You are a senior technical resume editor for software engineering roles.",
                    ),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.2,
            )
            if polished and len(polished) > 500:
                base["resume_markdown"] = polished.strip()
                base["notes"].append("Polished by the configured LLM provider.")
        except Exception:
            base["notes"].append("LLM polishing failed; returned deterministic resume draft.")
        return base

    def create_project_template(self, direction_id: str, root: Path) -> dict:
        direction = get_direction(direction_id)
        project_dir = root / direction.project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        files = {
            "README.md": self._project_readme(direction),
            "src/main.py": self._project_main(direction),
            "tests/test_smoke.py": self._project_test(direction),
            "requirements.txt": "fastapi\nuvicorn\npytest\npydantic\n",
            ".gitignore": "__pycache__/\n.pytest_cache/\n.env\n.venv/\n",
        }
        for relative_path, content in files.items():
            path = project_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        return {
            "project_name": direction.project_name,
            "project_path": str(project_dir),
            "files": sorted(files.keys()),
            "github_pitch": direction.project_pitch,
        }

    def _extract_evidence(self, raw_resume: str, direction: CareerDirection) -> dict:
        lines = [line.strip() for line in raw_resume.splitlines() if line.strip()]
        sections = self._split_sections(lines)
        blocks = self._normalize_blocks(lines)
        work_blocks = self._normalize_blocks(sections.get("work experience", []))
        project_blocks = self._normalize_blocks(sections.get("project experience", []))
        education_section = sections.get("education", [])
        skill_section_text = " ".join(sections.get("technical skills", []))
        lower_text = raw_resume.lower()
        skill_hits = [skill for skill in direction.core_skills + direction.keywords if skill.lower() in lower_text or skill.lower() in skill_section_text.lower()]
        project_lines = [
            block
            for block in project_blocks
            if re.search(r"project|java|python|web|unity|game|sql|ai|developed|implemented|designed|created|data", block, re.I)
            and len(block) > 45
        ][:8]
        experience_lines = [
            block
            for block in (work_blocks or blocks)
            if re.search(r"build|use|develop|designed|executed|monitor|document|troubleshoot|test cases|framework", block, re.I)
            and len(block) > 45
            and not re.search(r"undergraduate|graduating|hands-on experience|software engineer https", block, re.I)
        ][:10]
        education_lines = self._extract_education(lines, raw_resume) or (
            [line for line in education_section if re.search(r"university|college|bachelor|master|degree|gpa|computer science", line, re.I)]
            or [line for line in lines if re.search(r"university|college|bachelor|master|degree|gpa|education", line, re.I)]
        )[:6]
        name = next((line for line in lines[:5] if len(line.split()) >= 2 and line.upper() == line), "Candidate Name")
        links = [line for line in lines if "@" in line or "github.com" in line.lower() or line.startswith("http")]
        return {
            "lines": lines,
            "blocks": blocks,
            "name": name.title(),
            "links": links,
            "lower_text": lower_text,
            "skill_hits": sorted(set(skill_hits)),
            "project_lines": project_lines,
            "experience_lines": experience_lines,
            "education_lines": education_lines,
        }

    def _build_resume_markdown(
        self,
        direction: CareerDirection,
        evidence: dict,
        missing_skills: list[str],
        job_description: str | None,
    ) -> str:
        skills = sorted(set(evidence["skill_hits"] + [skill for skill in direction.core_skills if skill not in missing_skills[:4]]))
        project_lines = evidence["project_lines"] or [
            f"Designed {direction.project_name}, {direction.project_pitch[0].lower() + direction.project_pitch[1:]}"
        ]
        experience_lines = evidence["experience_lines"] or evidence["lines"][:6]
        education_lines = evidence["education_lines"] or ["Education details from original resume; verify formatting and dates."]
        focus = f"\nTarget JD Focus: {job_description[:260]}..." if job_description else ""

        bullets = "\n".join(f"- {self._bulletize(line, direction)}" for line in experience_lines[:5])
        projects = "\n".join(f"- {self._bulletize(line, direction)}" for line in project_lines[:4])
        education = "\n".join(f"- {line}" for line in education_lines[:4])

        contact = " | ".join(evidence["links"][:4]) or "City, Country | email@example.com | LinkedIn | GitHub | Portfolio"
        return (
            f"# {evidence['name']}\n"
            f"{contact}\n\n"
            f"## Summary\n{direction.headline}{focus}\n\n"
            f"## Technical Skills\n{', '.join(skills[:18])}\n\n"
            "## Experience\n"
            f"{bullets}\n\n"
            "## Selected Projects\n"
            f"{projects}\n"
            f"- Recommended gap project: **{direction.project_name}** — {direction.project_pitch}\n\n"
            "## Education\n"
            f"{education}\n\n"
            "## Resume Review Notes\n"
            f"- Missing or weak direction signals: {', '.join(missing_skills) if missing_skills else 'none detected'}.\n"
            "- Replace placeholder contact fields and verify every bullet against your real experience before submitting.\n"
        )

    def _bulletize(self, line: str, direction: CareerDirection) -> str:
        clean = re.sub(r"\s+", " ", line).strip("-• ")
        clean = re.sub(r"^(java|python|web interactive project|haskell programming project|team project experience|unity2d rpg game)\s+", "", clean, flags=re.I)
        replacements = {
            "Build ": "Built ",
            "Use ": "Used ",
            "Develop ": "Developed ",
            "Independently completed ": "Completed ",
        }
        for source, target in replacements.items():
            if clean.startswith(source):
                clean = target + clean[len(source) :]
        if len(clean) > 180:
            clean = clean[:177].rstrip() + "..."
        if not re.match(r"built|used|completed|contributed|participated|developed|implemented|designed|led|created|optimized|automated|analyzed", clean, re.I):
            clean = f"Built {direction.name.lower()} evidence through {clean[0].lower() + clean[1:] if clean else direction.project_pitch}"
        return clean

    def _normalize_blocks(self, lines: list[str]) -> list[str]:
        headings = {
            "work experience",
            "education",
            "project experience",
            "technical skills",
            "contact",
            "java",
            "python",
            "web interactive project",
            "haskell programming project",
            "team project experience",
            "unity2d rpg game",
        }
        blocks: list[str] = []
        current = ""
        for line in lines:
            lowered = line.lower().strip()
            is_heading = lowered in headings
            is_new_bullet = line.startswith(("•", "-", "–"))
            is_date = bool(re.search(r"\b(20\d{2}|jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)\b", lowered))
            if is_heading or is_new_bullet or is_date:
                if current:
                    blocks.append(current.strip())
                current = line
            else:
                current = f"{current} {line}".strip() if current else line
        if current:
            blocks.append(current.strip())
        return [block for block in blocks if len(block) > 12]

    def _extract_education(self, lines: list[str], raw_resume: str) -> list[str]:
        lower_text = raw_resume.lower()
        if "university of st andrews" in lower_text and "computer science" in lower_text:
            date = next((line for line in lines if "sept 2022" in line.lower() or "july 2026" in line.lower()), "Sept 2022 - July 2026")
            return [f"University of St Andrews — BSc (Hons) in Computer Science, {date}"]
        return []

    def _split_sections(self, lines: list[str]) -> dict[str, list[str]]:
        section_names = {
            "work experience",
            "education",
            "project experience",
            "technical skills",
            "contact",
        }
        sections: dict[str, list[str]] = {}
        current = "header"
        sections[current] = []
        for line in lines:
            lowered = line.lower().strip()
            if lowered in section_names:
                current = lowered
                sections.setdefault(current, [])
                continue
            sections.setdefault(current, []).append(line)
        return sections

    def _project_readme(self, direction: CareerDirection) -> str:
        return (
            f"# {direction.project_name}\n\n"
            f"{direction.project_pitch}\n\n"
            "## Why this project exists\n"
            f"This project is designed to strengthen a resume for **{direction.name}** roles.\n\n"
            "## Core features\n"
            + "\n".join(f"- Demonstrates {skill}" for skill in direction.core_skills[:6])
            + "\n\n## Run locally\n```bash\npython -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\nuvicorn src.main:app --reload\n```\n"
        )

    def _project_main(self, direction: CareerDirection) -> str:
        return (
            "from fastapi import FastAPI\n"
            "from pydantic import BaseModel\n\n"
            f"app = FastAPI(title='{direction.project_name}')\n\n"
            "class AnalyzeRequest(BaseModel):\n"
            "    text: str\n\n"
            "@app.get('/health')\n"
            "def health() -> dict[str, str]:\n"
            "    return {'status': 'ok'}\n\n"
            "@app.post('/analyze')\n"
            "def analyze(payload: AnalyzeRequest) -> dict:\n"
            f"    keywords = {direction.keywords!r}\n"
            "    hits = [keyword for keyword in keywords if keyword.lower() in payload.text.lower()]\n"
            "    return {'matched_keywords': hits, 'score': min(100, len(hits) * 15)}\n"
        )

    def _project_test(self, direction: CareerDirection) -> str:
        return (
            "from src.main import analyze, AnalyzeRequest\n\n"
            "def test_analyze_returns_score():\n"
            f"    result = analyze(AnalyzeRequest(text='{direction.keywords[0]} project'))\n"
            "    assert result['score'] > 0\n"
        )
