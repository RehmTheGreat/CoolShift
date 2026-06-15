"""Router for scenario profiles, appliances, and assets CRUD."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import ScenarioProfile, Appliance, EnergyAsset
from app.schemas import ScenarioProfileSchema, ApplianceSchema, EnergyAssetSchema, ErrorResponse

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.get("/", response_model=List[ScenarioProfileSchema])
def list_scenarios(db: Session = Depends(get_db)):
    """List all scenario profiles."""
    return db.query(ScenarioProfile).all()

@router.get("/{scenario_id}", response_model=ScenarioProfileSchema)
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Get details of a single scenario profile."""
    profile = db.query(ScenarioProfile).filter_by(scenario_id=scenario_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return profile

@router.post("/", response_model=ScenarioProfileSchema, status_code=status.HTTP_201_CREATED)
def create_scenario(profile_data: ScenarioProfileSchema, db: Session = Depends(get_db)):
    """Create a new scenario profile."""
    existing = db.query(ScenarioProfile).filter_by(scenario_id=profile_data.scenario_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Scenario with ID '{profile_data.scenario_id}' already exists.")
        
    profile = ScenarioProfile(**profile_data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.put("/{scenario_id}", response_model=ScenarioProfileSchema)
def update_scenario(scenario_id: str, profile_data: ScenarioProfileSchema, db: Session = Depends(get_db)):
    """Update an existing scenario profile."""
    profile = db.query(ScenarioProfile).filter_by(scenario_id=scenario_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
        
    for key, value in profile_data.model_dump().items():
        setattr(profile, key, value)
        
    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Delete a scenario profile and all cascade-related data."""
    profile = db.query(ScenarioProfile).filter_by(scenario_id=scenario_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    db.delete(profile)
    db.commit()
    return

# Sub-resources: Appliances & Energy Assets
@router.get("/{scenario_id}/appliances", response_model=List[ApplianceSchema])
def get_appliances(scenario_id: str, db: Session = Depends(get_db)):
    """Get appliances defined for a scenario."""
    # check if scenario exists
    profile = db.query(ScenarioProfile).filter_by(scenario_id=scenario_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return db.query(Appliance).filter_by(scenario_id=scenario_id).all()

@router.get("/{scenario_id}/assets", response_model=EnergyAssetSchema)
def get_assets(scenario_id: str, db: Session = Depends(get_db)):
    """Get energy assets (solar+battery) configuration for a scenario."""
    profile = db.query(ScenarioProfile).filter_by(scenario_id=scenario_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    asset = db.query(EnergyAsset).filter_by(scenario_id=scenario_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail=f"No energy asset configuration found for scenario '{scenario_id}'.")
    return asset
