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

class UserCreate(UserImagelessBase):
    pw:   str
    role_ids: list[int] = Field(default_factory=list)
    module_ids: list[int] = Field(default_factory=list)
    skill_ids: list[int] = Field(default_factory=list)

class UserRead(UserImagelessBase):
    id: int
    roles: list["UserRole"] | None = None
    skills: list["UserSkill"] | None = None
    modules: list["ModuleShortRead"] | None = None

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

