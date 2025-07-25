from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import weeks, professors, courses, semesters, config, events, auth, chronologie, calendrier

app = FastAPI(title="My API", version="0.1.0", debug=settings.debug)

# Autoriser le front Vue en local
origins = [settings.url_front]   # port par défaut de Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weeks.router)
app.include_router(professors.router)
app.include_router(courses.router)
app.include_router(semesters.router)
app.include_router(chronologie.router)
app.include_router(config.router)
app.include_router(events.router)
app.include_router(auth.router)
app.include_router(calendrier.router)

@app.get("/ping")
async def ping():
    return {"message": "pong"}
