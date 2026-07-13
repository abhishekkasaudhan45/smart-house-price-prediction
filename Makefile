# ============================================================
# Lucknow House Price Predictor — Makefile
# ============================================================
# Usage:
#   make help          → show all available commands
#   make install       → set up project from scratch
#   make run           → start the Flask API locally
#   make test          → run all pytest tests
#   make lint          → check code style (flake8)
#   make format        → auto-format code (black)
#   make check         → format + lint + test (pre-commit gate)
#   make docker-build  → build Docker image
#   make docker-run    → run app inside Docker
#   make docker-stop   → stop running Docker container
#   make clean         → remove cache and temp files
# ============================================================

# ── Variables ───────────────────────────────────────────────
APP_NAME    = lucknow-house-price
IMAGE_NAME  = lucknow-house-predictor
PORT        = 10000
PYTHON      = python
PIP         = pip
PYTEST      = pytest
BLACK       = black
FLAKE8      = flake8

# Source directories to lint/format/test
BACKEND     = Backend_API
FRONTEND    = Fronted_UI
TRAINING    = ML_Training
SRC_DIRS    = $(BACKEND) $(TRAINING)
TEST_DIR    = tests

.DEFAULT_GOAL := help

# ── Help ────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════╗"
	@echo "║   Lucknow House Price Predictor              ║"
	@echo "╚══════════════════════════════════════════════╝"
	@echo ""
	@echo "  Setup:"
	@echo "    make install        Install all dependencies"
	@echo ""
	@echo "  Development:"
	@echo "    make run            Start Flask API on port $(PORT)"
	@echo "    make test           Run all tests with pytest"
	@echo "    make lint           Check code style with flake8"
	@echo "    make format         Auto-format code with black"
	@echo "    make check          Run format + lint + test together"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-build   Build Docker image"
	@echo "    make docker-run     Run app in Docker container"
	@echo "    make docker-stop    Stop running container"
	@echo "    make docker-logs    View container logs"
	@echo ""
	@echo "  Cleanup:"
	@echo "    make clean          Remove cache and temp files"
	@echo ""

# ── Setup ───────────────────────────────────────────────────
.PHONY: install
install:
	@echo "📦 Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r $(BACKEND)/requirements.txt
	$(PIP) install pytest flake8 black pre-commit
	$(PYTHON) -m pre_commit install
	@echo "✅ Done! Run 'make run' to start the server."

# ── Development ─────────────────────────────────────────────
.PHONY: run
run:
	@echo "🚀 Starting Flask API on http://localhost:$(PORT)..."
	cd $(BACKEND) && $(PYTHON) app.py

.PHONY: test
test:
	@echo "🧪 Running tests..."
	$(PYTEST) $(TEST_DIR) -v --tb=short
	@echo "✅ All tests passed!"

.PHONY: lint
lint:
	@echo "🔍 Checking code style..."
	$(FLAKE8) $(SRC_DIRS) --max-line-length=88 --exclude=__pycache__,venv,.git
	@echo "✅ No style issues found!"

.PHONY: format
format:
	@echo "✨ Formatting code with black..."
	$(BLACK) $(SRC_DIRS) --line-length=88
	@echo "✅ Code formatted!"

.PHONY: check
check: format lint test
	@echo ""
	@echo "✅ All checks passed — safe to commit!"

# ── Docker ──────────────────────────────────────────────────
.PHONY: docker-build
docker-build:
	@echo "🐳 Building Docker image: $(IMAGE_NAME)..."
	docker build -t $(IMAGE_NAME) -f $(BACKEND)/Dockerfile .
	@echo "✅ Image built! Run 'make docker-run' to start."

.PHONY: docker-run
docker-run:
	@echo "🐳 Running container on http://localhost:$(PORT)..."
	docker run -d \
		--name $(APP_NAME) \
		-p $(PORT):$(PORT) \
		$(IMAGE_NAME)
	@echo "✅ Container started! Logs: make docker-logs"

.PHONY: docker-stop
docker-stop:
	@echo "🛑 Stopping container..."
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME)   || true
	@echo "✅ Container stopped."

.PHONY: docker-logs
docker-logs:
	docker logs -f $(APP_NAME)

# ── Cleanup ─────────────────────────────────────────────────
.PHONY: clean
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__"  -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info"   -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc"        -delete 2>/dev/null || true
	find . -type f -name "*.pyo"        -delete 2>/dev/null || true
	find . -type f -name ".coverage"    -delete 2>/dev/null || true
	@echo "✅ All clean!"
