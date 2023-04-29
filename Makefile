lint:
	poetry run pre-commit run --all-files

test:
	poetry run pytest tests/ ${PYTEST_ARGS}

coverage:
	poetry run coverage run --source=headjack_server/ -m pytest tests/ ${PYTEST_ARGS}
	poetry run coverage report -m --fail-under=95
	poetry run coverage html
