import os
import uuid
from typing import Annotated
from fastapi import FastAPI, Request, Depends, HTTPException,UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import Session, select

from app.models import UserRead, User, Module

from app.core.database import init_db, get_session
from app.dependencies.auth import (
    auth_router, get_current_active_user, 
    verify_password, get_password_hash)
from app.core.config import settings
from app.core.utils import (
    flash, get_flashed_messages, 
    redirect_to_route, is_valid_email)

# Module routes
from app.api.users_and_permissions import users_and_permissions_router
from app.api.design_test_catalogue import design_test_catalogue_router
from app.api.lab_quality_control import lab_quality_control_router
from app.api.mp_common_definitions import mp_common_definitions_router

async def lifespan(app: FastAPI):
    # Load the ML model
    init_db()
    yield

app = FastAPI(lifespan=lifespan, title='M&P Portal', description='Outsourcing responsibility is the fastest path to regret.')

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

SessionDep = Annotated[Session, Depends(get_session)]

app.include_router(auth_router)
app.include_router(users_and_permissions_router)
app.include_router(design_test_catalogue_router)
app.include_router(lab_quality_control_router)
app.include_router(mp_common_definitions_router)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", include_in_schema=False, name='dashboard', response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
    # db: SessionDep,
):
    """
    Show the dashboard with modules that *this* user can access.
    A user’s access is defined by the many‑to‑many relationship
    User <-> UserModuleLink <-> Module.
    """

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
    })

@app.get("/user_profile", include_in_schema=False, name='user_profile', response_class=HTMLResponse)
async def user_profile(
    request: Request, 
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
    db: Session = Depends(get_session)
):
    # Refresh user data from database
    db_user = db.exec(select(User).where(User.username == current_user.username)).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="UserRead not found")
    
    flash_messages = get_flashed_messages(request)

    return templates.TemplateResponse("user_profile.html", {
        "request": request,
        "user": current_user,
        "flash_messages": flash_messages
    })

# redirects to user_profile
@app.post("/update_profile", include_in_schema=False, name="update_profile", response_class=RedirectResponse)
async def update_profile(
    request: Request,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_session),
    email: str = Form(...),
    profile_image: UploadFile = File(None),
):
    try:
        # Refresh user data
        user = db.exec(select(User).where(User.username == current_user.username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="UserRead not found")
        
        # Check if email is being changed
        if email != user.email:
            # Verify new email is not taken
            existing_user = db.exec(select(User).where(User.email == email)).first()
            if existing_user and existing_user.username != user.username:
                flash(request, "Email is already in use by another account.", "error")
                return redirect_to_route(request, "user_profile")
        
        if not is_valid_email(email):
            flash(request, "Invalid email format", "error")
            return redirect_to_route(request, "user_profile")
               
        # Update email only (name, surname, title are now read-only)
        user.email = email
        
        # Handle profile image upload
        images_path = os.path.join('app', 'static', 'images')
        if profile_image and profile_image.filename:
            # Validate file
            allowed_types = ["image/jpeg", "image/png", "image/gif"]
            if profile_image.content_type not in allowed_types:
                flash(request, "Invalid image format. Please use JPEG, PNG, or GIF.", "error")
                return redirect_to_route(request, "user_profile")
                        
            # Validate file size (max 5MB)
            if profile_image.size > 5 * 1024 * 1024:
                flash(request, "File too large. Maximum size is 5MB.", "error")
                return RedirectResponse("/userprofile", status_code=303)
                        
            # Generate unique filename
            ext = profile_image.filename.split(".")[-1]
            filename = f"{user.username}_profile_image_{uuid.uuid4().hex[:8]}.{ext}"
            file_path = os.path.join(images_path, filename)
            
            # Save the file
            with open(file_path, "wb") as f:
                f.write(await profile_image.read())
            
            # Delete old image if not default
            if user.profile_image_path != "default_profile_image.png":
                old_path = os.path.join(images_path,user.profile_image_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            user.profile_image_path = filename
            

        db.add(user)
        db.commit()

        # Success messages
        flash(request, "Profile updated successfully!", "success")

    except Exception as e:
        flash(request, f"An error occurred: {str(e)}", "error")

    return redirect_to_route(request, "user_profile")

# redirects to user_profile
@app.post("/update_password", include_in_schema=False, name='update_password', response_class=RedirectResponse)
async def update_password(
    request: Request,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_session),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    try:
        # Refresh user data to ensure we have the latest
        user = db.exec(select(User).where(User.username == current_user.username)).first()
        if not user:
            flash(request, "UserRead not found.", "error")
            return redirect_to_route(request, "user_profile")
        
        if new_password != confirm_password:
            flash(request, "New passwords do not match.", "error")
            return redirect_to_route(request, "user_profile")

        
        # Verify current password
        if not verify_password(current_password, user.hashed_pw):
            flash(request, "Current password is incorrect.", "error")
            return redirect_to_route(request, "user_profile")
        
        # Update password
        user.hashed_pw = get_password_hash(new_password)
        db.add(user)
        db.commit()
        flash(request, "Password changed successfully!", "success")

    except Exception as e:
        flash(request, f"An error occurred: {str(e)}", "error")

    return redirect_to_route(request, "user_profile")
