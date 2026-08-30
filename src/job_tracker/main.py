from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .auth import authenticate_user, create_access_token, get_current_user, register_user
from .config import settings
from .db import get_db
from .models import ApplicationStatus, JobApplication, User
from .pagination import PaginatedApplications, Pagination
from .repositories import ApplicationRepository
from .schemas import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    CompanyCreate,
    CompanyRead,
    ContactCreate,
    ContactRead,
    DashboardStats,
    HealthResponse,
    HistoryRead,
    InterviewCreate,
    InterviewRead,
    TokenResponse,
    UserCreate,
    UserRead,
)
from .services import ApplicationService
from .version import __version__

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "A professional REST API for managing job applications and domain data."
    ),
)


def get_service(db: Session = Depends(get_db)) -> ApplicationService:
    return ApplicationService(ApplicationRepository(db))


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)


@app.post(
    "/auth/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    try:
        return register_user(db, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id))


@app.get("/auth/me", response_model=UserRead, tags=["auth"])
def current_user(user: User = Depends(get_current_user)) -> User:
    return user


@app.get("/dashboard", response_model=DashboardStats, tags=["dashboard"])
def dashboard(
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> DashboardStats:
    return service.dashboard(user.id)


@app.post(
    "/applications",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["applications"],
)
def create_application(
    payload: ApplicationCreate,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> JobApplication:
    try:
        return service.create(payload, user.id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/applications", response_model=PaginatedApplications, tags=["applications"])
def list_applications(
    pagination: Pagination = Depends(),
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    company: str | None = Query(default=None, min_length=1),
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> PaginatedApplications:
    repository = service.repository
    items = repository.list(
        user_id=user.id,
        status_filter=status_filter,
        company=company,
        offset=pagination.offset,
        limit=pagination.page_size,
    )
    total = repository.count(
        user_id=user.id, status_filter=status_filter, company=company
    )
    pages = (total + pagination.page_size - 1) // pagination.page_size
    return PaginatedApplications(
        items=items,
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
        pages=pages,
    )


@app.get(
    "/applications/{application_id}",
    response_model=ApplicationRead,
    tags=["applications"],
)
def get_application(
    application_id: int,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> JobApplication:
    application = service.get(application_id, user_id=user.id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.patch(
    "/applications/{application_id}",
    response_model=ApplicationRead,
    tags=["applications"],
)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> JobApplication:
    application = service.get(application_id, user_id=user.id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    try:
        return service.update(application, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["applications"],
)
def delete_application(
    application_id: int,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> None:
    application = service.get(application_id, user_id=user.id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    service.delete(application)


@app.post(
    "/companies",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
    tags=["companies"],
)
def create_company(
    payload: CompanyCreate,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> CompanyRead:
    try:
        return service.create_company(payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/companies", response_model=list[CompanyRead], tags=["companies"])
def list_companies(
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> list[CompanyRead]:
    return service.list_companies()


@app.get(
    "/companies/{company_id}",
    response_model=CompanyRead,
    tags=["companies"],
)
def get_company(
    company_id: int,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> CompanyRead:
    company = service.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@app.post(
    "/companies/{company_id}/contacts",
    response_model=ContactRead,
    status_code=status.HTTP_201_CREATED,
    tags=["contacts"],
)
def create_contact(
    company_id: int,
    payload: ContactCreate,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> ContactRead:
    try:
        return service.create_contact(company_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get(
    "/companies/{company_id}/contacts",
    response_model=list[ContactRead],
    tags=["contacts"],
)
def list_contacts(
    company_id: int,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> list[ContactRead]:
    try:
        return service.list_contacts(company_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/applications/{application_id}/interviews",
    response_model=InterviewRead,
    status_code=status.HTTP_201_CREATED,
    tags=["interviews"],
)
def create_interview(
    application_id: int,
    payload: InterviewCreate,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> InterviewRead:
    try:
        return service.create_interview(application_id, payload, user_id=user.id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get(
    "/applications/{application_id}/interviews",
    response_model=list[InterviewRead],
    tags=["interviews"],
)
def list_interviews(
    application_id: int,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> list[InterviewRead]:
    try:
        return service.list_interviews(application_id, user_id=user.id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get(
    "/applications/{application_id}/history",
    response_model=list[HistoryRead],
    tags=["history"],
)
def list_history(
    application_id: int,
    user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_service),
) -> list[HistoryRead]:
    try:
        return service.list_history(application_id, user_id=user.id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
