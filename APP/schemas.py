from pydantic import BaseModel, Field

class UploadResponse(BaseModel):
    request_uuid: str = Field(..., description="요청으로 받은 UUID")
    stored_path: str = Field(..., description="저장된 파일 경로(컨테이너 내부 기준)")
    original_filename: str
    stored_filename: str
    bytes_written: int
