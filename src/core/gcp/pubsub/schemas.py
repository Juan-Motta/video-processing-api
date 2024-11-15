from pydantic import BaseModel


class PubSubEventMessage(BaseModel):
    event_type: str
    data: dict
