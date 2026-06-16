import re


class JDParser:
    def parse(self, raw_description: str) -> dict:
        skills = self._extract_skills(raw_description)
        return {
            "required_skills": skills,
            "preferred_skills": [],
            "hard_requirements": self._extract_hard_requirements(raw_description),
            "nice_to_have": [],
            "responsibilities": self._extract_responsibilities(raw_description),
        }

    def _extract_skills(self, text: str) -> list[str]:
        known_skills = [
            "Python",
            "FastAPI",
            "React",
            "PostgreSQL",
            "Docker",
            "Kubernetes",
            "LLM",
            "RAG",
            "ChromaDB",
            "LangChain",
            "AWS",
            "Azure",
            "GCP",
        ]
        lower_text = text.lower()
        return [skill for skill in known_skills if skill.lower() in lower_text]

    def _extract_hard_requirements(self, text: str) -> list[str]:
        patterns = [
            r"\b\d+\+?\s+years? of experience\b",
            r"\bmust have\b[^.]*",
            r"\brequired\b[^.]*",
        ]
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text, flags=re.IGNORECASE))
        return [match.strip() for match in matches]

    def _extract_responsibilities(self, text: str) -> list[str]:
        lines = [line.strip("-• \t") for line in text.splitlines()]
        return [line for line in lines if len(line) > 40][:8]

