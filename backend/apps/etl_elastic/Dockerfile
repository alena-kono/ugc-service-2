FROM python:3.10-slim

# Update base
RUN apt-get update \
    && apt-get install -y --reinstall build-essential

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /service

# Installing dependencies
RUN pip install --upgrade pip \
    && pip install poetry

COPY ./README.md /service/README.md
COPY ./poetry.lock /service/poetry.lock
COPY ./pyproject.toml /service/pyproject.toml
COPY ./etl /service/etl
COPY ./configs /service/configs

RUN poetry config installer.max-workers 10 \
    && poetry install




ENTRYPOINT ["poetry","run", "python", "etl/main.py"]
