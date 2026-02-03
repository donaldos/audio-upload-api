FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# (권장) non-root 유저
RUN useradd -m appuser

# 의존성 설치 캐시 최적화
COPY APP/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 앱 소스
COPY APP /app/APP

# 업로드 디렉토리(컨테이너 내부) 생성 및 권한
RUN mkdir -p /data/uploads && chown -R appuser:appuser /data/uploads

USER appuser

EXPOSE 8000
ENV UPLOAD_DIR=/data/uploads

CMD ["uvicorn", "APP.main:app", "--host", "0.0.0.0", "--port", "8000"]
