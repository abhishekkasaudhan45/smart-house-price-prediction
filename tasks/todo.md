# Task List: Phase 2 — Docker + CI/CD

---

## Task 1: Dockerfile & Configuration

**Description:** Create `Backend_API/Dockerfile` and `.dockerignore` to containerize the Flask API. The image should copy model artifacts, install dependencies, and run via gunicorn. Test locally with `make docker-build` and `make docker-run`.

**Acceptance criteria:**
- [ ] `Dockerfile` exists at `Backend_API/Dockerfile`
- [ ] `.dockerignore` excludes `__pycache__`, notebooks, .git, training data
- [ ] `make docker-build` exits 0 and produces an image named `house-predictor`
- [ ] `make docker-run` starts the container, `curl localhost:10000/` returns 200
- [ ] `make docker-stop` stops and removes the container
- [ ] `POST /predict` returns a prediction from inside the container
- [ ] Image size is reasonable (< 1.5GB)

**Verification:**
- [ ] `docker build -t test-predictor -f Backend_API/Dockerfile .`
- [ ] `docker run -d -p 10000:10000 test-predictor && curl localhost:10000/`
- [ ] `curl -X POST localhost:10000/predict -H "Content-Type: application/json" -d '{...}'`
- [ ] `docker images | grep test-predictor` shows size

**Dependencies:** None (uses existing files)

**Files likely touched:**
- `Backend_API/Dockerfile` (NEW)
- `Backend_API/.dockerignore` (NEW)
- `Backend_API/requirements.txt` (may pin scikit-learn version)

**Scope:** Small (2-3 files)

---

## Task 2: CI/CD Pipeline Upgrade

**Description:** Upgrade `.github/workflows/ci.yml` to add a Docker build step and a deploy step that POSTs to the Render Deploy Hook on push to main.

**Important:** The `RENDER_DEPLOY_HOOK` secret must be added to GitHub repository secrets via the GitHub UI:
1. Go to repo → Settings → Secrets and variables → Actions
2. Add secret named `RENDER_DEPLOY_HOOK` with value: `https://api.render.com/deploy/srv-d99r65ecjfls738o2po0?key=ZZe7VZth5m0`

**Acceptance criteria:**
- [ ] CI runs `make check` (format + lint + pytest) on every push to any branch
- [ ] CI builds Docker image on every push (but does not deploy from non-main)
- [ ] CD deploys only on push to `main` by POSTing to `RENDER_DEPLOY_HOOK`
- [ ] Deploy step uses `curl --fail` to catch hook errors
- [ ] CI badge in README shows passing status

**Verification:**
- [ ] Push to any branch → CI triggers, all checks pass, Docker image builds, no deploy
- [ ] Push to `main` → CI passes, Docker builds, deploy step fires

**Dependencies:** Task 1 (Dockerfile must exist for the CI build step)

**Files likely touched:**
- `.github/workflows/ci.yml` (major edits)

**Scope:** Small (1 file)

---

## Checkpoint: Complete
- [ ] `make docker-build && make docker-run` works locally
- [ ] API responds from inside container
- [ ] CI/CD pipeline triggers on push
- [ ] Render auto-deploys from main
