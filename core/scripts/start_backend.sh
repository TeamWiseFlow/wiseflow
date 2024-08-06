#!/bin/bash
set -o allexport
source ../.env
set +o allexport
exec uvicorn backend:app --reload --host localhost --port 8077