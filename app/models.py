from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from pydantic import EmailStr
from sqlalchemy import Column, ForeignKey

class UserRoleLink(SQLModel, table=True):
    user_id: int = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    role_id: int = Field(
        sa_column=Column(
            ForeignKey("userrole.id", ondelete="CASCADE"),
            primary_key=True
        )
    )

class UserSkillLink(SQLModel, table=True):
    user_id: int = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    skill_id: int = Field(
        sa_column=Column(
            ForeignKey("userskill.id", ondelete="CASCADE"),
            primary_key=True
        )
    )

class UserModuleLink(SQLModel, table=True):
    user_id: int = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    module_id: int = Field(
        sa_column=Column(
            ForeignKey("module.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )

class LocationWarehouseLink(SQLModel, table=True):
    location_id: int = Field(
        sa_column=Column(
            ForeignKey("location.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    warehouse_id: int = Field(
        sa_column=Column(
            ForeignKey("warehouse.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )

class DivisionLaboratoryLink(SQLModel, table=True):
    division_id: int = Field(
        sa_column=Column(
            ForeignKey("division.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    laboratory_id: int = Field(
        sa_column=Column(
            ForeignKey("laboratory.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )

class DivisionWarehouseLink(SQLModel, table=True):
    division_id: int = Field(
        sa_column=Column(
            ForeignKey("division.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    warehouse_id: int = Field(
        sa_column=Column(
            ForeignKey("warehouse.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )

class DivisionEmployeeLink(SQLModel, table=True):
    division_id: int = Field(
        sa_column=Column(
            ForeignKey("division.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    user_id: int = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )

# region User models
class UserType(str, Enum):
    superadmin = "superadmin"
    mp_admin    = "mp_admin"
    regular    = "regular"

class UserShortBase(SQLModel):
    username:    str           = Field(index=True, unique=True)
    name:        str
    surname:     str
    email:       EmailStr       = Field(unique=True)
    usertype:    UserType

class UserImagelessBase(UserShortBase):
    title:       str
    usertype:    UserType
    is_active:   bool           = Field(default=True)

class UserBase(UserImagelessBase):
    profile_image_path: str    = Field(default="default_profile_image.png")
    created_at:  datetime       = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by:  str
    last_modified_at:  datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified_by:  str

class User(UserBase, table=True):
    id:          int | None    = Field(default=None, primary_key=True)
    hashed_pw:   str

    roles: list["UserRole"] = Relationship(
        back_populates="users",
        link_model=UserRoleLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

    skills: list["UserSkill"] = Relationship(
        back_populates="users",
        link_model=UserSkillLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

    modules: list["Module"] = Relationship(
        back_populates="users",
        link_model=UserModuleLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True},
    )

    divisions: list["Division"] = Relationship(
        back_populates="employees",
        link_model=DivisionEmployeeLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True},
    )

class UserCreate(UserImagelessBase):
    pw:   str
    role_ids: list[int] = Field(default_factory=list)
    module_ids: list[int] = Field(default_factory=list)
    skill_ids: list[int] = Field(default_factory=list)

class UserRead(UserImagelessBase):
    id: int
    roles: list["UserRoleBase"] | None = None
    skills: list["UserSkillBase"] | None = None
    modules: list["ModuleShortRead"] | None = None
    divisions: list["DivisionBase"] | None = None

class UserUpdate(SQLModel):
    username:    str           = Field(default=None)
    email:       EmailStr      = Field(default=None)
    name:        str           = Field(default=None)
    surname:     str           = Field(default=None)
    title:       str           = Field(default=None)
    usertype:    UserType      = Field(default=UserType.regular)
    is_active:   bool          = Field(default=None)

    roles: list[int] | None = Field(default=None)
    skills: list[int] | None = Field(default=None)
    modules: list[int] | None = Field(default=None)
#endregion

# region UserRole models
class UserRoleBase(SQLModel):
    rolename: str = Field(index=True, unique=True, nullable=False)
    can_create: bool = Field(default=False)
    can_read: bool = Field(default=False)
    can_update: bool = Field(default=False)
    can_delete: bool = Field(default=False)
    notes: str | None = Field(default=None, max_length=255)

class UserRole(UserRoleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRoleLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleRead(UserRoleBase):
    id: int
    users: list["UserShortBase"] | None = None

class UserRoleUpdate(UserRoleBase):
    rolename: str | None= Field(default=None)
    can_create: bool | None= Field(default=None)
    can_read: bool | None= Field(default=None)
    can_update: bool | None = Field(default=None)
    can_delete: bool | None = Field(default=None)
    notes: str | None = Field(default=None, max_length=255)

#endregion

# region UserSkill models
class UserSkillBase(SQLModel):
    skillname: str = Field(index=True, unique=True, nullable=False)
    skill_level: int = Field(default=0)
    notes: str | None = Field(default=None, max_length=255)

class UserSkill(UserSkillBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    users: list["User"] = Relationship(
        back_populates="skills",
        link_model=UserSkillLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

class UserSkillCreate(UserSkillBase):
    pass

class UserSkillRead(UserSkillBase):
    id: int
    users: list["UserShortBase"] | None = None

class UserSkillUpdate(UserSkillBase):
    skillname: str | None = Field(default=None)
    skill_level: int | None = Field(default=None)
    notes: str | None = Field(default=None, max_length=255)
    
#endregion

# region Module models
class ModuleBase(SQLModel):
    title: str
    description: str

class Module(ModuleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    linkname: str
    image_url: str

    users: list["User"] = Relationship(
        back_populates="modules",
        link_model=UserModuleLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True},
    )

class ModuleShortRead(ModuleBase):
    id: int

class ModuleRead(ModuleBase):
    id: int
    users: list["UserShortBase"] | None = None
# endregion

# region Division models
class DivisionBase(SQLModel):
    code: str = Field(index=True, unique=True, nullable=False)
    name: str = Field(index=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)

class Division(DivisionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    laboratories: list["Laboratory"] = Relationship(
        back_populates="divisions",
        link_model=DivisionLaboratoryLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

    warehouses: list["Warehouse"] = Relationship(
        back_populates="divisions",
        link_model=DivisionWarehouseLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

    employees: list["User"] = Relationship(
        back_populates="divisions",
        link_model=DivisionEmployeeLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )
class DivisionCreate(DivisionBase):
    laboratory_codes: list[str] = Field(default_factory=list)
    warehouse_codes: list[str] = Field(default_factory=list)
    employee_usernames: list[str] = Field(default_factory=list)

class DivisionRead(DivisionBase):
    id: int
    laboratories: list["Laboratory"] | None = None
    warehouses: list["Warehouse"] | None = None
    employees: list["UserShortBase"] | None = None

class DivisionUpdate(DivisionBase):
    code: str | None = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=255)
    laboratory_codes: list[str] | None = Field(default=None)
    warehouse_codes: list[str] | None = Field(default=None)
    employee_usernames: list[str] | None = Field(default=None)

# endregion

# region Location models
class LocationBase(SQLModel):
    code: str = Field(index=True, unique=True, nullable=False)
    name: str = Field(index=True, nullable=False)
    adress: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class Location(LocationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    warehouses: list["Warehouse"] = Relationship(
        back_populates="locations",
        link_model=LocationWarehouseLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

class LocationCreate(LocationBase):
    pass

class LocationRead(LocationBase):
    id: int
    warehouses: list["WarehouseBase"] | None = None

class LocationUpdate(LocationBase):
    code: str | None = Field(default=None)
    name: str | None = Field(default=None)
    adress: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)
# endregion

# region Warehouse models
class WarehouseBase(SQLModel):
    code: str = Field(index=True, nullable=False)
    name: str = Field(index=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)

class Warehouse(WarehouseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    locations: list["Location"] = Relationship(
        back_populates="warehouses",
        link_model=LocationWarehouseLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

    divisions: list["Division"] = Relationship(
        back_populates="warehouses",
        link_model=DivisionWarehouseLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

class WarehouseCreate(WarehouseBase):
    location_codes: list[str] = Field(default_factory=list)
    division_codes: list[str] = Field(default_factory=list)

class WarehouseRead(WarehouseBase):
    id: int
    locations: list["Location"] | None = None
    divisions: list["Division"] | None = None

class WarehouseUpdate(WarehouseBase):
    code: str | None = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=255)
    location_codes: list[str] | None = Field(default=None)
    division_codes: list[str] | None = Field(default=None)

# endregion

# region Laboratory models
class LaboratoryBase(SQLModel):
    code: str = Field(index=True, nullable=False)
    name: str = Field(index=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)

class Laboratory(LaboratoryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    divisions: list["Division"] = Relationship(
        back_populates="laboratories",
        link_model=DivisionLaboratoryLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )

class LaboratoryCreate(LaboratoryBase):
    division_codes: list[str] = Field(default_factory=list)

class LaboratoryRead(LaboratoryBase):
    id: int
    divisions: list["Division"] | None = None

class LaboratoryUpdate(LaboratoryBase):
    code: str | None = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=255)
    division_codes: list[str] | None = Field(default=None)

# endregion
