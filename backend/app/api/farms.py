from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# In-memory storage for MVP (replace with Supabase later)
farms_db = []


class FarmBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    region: str = Field(..., min_length=1, max_length=100)
    country: str = Field(default="France", max_length=50)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    area_hectares: float = Field(..., gt=0)
    crop_type: Optional[str] = Field(default=None, max_length=50)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    soil_ph: Optional[float] = Field(default=None, ge=3, le=10)
    geometry: Optional[dict] = None  # GeoJSON polygon


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    region: Optional[str] = Field(default=None, min_length=1, max_length=100)
    country: Optional[str] = Field(default=None, max_length=50)
    area_hectares: Optional[float] = Field(default=None, gt=0)
    crop_type: Optional[str] = Field(default=None, max_length=50)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    soil_ph: Optional[float] = Field(default=None, ge=3, le=10)
    geometry: Optional[dict] = None


class FarmResponse(FarmBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_analysis_at: Optional[datetime] = None
    status: str = "active"
    alerts_count: int = 0

    class Config:
        from_attributes = True


class FarmListResponse(BaseModel):
    farms: List[FarmResponse]
    total: int


@router.post("", response_model=FarmResponse, status_code=201)
async def create_farm(farm: FarmCreate):
    new_farm = FarmResponse(
        id=str(uuid4()),
        **farm.model_dump(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    farms_db.append(new_farm)
    return new_farm


@router.get("", response_model=FarmListResponse)
async def list_farms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
):
    filtered = farms_db
    if search:
        search_lower = search.lower()
        filtered = [f for f in filtered if search_lower in f.name.lower() or search_lower in f.region.lower()]
    if status:
        filtered = [f for f in filtered if f.status == status]

    total = len(filtered)
    farms = filtered[skip:skip + limit]
    return FarmListResponse(farms=farms, total=total)


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: str):
    farm = next((f for f in farms_db if f.id == farm_id), None)
    if not farm:
        raise HTTPException(status_code=404, detail="Exploitation non trouvée")
    return farm


@router.patch("/{farm_id}", response_model=FarmResponse)
async def update_farm(farm_id: str, farm_update: FarmUpdate):
    farm = next((f for f in farms_db if f.id == farm_id), None)
    if not farm:
        raise HTTPException(status_code=404, detail="Exploitation non trouvée")

    update_data = farm_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    farm.updated_at = datetime.utcnow()
    return farm


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(farm_id: str):
    global farms_db
    farm = next((f for f in farms_db if f.id == farm_id), None)
    if not farm:
        raise HTTPException(status_code=404, detail="Exploitation non trouvée")
    farms_db = [f for f in farms_db if f.id != farm_id]