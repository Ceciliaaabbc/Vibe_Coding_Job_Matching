from enum import StrEnum


class ApplicationStatus(StrEnum):
    DISCOVERED = "discovered"
    PARSED = "parsed"
    SCORED = "scored"
    PENDING_CONFIRMATION = "pending_confirmation"
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    WITHDRAWN = "withdrawn"
    SKIPPED = "skipped"


class MaterialStatus(StrEnum):
    DRAFT = "draft"
    EDITED = "edited"
    APPROVED = "approved"


class MaterialType(StrEnum):
    COVER_LETTER = "cover_letter"
    RESUME_SUGGESTION = "resume_suggestion"
    APPLICATION_NOTE = "application_note"
    INTERVIEW_PREP = "interview_prep"

