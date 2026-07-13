# Spec: Phase 2 — Docker Containerization & CI/CD Pipeline

## Objective

Containerize the Lucknow House Price Predictor Flask API with Docker, and set up a GitHub Actions CI/CD pipeline that runs tests, builds the image, and auto-deploys to Render. This proves production engineering skills: containerization, CI/CD, and infrastructure-as-code.

**Success criteria:**
- `docker build` produces a working image serving the API on port 10000
- `docker run` starts the API, responds to all 3 endpoints
- GitHub Actions runs `make check` (format + lint + test) on every push
- On push to `main`, GitHub Actions deploys to Render via deploy hook
- Image is < 1.5GB (with pre-trained model artifacts)
- Makefile docker targets (`docker-build`, `docker-run`, `docker-stop`) work end-to-end

---

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Docker | 24+ | Containerization |
| GitHub Actions | — | CI/CD pipeline |
| Render Deploy Hooks | — | Trigger production deploy from CI |
| gunicorn | Already in requirements | Production WSGI server inside container |

---

## Commands

```bash
# Build Docker image
cd Backend_API && docker build -t house-predictor .
# or
make docker-build

# Run container locally
docker run -d --name lucknow-house-price -p 10000:10000 house-predictor
# or
make docker-run

# Stop container
make docker-stop

# View logs
make docker-logs

# Full CI check (runs on every push)
make check
```

---

## Project Structure (Additions)

```
Backend_API/
├── Dockerfile             # NEW — multi-stage or single-stage image
├── .dockerignore          # NEW — excludes training junk

.github/workflows/
├── ci.yml                 # MODIFIED — add Docker build + Render deploy
```

---

## Code Style

### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system deps (for scikit-learn, numpy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model artifacts and app
COPY model.pkl scaler.pkl label_encoders.pkl feature_columns.pkl model_metrics.pkl ./
COPY feature_importance.png actual_vs_predicted.png ./
COPY app.py .

EXPOSE 10000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
```

### CI/CD Pipeline (ci.yml additions)
```yaml
deploy:
  needs: check
  if: github.ref == 'refs/heads/main'
  steps:
    - run: curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

---

## Testing Strategy

| Level | What | How |
|---|---|---|
| Local | `make test` runs 7 pytest tests | Same tests from Phase 1 |
| Container | `curl localhost:10000/` after `docker run` | Manual smoke test |
| CI | `make check` runs format + lint + pytest | On every push |
| CD | Render deploy hook fires after tests pass | On push to main |

No Docker-in-CI testing for now (too complex for Phase 2). The CI just builds the image and deploys.

---

## Boundaries

- **Always do:** Use `.dockerignore` to exclude notebooks, cache, git. Pin Python version in base image. Use `--no-cache-dir` for pip. Use gunicorn inside the container, not Flask dev server.
- **Ask first:** Adding multi-stage builds, switching base image, adding Docker Compose with extra services, adding Docker-in-CI integration tests.
- **Never do:** Hardcode secrets in Dockerfile or CI config. Store model training data inside the image. Use `:latest` tag without pinning.

---

## Success Criteria Checklist

- [ ] `make docker-build` exits 0
- [ ] `make docker-run` starts the container, `curl localhost:10000/` returns 200
- [ ] `make docker-stop` stops and removes the container
- [ ] GitHub Actions CI runs on push: format → lint → test → all green
- [ ] GitHub Actions CD triggers on push to main: POST to Render deploy hook
- [ ] Render receives deploy hook and redeploys
- [ ] Image size < 1.5GB (docker images)

---

## Open Questions

None — all decisions made in the ideation session:
- Docker only, no PostgreSQL this phase
- Pre-trained model artifacts copied into image (not retrained)
- CI + auto-deploy to Render via deploy hook
