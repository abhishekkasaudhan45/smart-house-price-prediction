# Implementation Plan: Phase 2 — Docker Containerization & CI/CD Pipeline

## Overview

Containerize the Flask API with Docker and set up GitHub Actions CI/CD. Two tasks: (1) Dockerfile + configuration, (2) CI/CD pipeline with Render auto-deploy.

## Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Base image | `python:3.12-slim` | Smallest official Python image that supports scikit-learn |
| Model strategy | Copy pre-trained `.pkl` files | Faster builds, no retraining cost |
| WSGI server | gunicorn (inside container) | Production-grade, already in requirements |
| Deploy trigger | Render Deploy Hook (webhook URL) | Simplest auto-deploy — no Render API key needed |
| CD trigger | Push to `main` branch | Standard GitOps pattern |

## Dependency Graph

```
Dockerfile + .dockerignore
    │
    ├── make docker-build ──→ Image builds locally
    │
    └── ci.yml (modified)
            │
            ├── make check ──→ format + lint + test (every push)
            │
            └── Deploy step ──→ POST to Render hook (push to main)
```

## Implementation Order

```
Task 1: Dockerfile + .dockerignore
    ↓
Task 2: CI/CD pipeline (ci.yml upgrade)
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| scikit-learn version mismatch in container | Medium | Pin `scikit-learn==1.7.0` in requirements to match local version |
| Image too large (> 1.5GB) | Low | `.dockerignore` excludes notebooks, cache; slim base image |
| Render deploy hook fires but fails silently | Medium | Add `curl --fail` flag; log deploy hook response in CI |
| gunicorn not installed in container | Low | Already in `requirements.txt` |

## Open Questions

None resolved. User provided Render deploy hook URL.
