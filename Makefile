# For details on Makefiles, see the section notes.

# Specify phony list to ensure make recipes do not conflict with real file names
.PHONY: run-service-development db-migrations

# alambic migrations db
db-migrations:
	@echo "+ $@"
	alembic -c alembic.ini upgrade head

# start up Flask API service
run-service-development:
	@echo "+ $@"
	python run.py

# app run with monitoring
run-service-wsgi:
	@echo "+ $@"
	gunicorn --bind 0.0.0.0:5000 \
			--workers=1 \
			--log-config gunicorn_logging.conf \
			--log-level=DEBUG \
			--access-logfile=- \
			--error-logfile=- \
			run:application