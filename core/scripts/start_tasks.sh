#!/bin/bash
set -o allexport
source ../.env
set +o allexport
exec python tasks.py