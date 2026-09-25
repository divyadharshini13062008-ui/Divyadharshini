from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(
    directory="templates"
)


router = APIRouter(
    tags=["Pages"]
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "PocketSmart AI"
        },
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "title": "Login"
        },
    )


@router.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "title": "Create Account"
        },
    )


@router.get(
    "/home-planner",
    response_class=HTMLResponse,
)
def home_planner(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={
            "title": "Home Interior Planner"
        },
    )


@router.get(
    "/party-planner",
    response_class=HTMLResponse,
)
def party_planner(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={
            "title": "Party Planner"
        },
    )


@router.get(
    "/jewelry-planner",
    response_class=HTMLResponse,
)
def jewelry_planner(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={
            "title": "Jewelry Planner"
        },
    )


@router.get(
    "/history",
    response_class=HTMLResponse,
)
def history(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "title": "Recommendation History"
        },
    )