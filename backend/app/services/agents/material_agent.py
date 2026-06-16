from app.models.entities import Job, Resume
from app.services.llm.base import LLMMessage
from app.services.llm.provider_factory import get_llm_provider


class MaterialAgent:
    async def draft_cover_letter(self, resume: Resume | None, job: Job, match_result: dict | None = None) -> str:
        prompt = self._build_cover_letter_prompt(resume, job, match_result)
        try:
            return await get_llm_provider().chat(
                [
                    LLMMessage(
                        role="system",
                        content=(
                            "You are a senior job application assistant. "
                            "Write concise, honest, tailored application materials. "
                            "Never invent experience that is not supported by the resume."
                        ),
                    ),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.4,
            )
        except Exception:
            return self._fallback_cover_letter(resume, job, match_result)

    def _build_cover_letter_prompt(self, resume: Resume | None, job: Job, match_result: dict | None = None) -> str:
        matched = ", ".join((match_result or {}).get("matched_skills", [])) or "relevant experience"
        missing = ", ".join((match_result or {}).get("missing_skills", [])) or "none identified"
        resume_text = (resume.raw_text[:2500] if resume else "No resume text available.")
        return (
            "Generate a polished cover letter draft for this job application.\n\n"
            f"Company: {job.company}\n"
            f"Role: {job.title}\n"
            f"Location: {job.location or 'Not specified'}\n"
            f"Matched skills: {matched}\n"
            f"Missing skills to avoid overstating: {missing}\n\n"
            f"Job description:\n{job.raw_description[:3000]}\n\n"
            f"Resume excerpt:\n{resume_text}\n\n"
            "Requirements:\n"
            "- 180-260 words.\n"
            "- Use a confident but natural tone.\n"
            "- Mention specific overlap between resume and JD.\n"
            "- Do not claim missing skills as proven experience.\n"
            "- Return only the cover letter text."
        )

    def _fallback_cover_letter(self, resume: Resume | None, job: Job, match_result: dict | None = None) -> str:
        matched = ", ".join((match_result or {}).get("matched_skills", [])) or "relevant experience"
        resume_hint = "my background" if resume is None else "the experience reflected in my resume"
        return (
            f"Dear Hiring Team,\n\n"
            f"I am excited to apply for the {job.title} role at {job.company}. "
            f"Based on {resume_hint}, I can contribute strongly in areas such as {matched}. "
            f"The role's responsibilities align with my interest in building practical, reliable AI and software systems.\n\n"
            f"I would welcome the opportunity to discuss how my experience can support {job.company}'s goals.\n\n"
            f"Best regards"
        )

    def draft_application_note(self, job: Job, match_result: dict | None = None) -> str:
        score = (match_result or {}).get("score", "N/A")
        return f"匹配度：{score}/100。投递前请检查 cover letter、岗位链接和平台要求。"
