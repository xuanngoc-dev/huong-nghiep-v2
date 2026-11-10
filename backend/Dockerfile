# Backend FastAPI. Build context là THƯ MỤC GỐC dự án để copy được data_dh_json:
#   docker build -f backend/Dockerfile -t huongnghiep-backend .
#
# Cấu trúc trong image giữ giống repo để các đường dẫn tương đối trong code vẫn đúng:
#   /srv/backend/app, /srv/backend/data, /srv/data_dh_json
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=3060

WORKDIR /srv/backend

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/alembic.ini ./
COPY backend/alembic ./alembic
COPY backend/data ./data
COPY backend/app ./app
COPY data_dh_json /srv/data_dh_json

# Chạy bằng user thường; logs và thu_vien là thư mục ghi được (nên mount volume)
RUN useradd --system --uid 1000 --no-create-home app \
    && mkdir -p logs thu_vien tai_lieu \
    && chown -R app:app logs thu_vien tai_lieu
RUN chown -R app:app /srv
USER app

EXPOSE 3060

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
