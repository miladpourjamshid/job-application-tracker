from datetime import date

from .models import (
    ApplicationHistory,
    Company,
    Contact,
    Interview,
    JobApplication,
)
from .repositories import ApplicationRepository
from .schemas import (
    ApplicationCreate,
    ApplicationUpdate,
    CompanyCreate,
    ContactCreate,
    DashboardStats,
    InterviewCreate,
)


class ApplicationService:
    """Business rules for the complete job-application domain."""

    def __init__(self, repository: ApplicationRepository) -> None:
        self.repository = repository

    def get(self, application_id: int, user_id: int | None = None) -> JobApplication | None:
        return self.repository.get(application_id, user_id=user_id)

    def create(self, payload: ApplicationCreate, user_id: int) -> JobApplication:
        self._validate_dates(payload.applied_date, payload.deadline)
        self._validate_company(payload.company_id)
        data = payload.model_dump(mode="python")
        if data["job_url"] is not None:
            data["job_url"] = str(data["job_url"])
        application = JobApplication(user_id=user_id, **data)
        application.history.append(ApplicationHistory(status=payload.status.value))
        return self.repository.add(application)

    def dashboard(self, user_id: int) -> DashboardStats:
        return DashboardStats(**self.repository.dashboard_stats(user_id))

    def update(
        self, application: JobApplication, payload: ApplicationUpdate
    ) -> JobApplication:
        data = payload.model_dump(exclude_unset=True, mode="python")
        applied_date = data.get("applied_date", application.applied_date)
        deadline = data.get("deadline", application.deadline)
        self._validate_dates(applied_date, deadline)
        self._validate_company(data.get("company_id", application.company_id))
        old_status = application.status
        if data.get("job_url") is not None:
            data["job_url"] = str(data["job_url"])
        for field, value in data.items():
            setattr(application, field, value)
        if "status" in data and data["status"] != old_status:
            application.history.append(
                ApplicationHistory(status=data["status"].value, note="Status changed")
            )
        self.repository.db.commit()
        self.repository.db.refresh(application)
        return application

    def delete(self, application: JobApplication) -> None:
        self.repository.delete(application)

    def create_company(self, payload: CompanyCreate) -> Company:
        if self.repository.get_company_by_name(payload.name) is not None:
            raise ValueError("Company name is already registered")
        data = payload.model_dump(mode="python")
        if data["website"] is not None:
            data["website"] = str(data["website"])
        return self.repository.add_company(Company(**data))

    def get_company(self, company_id: int) -> Company | None:
        return self.repository.get_company(company_id)

    def list_companies(self) -> list[Company]:
        return self.repository.list_companies()

    def create_contact(self, company_id: int, payload: ContactCreate) -> Contact:
        if self.repository.get_company(company_id) is None:
            raise LookupError("Company not found")
        data = payload.model_dump(mode="python")
        if data["linkedin_url"] is not None:
            data["linkedin_url"] = str(data["linkedin_url"])
        return self.repository.add_contact(Contact(company_id=company_id, **data))

    def list_contacts(self, company_id: int) -> list[Contact]:
        if self.repository.get_company(company_id) is None:
            raise LookupError("Company not found")
        return self.repository.list_contacts(company_id)

    def create_interview(
        self, application_id: int, payload: InterviewCreate, user_id: int | None = None
    ) -> Interview:
        if self.repository.get(application_id, user_id=user_id) is None:
            raise LookupError("Application not found")
        if (
            payload.contact_id is not None
            and self.repository.get_contact(payload.contact_id) is None
        ):
            raise LookupError("Contact not found")
        return self.repository.add_interview(
            Interview(application_id=application_id, **payload.model_dump(mode="python"))
        )

    def list_interviews(
        self, application_id: int, user_id: int | None = None
    ) -> list[Interview]:
        if self.repository.get(application_id, user_id=user_id) is None:
            raise LookupError("Application not found")
        return self.repository.list_interviews(application_id, user_id=user_id)

    def list_history(
        self, application_id: int, user_id: int | None = None
    ) -> list[ApplicationHistory]:
        if self.repository.get(application_id, user_id=user_id) is None:
            raise LookupError("Application not found")
        return self.repository.list_history(application_id, user_id=user_id)

    def _validate_company(self, company_id: int | None) -> None:
        if company_id is not None and self.repository.get_company(company_id) is None:
            raise LookupError("Company not found")

    @staticmethod
    def _validate_dates(applied_date: date, deadline: date | None) -> None:
        if deadline is not None and deadline < applied_date:
            raise ValueError("deadline cannot be before applied_date")
