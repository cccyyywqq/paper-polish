from fastapi import APIRouter, UploadFile, File, HTTPException
from ..schemas.response import UploadResponse
from ..utils.file_parser import extract_text
from ..utils import logger
from ..config import get_settings

settings = get_settings()
router = APIRouter()

MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024
ALLOWED_EXTENSIONS = {".docx", ".pdf", ".txt"}


@router.post("/file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")

    file_ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 '{file_ext}'，仅支持: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"文件过大 ({size_mb:.1f}MB)，最大允许 {settings.max_file_size_mb}MB",
        )

    if file_size == 0:
        raise HTTPException(status_code=400, detail="文件为空")

    try:
        text = extract_text(content, file.filename)
    except Exception as e:
        logger.error(f"File parsing error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"文件解析失败: {str(e)}。请确保文件未损坏且格式正确。",
        )

    if not text or not text.strip():
        suggestions = {
            ".pdf": "PDF 可能是扫描版图片，建议使用 OCR 工具处理后重试",
            ".docx": "DOCX 文件可能格式损坏，请尝试用 Word 重新保存后上传",
            ".txt": "TXT 文件编码可能不支持，请确保使用 UTF-8 编码",
        }
        suggestion = suggestions.get(file_ext, "请检查文件内容是否正确")
        raise HTTPException(
            status_code=422,
            detail=f"文件中未提取到文本内容。{suggestion}",
        )

    logger.info(f"File uploaded: {file.filename}, size: {file_size}, extracted: {len(text)} chars")

    return UploadResponse(
        filename=file.filename,
        text=text,
        char_count=len(text),
    )
