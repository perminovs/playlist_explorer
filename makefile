BIN = .venv/bin/
FULL = organizer
CODE = organizer/organizer organizer/entrypoint.py

lint:
	$(BIN)flake8 --jobs 4 --statistics --show-source $(FULL)
	$(BIN)mypy $(CODE)
	$(BIN)black --target-version py38 --skip-string-normalization --line-length=119 --check $(FULL)

pretty:
	$(BIN)isort --apply --recursive $(FULL)
	$(BIN)black --target-version py38 --skip-string-normalization --line-length=119 $(FULL)

plint: pretty lint

tests:
	$(BIN)pytest $(FULL)/tests -v
