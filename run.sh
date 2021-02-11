cat config/heroku_config.yaml | envsubst > config/config.yaml
# необходимо для того, чтобы alembic смог найти наше приложение
export PYTHONPATH=.
python main.py