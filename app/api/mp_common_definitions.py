from typing import Annotated

from fastapi import ( 
    APIRouter, Response, Request, Depends, status, HTTPException
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_session
# Import the new CRUD functions
from app.crud.mp_common_definitions import *
# Import all necessary models
from app.models import *
from app.dependencies.auth import get_current_active_user

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Dependencies for this router
# NOTE: Using get_current_active_user makes these endpoints accessible to any logged-in user.
# If you need stricter permissions (e.g., only admins), you might want a different dependency.
UserDep = Annotated[User, Depends(get_current_active_user)]
SessionDep = Annotated[Session, Depends(get_session)]

mp_common_definitions_router = APIRouter(
    prefix="/mp_common_definitions",
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
    tags=['M&P Common Definitions']
)

@mp_common_definitions_router.get("/", name='mp_common_definitions_index', include_in_schema=False, response_class=HTMLResponse)
async def mp_common_definitions_index(request: Request, current_user: UserDep):
    """
    Main HTML page for the Common Definitions module.
    """
    return templates.TemplateResponse("mp_common_definitions.html", {
        "request": request,
        "user": current_user,
    })

# region Location operations
@mp_common_definitions_router.get("/locations/", name='get_all_locations', response_model=list[LocationRead])
def get_all_locations(current_user: UserDep, db: SessionDep):
    return read_all_locations(db)

@mp_common_definitions_router.get("/locations/{location_id}", response_model=LocationRead)
def get_location_by_id(current_user: UserDep, location_id: int, db: SessionDep):
    location = read_location(db, location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location

@mp_common_definitions_router.post("/locations/", name='create_new_location', response_model=Location, status_code=status.HTTP_201_CREATED)
def create_new_location(current_user: UserDep, location_create: LocationCreate, db: SessionDep):
    return create_location(db=db, location_create=location_create)

@mp_common_definitions_router.put("/locations/{location_id}",name='update_existing_location', response_model=Location)
def update_existing_location(current_user: UserDep, location_id: int, location_update: LocationUpdate, db: SessionDep):
    db_location = read_location(db, location_id)
    if not db_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return update_location(db=db, db_location=db_location, input_location=location_update)

@mp_common_definitions_router.delete("/locations/{location_id}",name='delete_location_by_id', status_code=status.HTTP_204_NO_CONTENT)
def delete_location_by_id(current_user: UserDep, location_id: int, db: SessionDep):
    if not delete_location(db, location_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
# endregion

# region Warehouse operations
@mp_common_definitions_router.get("/warehouses/", name='get_all_warehouses', response_model=list[WarehouseRead])
def get_all_warehouses(current_user: UserDep, db: SessionDep):
    return read_all_warehouses(db)

@mp_common_definitions_router.get("/warehouses/{warehouse_id}", response_model=WarehouseRead)
def get_warehouse_by_id(current_user: UserDep, warehouse_id: int, db: SessionDep):
    warehouse = read_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return warehouse

@mp_common_definitions_router.post("/warehouses/", name='create_new_warehouse', response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
def create_new_warehouse(current_user: UserDep, warehouse_create: WarehouseCreate, db: SessionDep):
    return create_warehouse(db=db, warehouse_create=warehouse_create)

@mp_common_definitions_router.put("/warehouses/{warehouse_id}", response_model=WarehouseRead)
def update_existing_warehouse(current_user: UserDep, warehouse_id: int, warehouse_update: WarehouseUpdate, db: SessionDep):
    db_warehouse = read_warehouse(db, warehouse_id)
    if not db_warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return update_warehouse(db=db, db_warehouse=db_warehouse, input_warehouse=warehouse_update)

@mp_common_definitions_router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse_by_id(current_user: UserDep, warehouse_id: int, db: SessionDep):
    if not delete_warehouse(db, warehouse_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
# endregion

# region Laboratory operations
@mp_common_definitions_router.get("/laboratories/", name='get_all_laboratories', response_model=list[LaboratoryRead])
def get_all_laboratories(current_user: UserDep, db: SessionDep):
    return read_all_laboratories(db)

@mp_common_definitions_router.get("/laboratories/{laboratory_id}", response_model=LaboratoryRead)
def get_laboratory_by_id(current_user: UserDep, laboratory_id: int, db: SessionDep):
    laboratory = read_laboratory(db, laboratory_id)
    if not laboratory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Laboratory not found")
    return laboratory

@mp_common_definitions_router.post("/laboratories/", response_model=LaboratoryRead, status_code=status.HTTP_201_CREATED)
def create_new_laboratory(current_user: UserDep, laboratory_create: LaboratoryCreate, db: SessionDep):
    return create_laboratory(db=db, laboratory_create=laboratory_create)

@mp_common_definitions_router.put("/laboratories/{laboratory_id}", response_model=LaboratoryRead)
def update_existing_laboratory(current_user: UserDep, laboratory_id: int, laboratory_update: LaboratoryUpdate, db: SessionDep):
    db_laboratory = read_laboratory(db, laboratory_id)
    if not db_laboratory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Laboratory not found")
    return update_laboratory(db=db, db_laboratory=db_laboratory, input_laboratory=laboratory_update)

@mp_common_definitions_router.delete("/laboratories/{laboratory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_laboratory_by_id(current_user: UserDep, laboratory_id: int, db: SessionDep):
    if not delete_laboratory(db, laboratory_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Laboratory not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
# endregion

# region Division operations
@mp_common_definitions_router.get("/divisions/", name='get_all_divisions', response_model=list[DivisionRead])
def get_all_divisions(current_user: UserDep, db: SessionDep):
    return read_all_divisions(db)

@mp_common_definitions_router.get("/divisions/{division_id}", response_model=DivisionRead)
def get_division_by_id(current_user: UserDep, division_id: int, db: SessionDep):
    division = read_division(db, division_id)
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")
    return division

@mp_common_definitions_router.post("/divisions/", response_model=DivisionRead, status_code=status.HTTP_201_CREATED)
def create_new_division(current_user: UserDep, division_create: DivisionCreate, db: SessionDep):
    return create_division(db=db, division_create=division_create)

@mp_common_definitions_router.put("/divisions/{division_id}", response_model=DivisionRead)
def update_existing_division(current_user: UserDep, division_id: int, division_update: DivisionUpdate, db: SessionDep):
    db_division = read_division(db, division_id)
    if not db_division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")
    return update_division(db=db, db_division=db_division, input_division=division_update)

@mp_common_definitions_router.delete("/divisions/{division_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_division_by_id(current_user: UserDep, division_id: int, db: SessionDep):
    if not delete_division(db, division_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Division not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
# endregion