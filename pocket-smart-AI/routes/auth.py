from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    OAuth2PasswordRequestForm,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.entities import User

from app.models.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_username = (
        db.query(User)
        .filter(
            User.username
            == user_data.username
        )
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists.",
        )

    existing_email = (
        db.query(User)
        .filter(
            User.email
            == str(user_data.email)
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists.",
        )

    user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=get_password_hash(
            user_data.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        credentials.username,
        credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "username": user.username,
        }
    )

    return TokenResponse(
        access_token=token
    )


@router.post(
    "/token",
    response_model=TokenResponse,
)
def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "username": user.username,
        }
    )

    return TokenResponse(
        access_token=token
    )


@router.get("/session-info")
def session_info(
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        },
    }


@router.post("/logout")
def logout():
    return {
        "message": (
            "Logout successful. "
            "Remove the stored access token "
            "from the client."
        )
    }