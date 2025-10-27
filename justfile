format:
	uv run ruff format

lint:
	uv run ruff check --fix

test:
	uv run pytest --verbose --color=yes tests

validate: format lint test
