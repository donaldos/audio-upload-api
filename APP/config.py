from pydantic import BaseModel
import os

class Settings(BaseModel):
    # 컨테이너 내부 저장 경로 (Docker에서 볼륨 마운트 권장)
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/data/uploads")
    # 최대 파일 크기(바이트) - 서버 단에서 1차 방어
    MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(50 * 1024 * 1024)))  # 기본 50MB
    # 허용 확장자(선택)
    ALLOWED_EXTENSIONS: set[str] = set(
        (os.getenv("ALLOWED_EXTENSIONS", "wav,mp3,m4a,ogg,webm").split(","))
    )

settings = Settings()
