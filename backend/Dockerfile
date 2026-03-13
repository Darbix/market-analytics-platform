FROM python:3.12-slim

WORKDIR /backend

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy backend code
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
