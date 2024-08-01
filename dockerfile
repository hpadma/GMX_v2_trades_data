FROM python:3.9

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . /app/

CMD ["sh", "-c", "prisma db push && prisma generate && python3.9 main.py"]
