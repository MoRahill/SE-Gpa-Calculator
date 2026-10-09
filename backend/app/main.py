from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import users, gpa, prediction, advisor

app = FastAPI(title="GPA Calculator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(gpa.router)
app.include_router(prediction.router)
app.include_router(advisor.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "gpa-calculator-api"}
