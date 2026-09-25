from app.config import settings

from app.models.schemas import (
    HomePlannerRequest,
    PartyPlannerRequest,
    RecommendationItem,
    RecommendationResponse,
)

from app.services.catalog import (
    HOME_CATALOG,
    JEWELRY_CATALOG,
    PARTY_CATALOG,
)

from app.services.gemini import (
    gemini_service,
)


def normalize_items(
    items: list[dict],
    budget: float,
):
    normalized = []
    total = 0.0

    for item in items:

        try:
            price = float(
                item.get(
                    "price",
                    0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        if price < 0:
            continue

        if total + price > budget:
            continue

        normalized.append(
            RecommendationItem(
                name=str(
                    item.get(
                        "name",
                        "Recommended item",
                    )
                ),
                category=str(
                    item.get(
                        "category",
                        "General",
                    )
                ),
                price=price,
                description=str(
                    item.get(
                        "description",
                        "",
                    )
                ),
                reason=str(
                    item.get(
                        "reason",
                        "",
                    )
                ),
                source=str(
                    item.get(
                        "source",
                        "",
                    )
                ),
                url=str(
                    item.get(
                        "url",
                        "",
                    )
                ),
            )
        )

        total += price

    return normalized, total


def fallback_response(
    planner_type: str,
    budget: float,
    catalog: list[dict],
    summary: str,
):
    items, total = normalize_items(
        catalog,
        budget,
    )

    return RecommendationResponse(
        planner_type=planner_type,
        summary=summary,
        tips=[
            "Compare prices before purchasing.",
            "Keep a small amount of your budget for unexpected costs.",
            "Use recommendations as a starting point rather than live inventory.",
        ],
        items=items,
        total_estimated_cost=round(
            total,
            2,
        ),
        budget=budget,
    )


def generate_home_recommendations(
    data: HomePlannerRequest,
):
    if (
        settings.use_mock_ai
        or not settings.gemini_api_key
    ):
        return fallback_response(
            planner_type="home",
            budget=data.budget,
            catalog=HOME_CATALOG,
            summary=(
                f"A budget-conscious "
                f"{data.style} setup for "
                f"a {data.room_type}."
            ),
        )

    prompt = f"""
Planner: Home Interior

Room type:
{data.room_type}

Budget:
{data.budget}

Style:
{data.style}

Room size:
{data.room_size}

Preferred colors:
{data.preferred_colors}

Additional requirements:
{data.additional_requirements}

Create practical recommendations.
"""

    try:
        result = gemini_service.generate(
            prompt
        )

        items, total = normalize_items(
            result.get(
                "items",
                [],
            ),
            data.budget,
        )

        return RecommendationResponse(
            planner_type="home",
            summary=result.get(
                "summary",
                "Personalized home recommendations.",
            ),
            tips=result.get(
                "tips",
                [],
            ),
            items=items,
            total_estimated_cost=round(
                total,
                2,
            ),
            budget=data.budget,
        )

    except Exception:
        return fallback_response(
            planner_type="home",
            budget=data.budget,
            catalog=HOME_CATALOG,
            summary=(
                "AI service was unavailable, "
                "so a budget-friendly fallback "
                "catalog was used."
            ),
        )


def generate_party_recommendations(
    data: PartyPlannerRequest,
):
    if (
        settings.use_mock_ai
        or not settings.gemini_api_key
    ):
        return fallback_response(
            planner_type="party",
            budget=data.budget,
            catalog=PARTY_CATALOG,
            summary=(
                f"A practical party plan "
                f"for {data.guests} guests."
            ),
        )

    prompt = f"""
Planner: Party Planning

Occasion:
{data.occasion}

Budget:
{data.budget}

Guests:
{data.guests}

Location type:
{data.location_type}

Theme:
{data.theme}

Food preference:
{data.food_preference}

Additional requirements:
{data.additional_requirements}

Create practical party recommendations.
"""

    try:
        result = gemini_service.generate(
            prompt
        )

        items, total = normalize_items(
            result.get(
                "items",
                [],
            ),
            data.budget,
        )

        return RecommendationResponse(
            planner_type="party",
            summary=result.get(
                "summary",
                "Personalized party recommendations.",
            ),
            tips=result.get(
                "tips",
                [],
            ),
            items=items,
            total_estimated_cost=round(
                total,
                2,
            ),
            budget=data.budget,
        )

    except Exception:
        return fallback_response(
            planner_type="party",
            budget=data.budget,
            catalog=PARTY_CATALOG,
            summary=(
                "AI service was unavailable, "
                "so a budget-friendly fallback "
                "catalog was used."
            ),
        )


def generate_jewelry_recommendations(
    data: dict,
    image_bytes: bytes | None = None,
    mime_type: str = "image/jpeg",
):
    budget = float(
        data["budget"]
    )

    if (
        settings.use_mock_ai
        or not settings.gemini_api_key
    ):
        return fallback_response(
            planner_type="jewelry",
            budget=budget,
            catalog=JEWELRY_CATALOG,
            summary=(
                f"Jewelry suggestions for "
                f"{data['occasion']}."
            ),
        )

    prompt = f"""
Planner: Jewelry

Occasion:
{data["occasion"]}

Budget:
{budget}

Jewelry type:
{data["jewelry_type"]}

Metal preference:
{data["metal_preference"]}

Color preference:
{data["color_preference"]}

Style:
{data["style"]}

Additional requirements:
{data["additional_requirements"]}

If an image is supplied, use it only as visual
context for the recommendation.

Create practical jewelry recommendations.
"""

    try:
        result = gemini_service.generate(
            prompt=prompt,
            image_bytes=image_bytes,
            mime_type=mime_type,
        )

        items, total = normalize_items(
            result.get(
                "items",
                [],
            ),
            budget,
        )

        return RecommendationResponse(
            planner_type="jewelry",
            summary=result.get(
                "summary",
                "Personalized jewelry recommendations.",
            ),
            tips=result.get(
                "tips",
                [],
            ),
            items=items,
            total_estimated_cost=round(
                total,
                2,
            ),
            budget=budget,
        )

    except Exception:
        return fallback_response(
            planner_type="jewelry",
            budget=budget,
            catalog=JEWELRY_CATALOG,
            summary=(
                "AI service was unavailable, "
                "so a budget-friendly fallback "
                "catalog was used."
            ),
        )