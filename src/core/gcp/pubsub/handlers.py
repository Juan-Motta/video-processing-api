from strenum import StrEnum

from src.apps.dummy.tasks import dummy_event_handler


class PubSubEvents(StrEnum):
    DUMMY_EVENT = "dummy_event"
    PROCESS_VIDEO = "process_video"


EVENT_HANDLERS: dict = {
    PubSubEvents.DUMMY_EVENT: dummy_event_handler,
}
