FROM python:3.9

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PARALLEL_TASKS=6
ENV BLOCKS_PER_RUN=3000000
ENV BLOCKS_PER_CALL=50000

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . /app/

RUN chmod +rwx /app/wrapper_script.sh

CMD ["/app/wrapper_script.sh"]
