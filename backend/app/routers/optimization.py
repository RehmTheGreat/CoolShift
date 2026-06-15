"""Router for running the optimization calculations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import OptimizationRun
from app.schemas import OptimizationRequest, OptimizationResponse
from app.services.optimizer import run_optimization

router = APIRouter(prefix="/optimization", tags=["Optimization"])

@router.post("/run", response_model=OptimizationResponse, status_code=status.HTTP_200_OK)
def trigger_optimization(request: OptimizationRequest, db: Session = Depends(get_db)):
    """Runs baseline and optimization calculations for a scenario."""
    try:
        run_id = run_optimization(request.scenario_id, db, request.algorithm_version)
        
        # Query the completed run to get runtime details
        run = db.query(OptimizationRun).filter_by(run_id=run_id).first()
        if not run:
            raise HTTPException(status_code=500, detail="Optimization run completed but record was not found.")
            
        return OptimizationResponse(
            run_id=run.run_id,
            scenario_id=run.scenario_id,
            status=run.status,
            runtime_seconds=run.runtime_seconds or 0.0,
            message=f"Optimization run {run_id} completed successfully.",
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization execution failed: {str(e)}")

@router.get("/runs", response_model=List[Dict[str, Any]])
def list_optimization_runs(db: Session = Depends(get_db)):
    """Lists history of optimization runs."""
    runs = db.query(OptimizationRun).order_by(OptimizationRun.created_at.desc()).all()
    result = []
    for r in runs:
        result.append({
            "id": r.id,
            "run_id": r.run_id,
            "scenario_id": r.scenario_id,
            "algorithm_version": r.algorithm_version,
            "created_at": r.created_at.isoformat(),
            "runtime_seconds": r.runtime_seconds,
            "status": r.status,
        })
    return result

@router.get("/status/{run_id}", response_model=Dict[str, Any])
def get_run_status(run_id: str, db: Session = Depends(get_db)):
    """Get status and metadata for a specific run."""
    run = db.query(OptimizationRun).filter_by(run_id=run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return {
        "run_id": run.run_id,
        "scenario_id": run.scenario_id,
        "status": run.status,
        "runtime_seconds": run.runtime_seconds,
        "created_at": run.created_at.isoformat(),
    }
