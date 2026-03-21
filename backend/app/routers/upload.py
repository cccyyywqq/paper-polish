from fastapi import APIRouter, UploadFile, File, HTTPException
from ..schemas.response import UploadResponse
from ..utils.file_parser import extract_text
from ..utils import logger

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件")

    allowed_extensions = [".docx", ".pdf", ".txt"]
    file_ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}"
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="文件大小超过限制(最大10MB)")

    try:
        text = extract_text(content, file.filename)

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="文件中未找到文本内容")

        logger.info(f"File uploaded: {file.filename}, extracted {len(text)} characters")

        return UploadResponse(
            filename=file.filename,
            text=text,
            char_count=len(text),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")
