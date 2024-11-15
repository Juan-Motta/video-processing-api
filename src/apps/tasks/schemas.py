from datetime import datetime

from pydantic import BaseModel, field_validator


class CreateTaskOutputSchema(BaseModel):
    message: str
    id: int
    task_id: str


class GetAllTaskOutputSchema(BaseModel):
    id: int
    task_id: str
    user_id: int
    original_video_id: int | None
    processed_video_id: int | None
    status: str
    created_at: datetime | str | None
    updated_at: datetime | str | None
    is_active: bool

    @field_validator("created_at", "updated_at")
    @classmethod
    def validate_datetime(cls, value):
        if value is None:
            return None
        return value.isoformat()


class GetTaskVideoOutputSchema(BaseModel):
    title: str
    user_id: int
    filename: str
    url: str | None
    score: float | None


class GetTaskOutputSchema(BaseModel):
    id: int
    task_id: str
    user_id: int
    original_video: GetTaskVideoOutputSchema | None
    processed_video: GetTaskVideoOutputSchema | None
    status: str
    created_at: datetime | str | None
    updated_at: datetime | str | None
    is_active: bool

    @field_validator("created_at", "updated_at")
    @classmethod
    def validate_datetime(cls, value):
        if value is None:
            return None
        return value.isoformat()


class DeleteTaskOutputSchema(BaseModel):
    message: str
    id: int
    task_id: str
    is_active: bool
