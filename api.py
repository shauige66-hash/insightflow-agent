# 提供 InsightFlow 的 FastAPI 服务入口。

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile as FastAPIUploadFile,
)
from services.analysis_service import run_analysis
from pathlib import Path
import shutil
from utils.run_logger import create_run_id
from fastapi.responses import FileResponse
from pydantic import WithJsonSchema
from typing import Annotated



UploadFile = Annotated[
    FastAPIUploadFile,
    WithJsonSchema(
        {
            "type": "string",
            "format": "binary"
        }
    )
]
UPLOAD_DIR = Path("uploads")
app = FastAPI(
    
    title="InsightFlow API",
    description=(
        "Agentic Data Intelligence Platform "
        "powered by LangGraph and LangChain."
    ),
    version="0.1.0"
)





@app.get("/health")
def health_check() -> dict[str, str]:

    return {
        "status": "ok",
        "service": "InsightFlow"
    }


@app.post("/analyze/upload")
def analyze_upload(
    files: list[UploadFile] = File(...),
    analysis_focus: str | None = Form(None)
) -> dict:

    run_id = create_run_id()

    run_upload_dir = (
        UPLOAD_DIR / run_id
    )

    run_upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    data_sources = []

    allowed_suffixes = {
        ".csv",
        ".xlsx",
        ".db",
        ".sqlite",
        ".sqlite3",
    }

    for uploaded_file in files:

        filename = Path(
            uploaded_file.filename or ""
        ).name

        suffix = Path(
            filename
        ).suffix.lower()

        if suffix not in allowed_suffixes:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file type: "
                    f"{filename}"
                )
            )

        file_path = (
            run_upload_dir
            / filename
        )

        with file_path.open(
            "wb"
        ) as output_file:

            shutil.copyfileobj(
                uploaded_file.file,
                output_file
            )

        data_sources.append(
            str(file_path)
        )

    try:
        result = run_analysis(
            data_sources=data_sources,
            analysis_focus=analysis_focus,
            run_id=run_id
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        ) from error

    return {
        "run_id": result.get(
            "run_id"
        ),
        "analysis_plan": result.get(
            "analysis_plan",
            []
        ),
        "failed_tasks": result.get(
            "failed_tasks",
            []
        ),
        "visualization_plan": result.get(
            "visualization_plan",
            []
        ),
        "visualization_results": result.get(
            "visualization_results",
            []
        ),
        "report_content": result.get(
            "report_content"
        ),
        "report_path": result.get(
            "report_path"
        ),
        "artifacts": result.get(
            "artifacts",
            []
        )
    }


@app.get("/runs/{run_id}/report")
def download_report(
    run_id: str
):

    report_path = (
        Path("outputs")
        / run_id
        / "analysis_report.pdf"
    )

    if not report_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Report not found for run: "
                f"{run_id}"
            )
        )

    return FileResponse(
        path=str(report_path),
        media_type="application/pdf",
        filename=f"{run_id}_report.pdf"
    )