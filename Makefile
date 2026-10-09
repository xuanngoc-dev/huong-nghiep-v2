# Định hướng nghề — lệnh tiện lợi
# Dùng: make <target>   hoặc   source scripts/aliases.sh rồi dùng alias dh-*

ROOT    := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BE      := $(ROOT)/backend
FE      := $(ROOT)/frontend
VENV    := $(BE)/.venv/bin
PY      := $(VENV)/python
UVICORN := $(VENV)/uvicorn
ALEMBIC := $(VENV)/alembic

# Đọc PORT từ backend/.env (mặc định 3060)
PORT := $(shell sed -n 's/^PORT=//p' $(BE)/.env 2>/dev/null)
ifeq ($(strip $(PORT)),)
  PORT := 3060
endif

.DEFAULT_GOAL := help

.PHONY: help install install-be install-fe be fe migrate migrate-down migrate-new migrate-history migrate-current stamp db-check

help: ## Hiện danh sách lệnh
	@echo ""
	@echo "  Định hướng nghề — lệnh tiện lợi"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Alias shell:  source scripts/aliases.sh"
	@echo ""

install: install-be install-fe ## Cài dependency backend + frontend

install-be: ## Cài Python deps (venv)
	@test -d $(BE)/.venv || python3 -m venv $(BE)/.venv
	$(VENV)/pip install -r $(BE)/requirements.txt

install-fe: ## Cài npm deps
	cd $(FE) && npm install

be: ## Chạy API FastAPI (reload)
	cd $(BE) && $(UVICORN) app.main:app --reload --host 0.0.0.0 --port $(PORT)

fe: ## Chạy frontend Vite
	cd $(FE) && npm run dev

migrate: ## Áp dụng migration (alembic upgrade head)
	cd $(BE) && $(ALEMBIC) upgrade head

migrate-down: ## Rollback 1 migration
	cd $(BE) && $(ALEMBIC) downgrade -1

migrate-new: ## Tạo migration mới (make migrate-new m="mo ta")
	@test -n "$(m)" || (echo 'Dùng: make migrate-new m="mo ta"'; exit 1)
	cd $(BE) && $(ALEMBIC) revision --autogenerate -m "$(m)"

migrate-history: ## Xem lịch sử migration
	cd $(BE) && $(ALEMBIC) history

migrate-current: ## Xem revision hiện tại
	cd $(BE) && $(ALEMBIC) current

stamp: ## Đánh dấu head (bảng đã có sẵn)
	cd $(BE) && $(ALEMBIC) stamp head

db-check: ## Kiểm tra kết nối MySQL
	cd $(BE) && $(PY) -m app.scripts.check_db
