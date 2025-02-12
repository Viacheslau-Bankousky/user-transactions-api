FROM python:3.12

WORKDIR /internship-task

COPY . /internship-task

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root


ENV PYTHONPATH=/internship-task

