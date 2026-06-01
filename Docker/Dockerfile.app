FROM python:3.12.11-slim

WORKDIR /app

COPY requirements/req_app_fastapi.txt ./
RUN pip install --no-cache-dir -r req_app_fastapi.txt


COPY ./app/ ./
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000" ]