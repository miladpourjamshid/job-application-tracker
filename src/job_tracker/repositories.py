from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from .models import (
    ApplicationHistory,
    ApplicationStatus,
    Company,
    Contact,
    Interview,
    JobApplication,
    User,
)


class ApplicationRepository:
    """Data-access operations for the application domain."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, application_id: int, user_id: int | None = None) -> JobApplication | None:
        statement = select(JobApplication).where(JobApplication.id == application_id)
        if user_id is not None:
            statement = statement.where(JobApplication.user_id == user_id)
        return self.db.scalar(statement)

    def list(
        self,
        *,
        user_id: int | None = None,
        status_filter: ApplicationStatus | None = None,
        company: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[JobApplication]:
        statement: Select[tuple[JobApplication]] = select(JobApplication).order_by(
            JobApplication.applied_date.desc(), JobApplication.id.desc()
        )
        if user_id is not None:
            statement = statement.where(JobApplication.user_id == user_id)
        if status_filter is not None:
            statement = statement.where(JobApplication.status == status_filter)
        if company:
            statement = statement.where(
                JobApplication.company.ilike(f"%{company.strip()}%")
            )
        return list(self.db.scalars(statement.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        user_id: int | None = None,
        status_filter: ApplicationStatus | None = None,
        company: str | None = None,
    ) -> int:
        statement = select(func.count()).select_from(JobApplication)
        if user_id is not None:
            statement = statement.where(JobApplication.user_id == user_id)
        if status_filter is not None:
            statement = statement.where(JobApplication.status == status_filter)
        if company:
            statement = statement.where(
                JobApplication.company.ilike(f"%{company.strip()}%")
            )
        return int(self.db.scalar(statement) or 0)

    def dashboard_stats(self, user_id: int) -> dict[str, object]:
        status_rows = self.db.execute(
            select(JobApplication.status, func.count())
            .where(JobApplication.user_id == user_id)
            .group_by(JobApplication.status)
        ).all()
        by_status = {str(status): int(total) for status, total in status_rows}
        total = sum(by_status.values())
        now = datetime.now(UTC)
        upcoming_interviews = self.db.scalar(
            select(func.count())
            .select_from(Interview)
            .join(JobApplication)
            .where(
                JobApplication.user_id == user_id,
                Interview.scheduled_at >= now,
                Interview.status == "scheduled",
            )
        )
        upcoming_deadlines = self.db.scalar(
            select(func.count())
            .select_from(JobApplication)
            .where(
                JobApplication.user_id == user_id,
                JobApplication.deadline >= now.date(),
            )
        )
        return {
            "total_applications": total,
            "by_status": by_status,
            "upcoming_interviews": int(upcoming_interviews or 0),
            "upcoming_deadlines": int(upcoming_deadlines or 0),
            "offers": by_status.get(ApplicationStatus.OFFER.value, 0),
            "rejections": by_status.get(ApplicationStatus.REJECTED.value, 0),
        }

    def add(self, application: JobApplication) -> JobApplication:
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def delete(self, application: JobApplication) -> None:
        self.db.delete(application)
        self.db.commit()

    def add_company(self, company: Company) -> Company:
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get_company(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)

    def get_company_by_name(self, name: str) -> Company | None:
        statement = select(Company).where(Company.name == name.strip())
        return self.db.scalar(statement)

    def list_companies(self) -> list[Company]:
        return list(self.db.scalars(select(Company).order_by(Company.name)).all())

    def add_contact(self, contact: Contact) -> Contact:
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def get_contact(self, contact_id: int) -> Contact | None:
        return self.db.get(Contact, contact_id)

    def list_contacts(self, company_id: int) -> list[Contact]:
        statement = (
            select(Contact)
            .where(Contact.company_id == company_id)
            .order_by(Contact.name)
        )
        return list(self.db.scalars(statement).all())

    def add_interview(self, interview: Interview) -> Interview:
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def list_interviews(
        self, application_id: int, user_id: int | None = None
    ) -> list[Interview]:
        statement = select(Interview).join(JobApplication).where(
            Interview.application_id == application_id
        )
        if user_id is not None:
            statement = statement.where(JobApplication.user_id == user_id)
        statement = statement.order_by(Interview.scheduled_at)
        return list(self.db.scalars(statement).all())

    def list_history(
        self, application_id: int, user_id: int | None = None
    ) -> list[ApplicationHistory]:
        statement = select(ApplicationHistory).join(JobApplication).where(
            ApplicationHistory.application_id == application_id
        )
        if user_id is not None:
            statement = statement.where(JobApplication.user_id == user_id)
        statement = statement.order_by(ApplicationHistory.created_at, ApplicationHistory.id)
        return list(self.db.scalars(statement).all())

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.strip().lower())
        return self.db.scalar(statement)

    def get_user(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def add_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
