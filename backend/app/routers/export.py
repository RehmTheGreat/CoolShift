"""Router for downloading results as CSV or XLSX."""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.database import get_db
from app.services.exporter import export_run_to_csv, export_run_to_xlsx

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/{run_id}/csv")
def download_csv(run_id: str, db: Session = Depends(get_db)):
    """Downloads the interval schedule of a run as a CSV file."""
    try:
        csv_content = export_run_to_csv(run_id, db)
        
        # Stream response
        response = Response(content=csv_content, media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={run_id}_schedule.csv"
        return response
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV: {str(e)}")

@router.get("/{run_id}/xlsx")
def download_xlsx(run_id: str, db: Session = Depends(get_db)):
    """Downloads the schedule and summary of a run as a multi-sheet Excel file."""
    try:
        xlsx_bytes = export_run_to_xlsx(run_id, db)
        
        response = Response(content=xlsx_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response.headers["Content-Disposition"] = f"attachment; filename={run_id}_results.xlsx"
        return response
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate XLSX: {str(e)}")
