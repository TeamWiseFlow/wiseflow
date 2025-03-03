version: '3.8'

services:
  pocketbase:
    image: ghcr.io/muchobien/pocketbase:latest
    ports:
      - '8090:8090'
    volumes:
      - ./pb:/pb
    restart: unless-stopped
    entrypoint: sh -c '/usr/local/bin/pocketbase superuser upsert $PB_SUPERUSER_EMAIL $PB_SUPERUSER_PASSWORD --dev --dir=/pb/pb_data && /usr/local/bin/pocketbase serve --dev --http=0.0.0.0:8090 --dir=/pb/pb_data --publicDir=/pb_public --hooksDir=/pb_hooks --migrationsDir=/pb/pb_migrations'
    environment:
      - PB_SUPERUSER_EMAIL=${PB_SUPERUSER_EMAIL}
      - PB_SUPERUSER_PASSWORD=${PB_SUPERUSER_PASSWORD}

  core:
    image: mcr.microsoft.com/playwright/python:v1.50.0-jammy
    volumes:
      - ./core:/app
      - ./docker/pip_cache:/root/.cache/pip
      - ${PROJECT_DIR}:/work_dir
    working_dir: /app
    command: sh -c 'pip install -r requirements.txt && python run_task.py'
    environment:
      - PB_API_BASE=http://pocketbase:8090
      - PB_API_AUTH=${PB_SUPERUSER_EMAIL}|${PB_SUPERUSER_PASSWORD}
      - VL_MODEL=${VL_MODEL}
      - PROJECT_DIR=/work_dir
      - LLM_API_KEY=${LLM_API_KEY}
      - LLM_API_BASE=${LLM_API_BASE}
      - ZHIPU_API_KEY=${ZHIPU_API_KEY}
      - PRIMARY_MODEL=${PRIMARY_MODEL}
      - SECONDARY_MODEL=${SECONDARY_MODEL}
      - LLM_CONCURRENT_NUMBER=${LLM_CONCURRENT_NUMBER:-1}
      - VERBOSE=${VERBOSE:-""}
      # - CRAWL4_AI_BASE_DIRECTORY=/work_dir
    depends_on:
      - pocketbase

volumes:
  work_dir:
