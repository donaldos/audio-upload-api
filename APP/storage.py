from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Tuple

import aiofiles
from fastapi import UploadFile, HTTPException

_FILENAME_SAFE_RE = re.compile(r"[^a-zA-Z0-9._-]+")

def sanitize_filename(name: str) -> str:
    """
    위험 문자 제거 및 길이 제한.
    """
    name = name.strip().replace("\\", "/").split("/")[-1]  # 경로 성분 제거
    name = _FILENAME_SAFE_RE.sub("_", name)
    if not name:
        name = "file"
    # 너무 긴 파일명 제한
    return name[:120]

def get_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    return ext

def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

async def save_uploadfile_streaming(
    upload_dir: str,
    request_uuid: str,
    original_filename: str,
    upload_file: UploadFile,
    max_bytes: int,
) -> Tuple[str, str, int]:
    """
    UploadFile을 chunk 단위로 읽어 디스크에 저장 (메모리 폭주 방지)
    - 저장 경로: {upload_dir}/{uuid}/{uuid}.{ext} (ext 없으면 bin)
    반환: (stored_path, stored_filename, bytes_written)
    """
    safe_original = sanitize_filename(original_filename)
    ext = get_extension(safe_original)
    if not ext:
        ext = "bin"

    # uuid 디렉토리 아래에 저장
    target_dir = Path(upload_dir) / request_uuid
    ensure_dir(target_dir)

    stored_filename = f"{request_uuid}.{ext}"
    target_path = target_dir / stored_filename

    bytes_written = 0
    chunk_size = 1024 * 1024  # 1MB

    try:
        async with aiofiles.open(target_path, "wb") as out:
            while True:
                chunk = await upload_file.read(chunk_size)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    # 부분 파일 삭제
                    try:
                        await out.close()
                    except Exception:
                        pass
                    try:
                        os.remove(target_path)
                    except Exception:
                        pass
                    raise HTTPException(status_code=413, detail="Uploaded file is too large.")
                await out.write(chunk)
    finally:
        await upload_file.close()

    return str(target_path), stored_filename, bytes_written
