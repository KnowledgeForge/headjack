lint:
	poetry run pre-commit run --all-files

test:
	poetry run pytest tests/ ${PYTEST_ARGS}

coverage:
	poetry run coverage run --source=headjack/ -m pytest tests/ ${PYTEST_ARGS}
	poetry run coverage report -m --fail-under=0
	poetry run coverage html
