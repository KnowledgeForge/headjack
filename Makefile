lint:
	pdm run pre-commit run --all-files

test:
	pdm run pytest tests/ ${PYTEST_ARGS}

coverage:
	pdm run coverage run --source=headjack/ -m pytest tests/ ${PYTEST_ARGS}
	pdm run coverage report -m --fail-under=0
	pdm run coverage html
