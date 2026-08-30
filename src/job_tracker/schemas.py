from datetime import date, datetime

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from .models import ApplicationStatus, InterviewStatus, InterviewType


class ApplicationBase(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    company_id: int | None = Field(default=None, ge=1)
    role: str = Field(min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    job_url: AnyHttpUrl | None = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    applied_date: date = Field(default_factory=date.today)
    deadline: date | None = None
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("company", "role", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("must be a string")
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class ApplicationCreate(ApplicationBase):
    @model_validator(mode="after")
    def validate_dates(self):
        if self.deadline is not None and self.deadline < self.applied_date:
            raise ValueError("deadline cannot be before applied_date")
        return self


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=120)
    company_id: int | None = Field(default=None, ge=1)
    role: str | None = Field(default=None, min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    job_url: AnyHttpUrl | None = None
    status: ApplicationStatus | None = None
    applied_date: date | None = None
    deadline: date | None = None
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("company", "role", mode="before")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError("must be a string")
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class ApplicationRead(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    website: AnyHttpUrl | None = None
    industry: str | None = Field(default=None, max_length=160)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("must be a string")
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class CompanyRead(CompanyCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    role: str | None = Field(default=None, max_length=160)
    email: EmailStr | None = None
    linkedin_url: AnyHttpUrl | None = None

    @field_validator("name", "role", mode="before")
    @classmethod
    def strip_contact_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError("must be a string")
        value = value.strip()
        return value or None


class ContactRead(ContactCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int


class InterviewCreate(BaseModel):
    contact_id: int | None = None
    interview_type: InterviewType
    status: InterviewStatus = InterviewStatus.SCHEDULED
    scheduled_at: datetime
    notes: str | None = Field(default=None, max_length=5000)


class InterviewRead(InterviewCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int


class HistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    status: ApplicationStatus
    note: str | None
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DashboardStats(BaseModel):
    total_applications: int = Field(ge=0)
    by_status: dict[str, int]
    upcoming_interviews: int = Field(ge=0)
    upcoming_deadlines: int = Field(ge=0)
    offers: int = Field(ge=0)
    rejections: int = Field(ge=0)


class HealthResponse(BaseModel):
    status: str
    service: str
