import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator

from app.database import get_db
from app.models.user import User
from app.auth.jwt_handler import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "student"  # 'student' or 'advisor'
    year: int | None = None  # class year 1-6, students only
    total_credits_required: float = 120


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    year: int | None = None
    total_credits_required: float
    advisor_name: str | None = None  # populated for students with an assigned advisor

    class Config:
        from_attributes = True

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_str(cls, value):
        return str(value)

    @field_validator("total_credits_required", mode="before")
    @classmethod
    def coerce_decimal_to_float(cls, value):
        return float(value) if value is not None else value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


def _build_user_out(db: Session, user: User) -> UserOut:
    advisor_name = None
    if user.role == "student" and user.advisor_id:
        advisor = db.get(User, user.advisor_id)
        if advisor:
            advisor_name = advisor.full_name

    out = UserOut.model_validate(user)
    out.advisor_name = advisor_name
    return out


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if payload.role not in ("student", "advisor"):
        raise HTTPException(status_code=400, detail="role must be 'student' or 'advisor'")
    if payload.year is not None and not (1 <= payload.year <= 6):
        raise HTTPException(status_code=400, detail="year must be between 1 and 6")

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user = User(
        id=uuid.uuid4(),
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        year=payload.year,
        total_credits_required=payload.total_credits_required,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=_build_user_out(db, user))


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=_build_user_out(db, user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _build_user_out(db, current_user)
