FROM python:3.11

WORKDIR /app
COPY pyproject.toml poetry.lock ./

# configure Poetry
ENV POETRY_VERSION=1.6.1

# installing Poetry
RUN pip install poetry==${POETRY_VERSION} && poetry install --no-root --no-directory
COPY src/ ./src/
RUN poetry install --no-dev

# run the application
CMD ["poetry", "run", "celery", "-A", "src.app", "worker", "-l", "INFO"]
