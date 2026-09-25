from typing import Any

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100,
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HomePlannerRequest(BaseModel):
    room_type: str

    budget: float = Field(gt=0)

    style: str

    room_size: str

    preferred_colors: str = ""

    additional_requirements: str = ""


class PartyPlannerRequest(BaseModel):
    occasion: str

    budget: float = Field(gt=0)

    guests: int = Field(gt=0)

    location_type: str

    theme: str

    food_preference: str = ""

    additional_requirements: str = ""


class JewelryPlannerRequest(BaseModel):
    occasion: str

    budget: float = Field(gt=0)

    jewelry_type: str

    metal_preference: str = ""

    color_preference: str = ""

    style: str = ""

    additional_requirements: str = ""


class RecommendationItem(BaseModel):
    name: str
    category: str
    price: float
    description: str
    reason: str = ""
    source: str = ""
    url: str = ""


class RecommendationResponse(BaseModel):
    planner_type: str
    summary: str
    tips: list[str]
    items: list[RecommendationItem]
    total_estimated_cost: float
    budget: float
    recommendation_id: int | None = None


class HistoryResponse(BaseModel):
    id: int
    planner_type: str
    created_at: str
    request_data: dict[str, Any]
    response_data: dict[str, Any]