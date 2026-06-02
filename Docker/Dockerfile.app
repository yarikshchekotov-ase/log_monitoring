FROM python:3.12.11-slim

WORKDIR /app
RUN groupadd --gid 2000 node && useradd --uid 2000 --gid node --shell /bin/bash --create-home node

COPY requirements/req_app_fastapi.txt ./
RUN pip install --no-cache-dir -r req_app_fastapi.txt

USER node

COPY --chown=node:node ./app/ ./
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000" ]