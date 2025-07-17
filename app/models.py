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

class DivisionUserLink(SQLModel, table=True):
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
        back_populates="users",
        link_model=DivisionUserLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True},
    )

class UserCreate(UserImagelessBase):
    pw:   str
    roles: list[int] = Field(default_factory=list, description="List of role IDs to assign to the user")
    modules: list[int] = Field(default_factory=list, description="List of module IDs to assign to the user")
    skills: list[int] = Field(default_factory=list, description="List of skill IDs to assign to the user")

class UserRead(UserImagelessBase):
    id: int
    roles: list["UserRoleShortRead"] | None = None
    skills: list["UserSkillShortRead"] | None = None
    modules: list["ModuleShortRead"] | None = None
    divisions: list["DivisionShortRead"] | None = None

class UserShortRead(UserShortBase):
    id: int

class UserUpdate(SQLModel):
    username:    str           = Field(default=None)
    email:       EmailStr      = Field(default=None)
    name:        str           = Field(default=None)
    surname:     str           = Field(default=None)
    title:       str           = Field(default=None)
    usertype:    UserType      = Field(default=UserType.regular)
    is_active:   bool          = Field(default=None)

    roles: list[int] | None = Field(default=None, description="List of role IDs to assign to the user")
    modules: list[int] | None = Field(default=None, description="List of module IDs to assign to the user")
    skills: list[int] | None = Field(default=None, description="List of skill IDs to assign to the user")
    
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
    users: list["UserShortRead"] | None = None

class UserRoleShortRead(UserRoleBase):
    id: int

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
    users: list["UserShortRead"] | None = None

class UserSkillShortRead(UserSkillBase):
    id: int

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
    users: list["UserShortRead"] | None = None
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

    users: list["User"] = Relationship(
        back_populates="divisions",
        link_model=DivisionUserLink,
        sa_relationship_kwargs={"cascade": "all", "passive_deletes": True}
    )
class DivisionCreate(DivisionBase):
    laboratories: list[str] = Field(default_factory=list, description="List of laboratory codes to assign to the division")
    warehouses: list[str] = Field(default_factory=list, description="List of warehouse codes to assign to the division")
    users: list[str] = Field(default_factory=list, description="List of employee usernames to assign to the division")

class DivisionRead(DivisionBase):
    id: int
    laboratories: list["LaboratoryShortRead"] | None = None
    warehouses: list["WarehouseShortRead"] | None = None
    users: list["UserShortRead"] | None = None

class DivisionShortRead(DivisionBase):
    id: int

class DivisionUpdate(DivisionBase):
    code: str | None = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=255)
    laboratories: list[str] | None = Field(default=None, description="List of laboratory codes to assign to the division")
    warehouses: list[str] | None = Field(default=None, description="List of warehouse codes to assign to the division")
    users: list[str] | None = Field(default=None, description="List of employee usernames to assign to the division")

# endregion

# region Location models
class LocationBase(SQLModel):
    code: str = Field(index=True, unique=True, nullable=False)
    name: str = Field(index=True, nullable=False)
    address: str | None = Field(default=None, max_length=255)
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
    warehouses: list["WarehouseShortRead"] | None = None

class LocationShortRead(LocationBase):
    id: int

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
    locations: list[str] = Field(default_factory=list, description="List of location codes to assign to the warehouse")
    divisions: list[str] = Field(default_factory=list, description="List of division codes to assign to the warehouse")

class WarehouseRead(WarehouseBase):
    id: int
    locations: list["LocationShortRead"] | None = None
    divisions: list["DivisionShortRead"] | None = None

class WarehouseShortRead(WarehouseBase):
    id: int

class WarehouseUpdate(WarehouseBase):
    code: str | None = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=255)
    locations: list[str] | None = Field(default=None, description="List of location codes to assign to the warehouse")
    divisions: list[str] | None = Field(default=None, description="List of division codes to assign to the warehouse")

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
    divisions: list[str] = Field(default_factory=list, description="List of division codes to assign to the laboratory")

class LaboratoryRead(LaboratoryBase):
    id: int
    divisions: list["DivisionShortRead"] | None = None

class LaboratoryShortRead(LaboratoryBase):
    id: int

class LaboratoryUpdate(LaboratoryBase):
    code: str | None = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=255)
    divisions: list[str] | None = Field(default=None, description="List of division codes to assign to the laboratory")

# endregion
