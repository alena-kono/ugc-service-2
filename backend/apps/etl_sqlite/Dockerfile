FROM python:3.10-slim

# Update base
RUN apt-get update \
    && apt-get install -y --reinstall build-essential

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /etl

# Installing dependencies
RUN pip install --upgrade pip \
    && pip install poetry

COPY . .

RUN poetry config installer.max-workers 10 \
    && poetry install


ENTRYPOINT ["poetry","run", "python", "sqlite_to_postgres/load_data.py"]
