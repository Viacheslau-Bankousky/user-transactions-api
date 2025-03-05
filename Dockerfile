FROM python:3.12 AS builder

WORKDIR /internship-task

COPY poetry.lock pyproject.toml /internship-task/

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

FROM python:3.12-slim AS runtime

WORKDIR /internship-task

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /internship-task

ENV PYTHONPATH=/internship-task

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

