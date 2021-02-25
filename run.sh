#!/bin/bash
cat config/heroku_config.yaml | envsubst > config/config.yaml

echo STARTING "$1"
alembic upgrade head
python main.py "$1"