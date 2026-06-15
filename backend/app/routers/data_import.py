"""Router for file imports and validation checks."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.importer import parse_and_import_excel, import_excel_with_validation
from app.services.validator import validate_scenario_data
from app.schemas import ImportResponse

router = APIRouter(prefix="/import", tags=["Data Import"])

@router.post("/excel", response_model=ImportResponse)
async def import_excel_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads the CoolShift Excel sheet containing scenario inputs."""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported.")
        
    try:
        content = await file.read()
        result = import_excel_with_validation(content, db)
        
        if not result["success"]:
            err_msg = "Validation failed:\n" + "\n".join(result["errors"][:15])
            if len(result["errors"]) > 15:
                err_msg += f"\n... and {len(result['errors']) - 15} more errors."
            raise HTTPException(status_code=400, detail=err_msg)
            
        counts = result["imported_counts"]
        msg = f"Excel file '{file.filename}' parsed and imported successfully."
        
        return ImportResponse(
            scenario_id="MULTIPLE",
            message=msg,
            rows_imported=counts,
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.get("/validate/{scenario_id}")
def validate_scenario(scenario_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Runs data validations for the scenario profile and interval timeseries."""
    try:
        report = validate_scenario_data(scenario_id, db)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
