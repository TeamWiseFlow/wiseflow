set -o allexport
source .env
set +o allexport
uvicorn main:app --reload --host localhost --port 7777