from datetime import (
    datetime,
    timedelta,
    timezone,
)

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    OAuth2PasswordBearer,
)

from jose import (
    JWTError,
    jwt,
)

from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.entities import User


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)


ALGORITHM = "HS256"


def get_password_hash(
    password: str,
) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def authenticate_user(
    db: Session,
    username: str,
    password: str,
):
    user = (
        db.query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user


def create_access_token(
    data: dict,
):
    payload = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=(
                settings
                .access_token_expire_minutes
            )
        )
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def get_current_user(
    token: str = Depends(
        oauth2_scheme
    ),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (
        JWTError,
        ValueError,
    ):
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user