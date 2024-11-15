from pydantic import BaseModel


class GetVideoOutputSchema(BaseModel):
    id: int
    title: str
    user_id: int
    filename: str
    url: str | None
    score: float | None
