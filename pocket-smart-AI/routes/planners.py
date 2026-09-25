import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

from app.models.entities import (
    RecommendationHistory,
    User,
)

from app.models.schemas import (
    HomePlannerRequest,
    PartyPlannerRequest,
    RecommendationResponse,
)

from app.services.auth import get_current_user

from app.services.recommendations import (
    generate_home_recommendations,
    generate_jewelry_recommendations,
    generate_party_recommendations,
)


router = APIRouter(
    tags=["Planners"]
)


def save_history(
    db: Session,
    user: User,
    planner_type: str,
    request_data: dict,
    response_data: dict,
):
    record = RecommendationHistory(
        user_id=user.id,
        planner_type=planner_type,
        request_data=json.dumps(
            request_data
        ),
        response_data=json.dumps(
            response_data
        ),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def save_and_return(
    db: Session,
    user: User,
    planner_type: str,
    request_data: dict,
    result: RecommendationResponse,
):
    response_data = result.model_dump()

    record = save_history(
        db,
        user,
        planner_type,
        request_data,
        response_data,
    )

    response_data[
        "recommendation_id"
    ] = record.id

    return RecommendationResponse(
        **response_data
    )


@router.post(
    "/generate-home",
    response_model=RecommendationResponse,
)
def generate_home(
    data: HomePlannerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    result = generate_home_recommendations(
        data
    )

    return save_and_return(
        db,
        current_user,
        "home",
        data.model_dump(),
        result,
    )


@router.post(
    "/generate-party",
    response_model=RecommendationResponse,
)
def generate_party(
    data: PartyPlannerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    result = generate_party_recommendations(
        data
    )

    return save_and_return(
        db,
        current_user,
        "party",
        data.model_dump(),
        result,
    )


@router.post(
    "/generate-jewelry",
    response_model=RecommendationResponse,
)
async def generate_jewelry(
    occasion: str = Form(...),
    budget: float = Form(...),
    jewelry_type: str = Form(...),
    metal_preference: str = Form(""),
    color_preference: str = Form(""),
    style: str = Form(""),
    additional_requirements: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    if budget <= 0:
        raise HTTPException(
            status_code=422,
            detail="Budget must be greater than zero.",
        )

    image_bytes = None
    mime_type = "image/jpeg"

    if image:
        image_bytes = await image.read()

        max_bytes = (
            settings.max_image_mb
            * 1024
            * 1024
        )

        if len(image_bytes) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=(
                    "Uploaded image is too large. "
                    f"Maximum size is "
                    f"{settings.max_image_mb} MB."
                ),
            )

        mime_type = (
            image.content_type
            or "image/jpeg"
        )

    data = {
        "occasion": occasion,
        "budget": budget,
        "jewelry_type": jewelry_type,
        "metal_preference": metal_preference,
        "color_preference": color_preference,
        "style": style,
        "additional_requirements": (
            additional_requirements
        ),
    }

    result = generate_jewelry_recommendations(
        data=data,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )

    return save_and_return(
        db,
        current_user,
        "jewelry",
        data,
        result,
    )


@router.get(
    "/recommendations-details/{recommendation_id}"
)
def recommendation_details(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    record = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.id
            == recommendation_id,
            RecommendationHistory.user_id
            == current_user.id,
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found.",
        )

    return {
        "id": record.id,
        "planner_type": record.planner_type,
        "created_at": (
            record.created_at.isoformat()
        ),
        "request_data": json.loads(
            record.request_data
        ),
        "response_data": json.loads(
            record.response_data
        ),
    }


@router.get("/history")
def recommendation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    records = (
        db.query(RecommendationHistory)
        .filter(
            RecommendationHistory.user_id
            == current_user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": record.id,
            "planner_type": record.planner_type,
            "created_at": (
                record.created_at.isoformat()
            ),
            "request_data": json.loads(
                record.request_data
            ),
            "response_data": json.loads(
                record.response_data
            ),
        }
        for record in records
    ]