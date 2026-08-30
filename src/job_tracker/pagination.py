from pydantic import BaseModel, Field

from .schemas import ApplicationRead


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedApplications(BaseModel):
    items: list[ApplicationRead]
    page: int
    page_size: int
    total: int
    pages: int
