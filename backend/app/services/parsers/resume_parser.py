from pathlib import Path

import fitz
from docx import Document


class ResumeParser:
    def parse(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._parse_pdf(path)
        if suffix == ".docx":
            return self._parse_docx(path)
        raise ValueError("Unsupported resume file type. Use PDF or DOCX.")

    def _parse_pdf(self, path: Path) -> str:
        with fitz.open(path) as document:
            return "\n".join(page.get_text() for page in document)

    def _parse_docx(self, path: Path) -> str:
        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())

