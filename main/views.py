from .decorators import login_required_json
from django.shortcuts import render, redirect
from pathlib import Path
import json, hashlib

USERS_FILE = Path(__file__).resolve().parent.parent / "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f).get("users", [])
    return []

def home(request):
    return render(request, "home.html")

def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = hash_password(request.POST.get("password"))
        users = load_users()
        user = next((u for u in users if u["username"] == username and u["password"] == password), None)
        if user:
            request.session["user"] = user
            return redirect("/")
        error = "Identifiants invalides."
    return render(request, "login.html", {"error": error})

def logout_view(request):
    request.session.flush()
    return redirect("/login")

@login_required_json
def home(request):
    return render(request, "home.html")

