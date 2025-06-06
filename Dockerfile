FROM python:3.13-slim
ENV POETRY_VIRTUALENVS_CREATE=false \
    UVICORN_RELOAD=false
WORKDIR /code
RUN pip install poetry
COPY pyproject.toml poetry.lock /code/
RUN poetry install --without dev --no-root
COPY eav_backend/ /code/eav_backend/
COPY alembic/ /code/alembic/
COPY alembic.ini /code/alembic.ini
COPY examples/ /code/examples/

RUN groupadd -r fastapi && useradd -r -g fastapi fastapi
USER fastapi

CMD ["python", "-m", "eav_backend"]
