from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import (
    # Location Models
    Location, LocationCreate, LocationRead, LocationUpdate,
    # Warehouse Models
    Warehouse, WarehouseCreate, WarehouseRead, WarehouseUpdate,
    # Laboratory Models
    Laboratory, LaboratoryCreate, LaboratoryRead, LaboratoryUpdate,
    # Division Models
    Division, DivisionCreate, DivisionRead, DivisionUpdate,
    # User Model for relationship linking
    User
)

# region Location CRUD
def read_location(db: Session, location_id: int) -> LocationRead | None:
    """Fetches a single location by its ID, eager-loading its warehouses."""
    statement = select(Location).options(selectinload(Location.warehouses)).where(Location.id == location_id)
    return db.exec(statement).first()

def read_all_locations(db: Session) -> list[LocationRead]:
    """Fetches all locations, eager-loading their associated warehouses."""
    statement = select(Location).options(selectinload(Location.warehouses))
    return db.exec(statement).all()

def create_location(*, db: Session, location_create: LocationCreate) -> Location:
    """Creates a new Location, ensuring the location code is unique."""
    if db.exec(select(Location).where(Location.code == location_create.code)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Location with code '{location_create.code}' already exists",
        )
    
    location = Location.model_validate(location_create)
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

def update_location(*, db: Session, db_location: Location, input_location: LocationUpdate) -> Location:
    """Updates a location, ensuring the new code is unique if changed."""
    if input_location.code and input_location.code != db_location.code:
        if db.exec(select(Location).where(Location.code == input_location.code)).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Location with code '{input_location.code}' already exists",
            )
            
    location_data = input_location.model_dump(exclude_unset=True)
    db_location.sqlmodel_update(location_data)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def delete_location(db: Session, location_id: int) -> bool:
    """Deletes a location. Returns True on success, False if not found."""
    location = db.get(Location, location_id)
    if not location:
        return False
    db.delete(location)
    db.commit()
    return True
# endregion

# region Warehouse CRUD
def read_warehouse(db: Session, warehouse_id: int) -> WarehouseRead | None:
    """Fetches a single warehouse, eager-loading its locations and divisions."""
    statement = (
        select(Warehouse)
        .options(selectinload(Warehouse.locations), selectinload(Warehouse.divisions))
        .where(Warehouse.id == warehouse_id)
    )
    return db.exec(statement).first()

def read_all_warehouses(db: Session) -> list[WarehouseRead]:
    """Fetches all warehouses, eager-loading their locations and divisions."""
    statement = select(Warehouse).options(selectinload(Warehouse.locations), selectinload(Warehouse.divisions))
    return db.exec(statement).all()

def create_warehouse(*, db: Session, warehouse_create: WarehouseCreate) -> Warehouse:
    """Creates a warehouse, linking it to locations and divisions by their codes."""
    if db.exec(select(Warehouse).where(Warehouse.code == warehouse_create.code)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Warehouse with code '{warehouse_create.code}' already exists",
        )
    
    warehouse_data = warehouse_create.model_dump(exclude={"location_codes", "division_codes"})
    db_warehouse = Warehouse.model_validate(warehouse_data)

    # Link Locations
    if warehouse_create.location_codes:
        locations = db.exec(select(Location).where(Location.code.in_(warehouse_create.location_codes))).all()
        if len(locations) != len(set(warehouse_create.location_codes)):
            missing = set(warehouse_create.location_codes) - {loc.code for loc in locations}
            raise HTTPException(status_code=404, detail=f"Locations not found: {missing}")
        db_warehouse.locations = locations

    # Link Divisions
    if warehouse_create.division_codes:
        divisions = db.exec(select(Division).where(Division.code.in_(warehouse_create.division_codes))).all()
        if len(divisions) != len(set(warehouse_create.division_codes)):
            missing = set(warehouse_create.division_codes) - {div.code for div in divisions}
            raise HTTPException(status_code=404, detail=f"Divisions not found: {missing}")
        db_warehouse.divisions = divisions

    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

def update_warehouse(*, db: Session, db_warehouse: Warehouse, input_warehouse: WarehouseUpdate) -> Warehouse:
    """Updates a warehouse, including its scalar fields and relationships to locations and divisions."""
    if input_warehouse.code and input_warehouse.code != db_warehouse.code:
        if db.exec(select(Warehouse).where(Warehouse.code == input_warehouse.code)).first():
            raise HTTPException(status_code=400, detail=f"Warehouse code '{input_warehouse.code}' already exists")
    
    # Update scalar fields
    warehouse_data = input_warehouse.model_dump(exclude_unset=True, exclude={"location_codes", "division_codes"})
    db_warehouse.sqlmodel_update(warehouse_data)

    # Update relationships if provided (None means leave unchanged)
    if input_warehouse.location_codes is not None:
        locations = db.exec(select(Location).where(Location.code.in_(input_warehouse.location_codes))).all()
        if len(locations) != len(set(input_warehouse.location_codes)):
            missing = set(input_warehouse.location_codes) - {loc.code for loc in locations}
            raise HTTPException(status_code=404, detail=f"Locations not found: {missing}")
        db_warehouse.locations = locations

    if input_warehouse.division_codes is not None:
        divisions = db.exec(select(Division).where(Division.code.in_(input_warehouse.division_codes))).all()
        if len(divisions) != len(set(input_warehouse.division_codes)):
            missing = set(input_warehouse.division_codes) - {div.code for div in divisions}
            raise HTTPException(status_code=404, detail=f"Divisions not found: {missing}")
        db_warehouse.divisions = divisions
    
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

def delete_warehouse(db: Session, warehouse_id: int) -> bool:
    """Deletes a warehouse. Returns True on success, False if not found."""
    warehouse = db.get(Warehouse, warehouse_id)
    if not warehouse:
        return False
    db.delete(warehouse)
    db.commit()
    return True
# endregion

# region Laboratory CRUD
def read_laboratory(db: Session, laboratory_id: int) -> LaboratoryRead | None:
    """Fetches a single laboratory, eager-loading its associated divisions."""
    statement = (
        select(Laboratory)
        .options(selectinload(Laboratory.divisions))
        .where(Laboratory.id == laboratory_id)
    )
    return db.exec(statement).first()

def read_all_laboratories(db: Session) -> list[LaboratoryRead]:
    """Fetches all laboratories, eager-loading their associated divisions."""
    statement = select(Laboratory).options(selectinload(Laboratory.divisions))
    return db.exec(statement).all()

def create_laboratory(*, db: Session, laboratory_create: LaboratoryCreate) -> Laboratory:
    """Creates a laboratory, linking it to divisions by their codes."""
    if db.exec(select(Laboratory).where(Laboratory.code == laboratory_create.code)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Laboratory with code '{laboratory_create.code}' already exists",
        )
    
    laboratory_data = laboratory_create.model_dump(exclude={"division_codes"})
    db_laboratory = Laboratory.model_validate(laboratory_data)

    # Link Divisions
    if laboratory_create.division_codes:
        divisions = db.exec(select(Division).where(Division.code.in_(laboratory_create.division_codes))).all()
        if len(divisions) != len(set(laboratory_create.division_codes)):
            missing = set(laboratory_create.division_codes) - {div.code for div in divisions}
            raise HTTPException(status_code=404, detail=f"Divisions not found: {missing}")
        db_laboratory.divisions = divisions

    db.add(db_laboratory)
    db.commit()
    db.refresh(db_laboratory)
    return db_laboratory

def update_laboratory(*, db: Session, db_laboratory: Laboratory, input_laboratory: LaboratoryUpdate) -> Laboratory:
    """Updates a laboratory, including its scalar fields and relationships to divisions."""
    if input_laboratory.code and input_laboratory.code != db_laboratory.code:
        if db.exec(select(Laboratory).where(Laboratory.code == input_laboratory.code)).first():
            raise HTTPException(status_code=400, detail=f"Laboratory code '{input_laboratory.code}' already exists")

    laboratory_data = input_laboratory.model_dump(exclude_unset=True, exclude={"division_codes"})
    db_laboratory.sqlmodel_update(laboratory_data)

    if input_laboratory.division_codes is not None:
        divisions = db.exec(select(Division).where(Division.code.in_(input_laboratory.division_codes))).all()
        if len(divisions) != len(set(input_laboratory.division_codes)):
            missing = set(input_laboratory.division_codes) - {div.code for div in divisions}
            raise HTTPException(status_code=404, detail=f"Divisions not found: {missing}")
        db_laboratory.divisions = divisions
        
    db.add(db_laboratory)
    db.commit()
    db.refresh(db_laboratory)
    return db_laboratory

def delete_laboratory(db: Session, laboratory_id: int) -> bool:
    """Deletes a laboratory. Returns True on success, False if not found."""
    laboratory = db.get(Laboratory, laboratory_id)
    if not laboratory:
        return False
    db.delete(laboratory)
    db.commit()
    return True
# endregion

# region Division CRUD
def read_division(db: Session, division_id: int) -> DivisionRead | None:
    """Fetches a single division, eager-loading all its relationships."""
    statement = (
        select(Division)
        .options(
            selectinload(Division.laboratories),
            selectinload(Division.warehouses),
            selectinload(Division.employees)
        )
        .where(Division.id == division_id)
    )
    return db.exec(statement).first()

def read_all_divisions(db: Session) -> list[DivisionRead]:
    """Fetches all divisions, eager-loading all their relationships."""
    statement = select(Division).options(
        selectinload(Division.laboratories),
        selectinload(Division.warehouses),
        selectinload(Division.employees)
    )
    return db.exec(statement).all()

def create_division(*, db: Session, division_create: DivisionCreate) -> Division:
    """Creates a division, linking it to laboratories, warehouses, and employees."""
    if db.exec(select(Division).where(Division.code == division_create.code)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Division with code '{division_create.code}' already exists",
        )
    
    division_data = division_create.model_dump(exclude={"laboratory_codes", "warehouse_codes", "employee_usernames"})
    db_division = Division.model_validate(division_data)

    # Link relationships
    if division_create.laboratory_codes:
        labs = db.exec(select(Laboratory).where(Laboratory.code.in_(division_create.laboratory_codes))).all()
        if len(labs) != len(set(division_create.laboratory_codes)):
            raise HTTPException(status_code=404, detail="One or more laboratories not found")
        db_division.laboratories = labs
    
    if division_create.warehouse_codes:
        warehouses = db.exec(select(Warehouse).where(Warehouse.code.in_(division_create.warehouse_codes))).all()
        if len(warehouses) != len(set(division_create.warehouse_codes)):
            raise HTTPException(status_code=404, detail="One or more warehouses not found")
        db_division.warehouses = warehouses

    if division_create.employee_usernames:
        employees = db.exec(select(User).where(User.username.in_(division_create.employee_usernames))).all()
        if len(employees) != len(set(division_create.employee_usernames)):
            raise HTTPException(status_code=404, detail="One or more employees not found")
        db_division.employees = employees
    
    db.add(db_division)
    db.commit()
    db.refresh(db_division)
    return db_division

def update_division(*, db: Session, db_division: Division, input_division: DivisionUpdate) -> Division:
    """Updates a division, including its relationships."""
    if input_division.code and input_division.code != db_division.code:
        if db.exec(select(Division).where(Division.code == input_division.code)).first():
            raise HTTPException(status_code=400, detail=f"Division code '{input_division.code}' already exists")

    division_data = input_division.model_dump(exclude_unset=True, exclude={"laboratory_codes", "warehouse_codes", "employee_usernames"})
    db_division.sqlmodel_update(division_data)

    # Update relationships if provided
    if input_division.laboratory_codes is not None:
        labs = db.exec(select(Laboratory).where(Laboratory.code.in_(input_division.laboratory_codes))).all()
        if len(labs) != len(set(input_division.laboratory_codes)):
            raise HTTPException(status_code=404, detail="One or more laboratories not found")
        db_division.laboratories = labs

    if input_division.warehouse_codes is not None:
        warehouses = db.exec(select(Warehouse).where(Warehouse.code.in_(input_division.warehouse_codes))).all()
        if len(warehouses) != len(set(input_division.warehouse_codes)):
            raise HTTPException(status_code=404, detail="One or more warehouses not found")
        db_division.warehouses = warehouses

    if input_division.employee_usernames is not None:
        employees = db.exec(select(User).where(User.username.in_(input_division.employee_usernames))).all()
        if len(employees) != len(set(input_division.employee_usernames)):
            raise HTTPException(status_code=404, detail="One or more employees not found")
        db_division.employees = employees

    db.add(db_division)
    db.commit()
    db.refresh(db_division)
    return db_division

def delete_division(db: Session, division_id: int) -> bool:
    """Deletes a division. Returns True on success, False if not found."""
    division = db.get(Division, division_id)
    if not division:
        return False
    db.delete(division)
    db.commit()
    return True
# endregion