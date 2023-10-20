FROM python:3.11-slim AS base-build

ARG APP_PATH=/opt/app
ARG USER=backend-usr
ARG GROUP=backend-grp


ENV PYTHONUNBUFFERED=1 \
  # Prevents python creating .pyc files
  PYTHONDONTWRITEBYTECODE=1 \
  \
  # Pip
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry
  POETRY_VERSION=1.4.2 \
  # Make poetry install to this location
  POETRY_HOME="/usr/local" \
  # Make poetry not create a virtual environment
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR="/var/cache/pypoetry" \
  # Do not ask any interactive question
  POETRY_NO_INTERACTION=1

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  curl \
  # dependencies for building Python packages
  build-essential

# Install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN addgroup --system ${GROUP} \
  && adduser --system --ingroup ${GROUP} ${USER}

# Copy app code to WORKDIR
WORKDIR $APP_PATH
COPY --chown=${USER}:${GROUP} . ${APP_PATH}

# Make $USER owner of the WORKDIR directory as well
RUN chown -R ${USER}:${GROUP} ${APP_PATH}


FROM base-build AS dev-build

# Copy in the built poetry + app
COPY --from=base-build $POETRY_HOME $POETRY_HOME
COPY --from=base-build $APP_PATH $APP_PATH

RUN poetry install --with dev

USER ${USER}:${GROUP}

CMD ["poetry", "run", "python", "src/main.py"]


FROM base-build AS prod-build

# Copy in the built poetry + app
COPY --from=base-build $POETRY_HOME $POETRY_HOME
COPY --from=base-build $APP_PATH $APP_PATH

RUN poetry install --only main

USER ${USER}:${GROUP}

CMD ["poetry", "run", "python", "src/main.py"]
