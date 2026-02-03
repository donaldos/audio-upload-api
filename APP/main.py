from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from APP.config import settings
from APP.schemas import UploadResponse
from APP.storage import (
    sanitize_filename,
    get_extension,
    save_uploadfile_streaming,
)

app = FastAPI(title="Audio Upload Service", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_audio(
    # 1) 텍스트 파라미터
    request_uuid: str = Form(..., alias="uuid"),
    filename: str = Form(...),
    script: str = Form(...),
    # 2) 바이너리 파일
    audio: UploadFile = File(...),
):
    """
    multipart/form-data 로 받는 예:
    - uuid: 텍스트
    - filename: 텍스트 (원본 파일명)
    - script: 텍스트
    - audio: 파일(바이너리)
    """

    # 기본 검증
    request_uuid = request_uuid.strip()
    if not request_uuid:
        raise HTTPException(status_code=400, detail="uuid is required.")

    safe_name = sanitize_filename(filename)
    ext = get_extension(safe_name)

    # 확장자 allowlist (원하면 꺼도 됨)
    if ext and ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported extension: {ext}. Allowed: {sorted(settings.ALLOWED_EXTENSIONS)}",
        )

    # 업로드된 파일의 content-type 간단 체크(선택)
    # audio.content_type 예: audio/wav, audio/mpeg ...
    if audio.content_type and not audio.content_type.startswith("audio/"):
        # webm 등은 audio/webm으로 오지만, 일부는 application/octet-stream 일 수 있음 → 운영 정책에 맞게 조정
        # 여기서는 너무 엄격하지 않게: audio/가 아니면 경고 수준으로 막음
        raise HTTPException(status_code=400, detail=f"Invalid content_type: {audio.content_type}")

    # 파일 저장 (볼륨 경로)
    stored_path, stored_filename, bytes_written = await save_uploadfile_streaming(
        upload_dir=settings.UPLOAD_DIR,
        request_uuid=request_uuid,
        original_filename=safe_name,
        upload_file=audio,
        max_bytes=settings.MAX_UPLOAD_BYTES,
    )

    # script는 같이 저장하고 싶으면 텍스트 파일로 저장 가능(옵션)
    # 예: {uuid}/meta.txt 에 저장 등
    # 여기서는 응답만 반환 (원하면 meta 저장 로직 추가해드릴게요)

    return UploadResponse(
        request_uuid=request_uuid,
        stored_path=stored_path,
        original_filename=safe_name,
        stored_filename=stored_filename,
        bytes_written=bytes_written,
    )


# 에러 응답 형식 통일(선택)
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
