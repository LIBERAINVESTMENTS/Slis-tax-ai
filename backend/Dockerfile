FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql+psycopg2://aiaccountant:aiaccountant@db:5432/aiaccountant
ENV ENVIRONMENT=production

CMD ["alembic", "upgrade", "head", "&&", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
