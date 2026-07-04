web: gunicorn nutritrack.api.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
admin: gunicorn run_admin:app --bind 0.0.0.0:$PORT
worker: celery -A nutritrack.worker.celery_app worker --loglevel=info