from sqlmodel import Session, select
from datetime import datetime, timezone
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models import (
    UserRole, UserRoleCreate, UserRoleUpdate, UserRoleRead,
    UserSkill, UserSkillCreate, UserSkillUpdate, UserSkillRead,
    User, UserCreate, UserType, UserUpdate, UserRead,
    Module, ModuleRead)

from app.dependencies.auth import get_password_hash


# region userrole crud
def read_role(db: Session, role_id: int) -> UserRoleRead | None:
    statement = select(UserRole).options(selectinload(UserRole.users)).where(UserRole.id == role_id)
    return db.exec(statement).first()

def read_all_roles(db: Session) -> list[UserRoleRead]:
    statement = select(UserRole).options(selectinload(UserRole.users))
    return db.exec(statement).all()

def create_role(*, db: Session, role_create: UserRoleCreate) -> UserRole:
    if db.exec(select(UserRole).where(UserRole.rolename == role_create.rolename)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_create.rolename}' already exists",
        )
    role = UserRole.model_validate(role_create)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def update_role(*, db: Session, db_role: UserRole, input_role: UserRoleUpdate) -> UserRole:
    if input_role.rolename and input_role.rolename != db_role.rolename:
        if db.exec(
            select(UserRole).where(UserRole.rolename == input_role.rolename)
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{input_role.rolename}' already exists",
            )
    role_data = input_role.model_dump(exclude_unset=True)
    db_role.sqlmodel_update(role_data)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int) -> bool:
    role = db.get(UserRole, role_id)
    if not role:
        return False
    db.delete(role)
    db.commit()
    return True
#endregion

# region userskill crud
def read_skill(db: Session, skill_id: int) -> UserSkillRead | None:
    statement = (
        select(UserSkill)
        .options(selectinload(UserSkill.users))
        .where(UserSkill.id == skill_id)
    )
    return db.exec(statement).first()

def read_all_skills(db: Session) -> list[UserSkillRead]:
    statement = select(UserSkill).options(selectinload(UserSkill.users))
    return db.exec(statement).all()

def create_skill(*, db: Session, skill_create: UserSkillCreate) -> UserSkill:
    """
    Insert a new UserSkill, guarding against duplicate skill names.
    """
    if db.exec(select(UserSkill).where(UserSkill.skillname == skill_create.skillname)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill '{skill_create.skillname}' already exists",
        )

    skill = UserSkill.model_validate(skill_create)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

def update_skill(
    *,
    db: Session,
    db_skill: UserSkill,
    input_skill: UserSkillUpdate
) -> UserSkill:

    # Uniqueness guard if skillname is changing
    if input_skill.skillname and input_skill.skillname != db_skill.skillname:
        if db.exec(
            select(UserSkill).where(UserSkill.skillname == input_skill.skillname)
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Skill '{input_skill.skillname}' already exists",
            )

    # Scalar updates
    skill_data = input_skill.model_dump(exclude_unset=True)
    db_skill.sqlmodel_update(skill_data)

    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

def delete_skill(db: Session, skill_id: int) -> bool:

    skill = db.get(UserSkill, skill_id)
    if not skill:
        return False

    db.delete(skill)          # link rows removed via ON DELETE CASCADE
    db.commit()
    return True

#endregion

# region user crud
def read_user(db: Session, username: str) -> UserRead | None:
    statement = select(User).options(
        selectinload(User.roles), 
        selectinload(User.modules),
        selectinload(User.skills)).where(User.username == username)
    return db.exec(statement).first()

def read_all_users(db: Session) -> list[UserRead]:
    statement = select(User).options(
        selectinload(User.roles), 
        selectinload(User.modules),
        selectinload(User.skills))
    return db.exec(statement).all()

def create_user(*, db: Session, user_create: UserCreate, created_by:str) -> User:
    # Check for existing username/email
    if db.exec(select(User).where(
        (User.username == user_create.username) |
        (User.email == user_create.email)
    )).first():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Create user object
    user_data = user_create.model_dump(exclude={"pw", "role_ids", "module_ids", "skill_ids"})
    hashed_pw = get_password_hash(user_create.pw)
    db_user = User(**user_data, hashed_pw=hashed_pw, created_by=created_by, last_modified_by=created_by)
    db.add(db_user)
    db.flush()
    
    # Super‑admin gets *all* existing modules (ignores module_ids)
    if user_create.usertype == UserType.superadmin:
        db_user.modules = db.exec(select(Module)).all()
    elif user_create.module_ids:
        modules = db.exec(select(Module).where(Module.id.in_(user_create.module_ids))).all()
        if len(modules) != len(set(user_create.module_ids)):
            missing = set(user_create.module_ids) - {m.id for m in modules}
            raise HTTPException(status_code=404, detail=f"Modules not found: {missing}")
        db_user.modules = modules

    if user_create.role_ids:
        roles = db.exec(select(UserRole).where(UserRole.id.in_(user_create.role_ids))).all()
        if len(roles) != len(set(user_create.role_ids)):
            missing = set(user_create.role_ids) - {r.id for r in roles}
            raise HTTPException(status_code=404, detail=f"Roles not found: {missing}")
        db_user.roles = roles

    if user_create.skill_ids:
        skills = db.exec(select(UserSkill).where(UserSkill.id.in_(user_create.skill_ids))).all()
        if len(skills) != len(set(user_create.skill_ids)):
            missing = set(user_create.skill_ids) - {r.id for r in skills}
            raise HTTPException(status_code=404, detail=f"Skills not found: {missing}")
        db_user.skills = skills

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(*, db: Session, db_user: User, user_update: UserUpdate, updated_by:str) -> User:
    """
    Partially update a user (PATCH‑style).

    • Checks for duplicate username / email when changed  
    • Updates scalar fields via `sqlmodel_update`  
    • Re‑links roles / modules if they are provided  
    • If the resulting usertype is `superadmin`, links **all** modules
    """
    if user_update.username and user_update.username != db_user.username:
        if db.exec(select(User).where(User.username == user_update.username)).first():
            raise HTTPException(status_code=400, detail="Username already exists")
    if user_update.email and user_update.email != db_user.email:
        if db.exec(select(User).where(User.email == user_update.email)).first():
            raise HTTPException(status_code=400, detail="Email already exists")

    data = user_update.model_dump(exclude_unset=True, exclude={"roles", "modules", "skills"})
    data["last_modified_at"] = datetime.now(timezone.utc)
    data["last_modified_by"] = updated_by
    db_user.sqlmodel_update(data)

    # Determine the *new* usertype (may have been updated above)
    new_usertype = data.get("usertype", db_user.usertype)

    if user_update.roles is not None:   # None ➜ leave unchanged
        role_ids = [r.id if isinstance(r, UserRole) else r for r in user_update.roles]
        roles = db.exec(select(UserRole).where(UserRole.id.in_(role_ids))).all()
        if len(roles) != len(set(role_ids)):
            missing = set(role_ids) - {r.id for r in roles}
            raise HTTPException(status_code=404, detail=f"Roles not found: {missing}")
        db_user.roles = roles

    if user_update.skills is not None:   # None ➜ leave unchanged
        skill_ids = [r.id if isinstance(r, UserSkill) else r for r in user_update.skills]
        skills = db.exec(select(UserSkill).where(UserSkill.id.in_(skill_ids))).all()
        if len(skills) != len(set(skill_ids)):
            missing = set(skill_ids) - {r.id for r in skills}
            raise HTTPException(status_code=404, detail=f"Skills not found: {missing}")
        db_user.skills = skills

    if new_usertype == UserType.superadmin:
        # Super‑admin always owns every module, ignoring payload
        db_user.modules = db.exec(select(Module)).all()
    elif user_update.modules is not None:                # None ➜ leave unchanged
        module_ids = [m.id if isinstance(m, Module) else m for m in user_update.modules]
        modules = db.exec(select(Module).where(Module.id.in_(module_ids))).all()
        if len(modules) != len(set(module_ids)):
            missing = set(module_ids) - {m.id for m in modules}
            raise HTTPException(status_code=404, detail=f"Modules not found: {missing}")
        db_user.modules = modules

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(*, db: Session, username: str, protect_superadmin: bool = True) -> bool:
    """
    Hard‑delete a user (and cascading link rows).

    Set `protect_superadmin=False` if you truly want the ability to remove
    a super‑admin account.
    """
    statement = select(User).where(User.username == username)
    user=db.exec(statement).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with username={user} not found")

    if protect_superadmin and user.usertype == UserType.superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Deleting a super‑admin is not allowed")

    db.delete(user)      # ON DELETE CASCADE covers link tables
    db.commit()
    return True
# endregion

# region module crud
def read_all_modules(db: Session) -> list[ModuleRead]:
    statement = select(Module).options(selectinload(Module.users))
    return db.exec(statement).all()
# endregion

