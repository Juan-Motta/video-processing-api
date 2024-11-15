FROM python:3.11-slim AS build

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt update \
    && apt install -y curl \
    && pip install --upgrade pip \
    && pip install poetry \
    && poetry config warnings.export false

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry export -f requirements.txt --output /app/requirements.txt --without-hashes

RUN pip install -r requirements.txt

COPY  . .

ENTRYPOINT ["pytest", "--cov", "--cov-report=html"]
