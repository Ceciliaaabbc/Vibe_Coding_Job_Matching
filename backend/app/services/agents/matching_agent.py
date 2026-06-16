from app.models.entities import Job, Resume


class MatchingAgent:
    def score(self, resume: Resume, job: Job, semantic_score: int | None = None, rag_context: list[str] | None = None) -> dict:
        jd = job.parsed_jd_json or {}
        required_skills = set(jd.get("required_skills", []))
        resume_text = resume.raw_text.lower()
        matched = sorted(skill for skill in required_skills if skill.lower() in resume_text)
        missing = sorted(required_skills - set(matched))

        keyword_score = int((len(matched) / max(len(required_skills), 1)) * 100)
        semantic_score = semantic_score if semantic_score is not None else 70 if matched else 45
        requirement_score = max(0, 100 - len(missing) * 15)
        score = round(keyword_score * 0.4 + semantic_score * 0.4 + requirement_score * 0.2)

        recommendation = "建议投递" if score >= 70 else "可考虑" if score >= 55 else "不建议投递"
        return {
            "score": score,
            "keyword_score": keyword_score,
            "semantic_score": semantic_score,
            "requirement_score": requirement_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "reasons": self._build_reasons(matched, missing, score, rag_context or []),
            "recommendation": recommendation,
        }

    def _build_reasons(self, matched: list[str], missing: list[str], score: int, rag_context: list[str]) -> list[str]:
        reasons = []
        if matched:
            reasons.append(f"简历覆盖了核心技能：{', '.join(matched)}。")
        if missing:
            reasons.append(f"需要补充或弱化风险的技能：{', '.join(missing)}。")
        if rag_context:
            reasons.append("RAG 检索找到了与该岗位相关的简历片段，可用于定制 cover letter。")
        reasons.append(f"综合匹配分为 {score}/100，需由用户确认后才能进入投递。")
        return reasons
