# Architecture

## Runtime Components

```text
React frontend
  -> FastAPI backend
    -> PostgreSQL for business data
    -> ChromaDB for embeddings
    -> LLM providers for structured extraction and generation
    -> Legal job data connectors
```

## Compliance Boundary

The backend may discover, analyze, rank, and draft application materials. It must not mark an application as applied unless a user confirmation event exists.

Restricted platforms such as LinkedIn, Boss Zhipin, Glassdoor, and similar sites should be integrated as external-link or user-import workflows unless an official or user-authorized API is available.

## Application State Flow

```text
discovered
  -> parsed
  -> scored
  -> pending_confirmation
  -> applied
  -> interviewing
  -> offer
```

Alternative terminal states:

```text
skipped
rejected
withdrawn
```

