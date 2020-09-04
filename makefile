BIN = .venv/bin/
CODE = playlist_order

lint:
	$(BIN)flake8 --jobs 4 --statistics --show-source $(CODE)
	$(BIN)mypy $(CODE)
	$(BIN)black --target-version py38 --skip-string-normalization --line-length=119 --check $(CODE)

pretty:
	$(BIN)isort --apply --recursive $(CODE)
	$(BIN)black --target-version py38 --skip-string-normalization --line-length=119 $(CODE)

plint: pretty lint
