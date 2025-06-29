from fastapi.responses import RedirectResponse
from fastapi import Request
from passlib.context import CryptContext
import re

def flash(request: Request, message: str, category: str = "info"):
    """Add a flash message to the session"""
    if "_flashes" not in request.session:
        request.session["_flashes"] = []
    request.session["_flashes"].append({"message": message, "category": category})

def get_flashed_messages(request: Request) -> list[dict[str, object]]:
    """Get and clear flash messages from session"""
    flashes = request.session.get("_flashes", [])
    if flashes:
        request.session["_flashes"] = []  # Clear after reading
    return flashes

def redirect_to_route(request: Request, route_name: str, status_code: int = 303):
    """Helper function to redirect to a named route"""
    return RedirectResponse(request.url_for(route_name), status_code=status_code)

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None