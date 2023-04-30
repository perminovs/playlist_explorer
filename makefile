BIN = .venv/bin/
CODE = playlist_organizer/
TEST = tests/

lint:
	$(BIN)flake8 --jobs 4 --statistics --show-source $(CODE)
	$(BIN)pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(BIN)mypy $(CODE)
	$(BIN)black --target-version py310 --skip-string-normalization --line-length=119 --check $(CODE) $(TEST)

pretty:
	$(BIN)isort --apply --recursive $(CODE) $(TEST)
	$(BIN)black --target-version py310 --skip-string-normalization --line-length=119 $(CODE) $(TEST)

plint: pretty lint

test:
	$(BIN)pytest $(TEST) -v
