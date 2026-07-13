# Resume-Ready Upgrades — Lucknow House Price Predictor

## Problem Statement

The project is functionally complete (deployed ML API + frontend with 4 models, SHAP, and validation) but lacks the engineering rigor signals that full-stack/Python dev hiring managers look for: tests, linting, CI/CD, Docker, and database fluency.

## Recommended Direction

Build the upgrades in three ordered phases. Phase 1 (professional dev workflow) is the highest-ROI move — it signals "this person writes code like a professional" within hours, not weeks. Phase 2 (containerization) proves DevOps readiness. Phase 3 (database) adds SQL proficiency.

| Phase | Focus | Time | Resume Signal |
|---|---|---|---|
| 1 | Makefile, pytest, black, flake8, pre-commit, GitHub Actions CI | 2 days | "Maintained code quality with pytest, black, and GitHub Actions CI" |
| 2 | Dockerfile, docker-compose, Render deploy via CI | 3-4 days | "Containerized ML API with Docker, deployed via GitHub Actions" |
| 3 | PostgreSQL + SQLAlchemy, Alembic migrations, prediction history | 5-7 days | "Designed PostgreSQL schema with SQLAlchemy ORM and Alembic migrations" |

## Key Assumptions to Validate

- [ ] **pytest tests actually run on GitHub Actions CI** — Ubuntu runner, scikit-learn version mismatch may cause pickle load warnings
- [ ] **Pre-commit hooks work cross-platform** — `.pre-commit-config.yaml` hooks must resolve on Windows dev + Linux CI
- [ ] **Docker image is small enough** — scikit-learn + xgboost + numpy is ~1GB base image; need `.dockerignore` to exclude training notebooks
- [ ] **Postgres migration from pickle is worth the complexity** — for a demo project with 1k synthetic rows, pickle is actually fine. The resume value is showing you *know* SQL, not that the app needs it

## MVP Scope

Phase 1 only. This is the minimum that proves professional engineering habits:

- `Makefile` with `install`, `run`, `test`, `lint`, `format`, `check`, `clean` targets
- `pytest` with 7 tests covering health, prediction, validation, metrics
- `black` + `flake8` config with `pyproject.toml` and `.flake8`
- `.pre-commit-config.yaml` with trailing-whitespace, black, flake8
- GitHub Actions CI workflow running `make check` on push/PR
- Badge in README: `[![CI](https://github.com/.../workflows/CI/badge.svg)]`

## Not Doing (and Why)

- **Skip NextJS rewrite** — 1-2 week job for a learner, doesn't add ML value. The vanilla JS frontend works fine.
- **Skip full platform (Phase 1+2+3 combined)** — That's a month. The phases build on each other naturally; do them sequentially.
- **Skip API keys/rate limiting** — Niche resume signal for API-product companies. Not general full-stack.
- **Skip prediction history UI** — If we add a database (Phase 3), don't build a frontend for history. Just show the schema + migration in the repo.
- **Skip pre-commit.ci SaaS** — Use GitHub Actions instead. One less service to manage.

## Open Questions

- Should Phase 2 Dockerfile copy model artifacts or rebuild them in the container? (Rebuilding adds time to CI, copying keeps the image smaller.)
- Phase 3: SQLite instead of Postgres for simplicity? Still proves SQL/ORM but avoids needing a running Postgres instance for local dev.
