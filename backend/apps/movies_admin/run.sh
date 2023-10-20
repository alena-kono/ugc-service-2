poetry run python manage.py collectstatic --no-input && \
poetry run python manage.py migrate && \
poetry run gunicorn -c gunicorn/gunicorn.py
