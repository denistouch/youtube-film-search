FROM python:3.12-alpine

RUN pip install --no-cache-dir poetry


WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

CMD ["poetry", "run", "python", "app/main.py"]
