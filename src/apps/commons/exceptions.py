class CustomException(Exception):
    def __init__(
        self,
        error: str,
        message: str,
        status_code: int | None = 400,
        context: dict | None = None,
    ):
        self.error = error
        self.message = message
        self.status_code = status_code or 400
        self.context = context or None
