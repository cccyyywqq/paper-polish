from fastapi import APIRouter, UploadFile, File, HTTPException
from ..utils.file_parser import extract_text
from ..utils import logger

router = APIRouter()


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_extensions = [".docx", ".pdf", ".txt"]
    file_ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        content = await file.read()
        text = extract_text(content, file.filename)

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="No text content found in file")

        logger.info(f"File uploaded: {file.filename}, extracted {len(text)} characters")

        return {
            "success": True,
            "filename": file.filename,
            "text": text,
            "char_count": len(text),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")
