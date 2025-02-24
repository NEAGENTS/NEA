.PHONY: quality style test docs utils

check_dirs := .

# Quality checks
# -----------------------------
# Ensure the source code meets quality standards

extra_quality_checks:
	python utils/check_copies.py
	python utils/check_dummies.py
	python utils/check_repo.py
	doc-builder style nea docs/source --max_len 119

quality:
	ruff check $(check_dirs)
	ruff format --check $(check_dirs)
	doc-builder style nea docs/source --max_len 119 --check_only

style:
	ruff check $(check_dirs) --fix
	ruff format $(check_dirs)
	doc-builder style nea docs/source --max_len 119

# Testing
# -----------------------------
# Run specific tests or all tests for the library

test_big_modeling:
	python -m pytest -s -v ./tests/test_big_modeling.py ./tests/test_modeling_utils.py \
		$(if $(IS_GITHUB_CI),--report-log "$(PYTORCH_VERSION)_big_modeling.log",)

test_core:
	python -m pytest -s -v ./tests/ --ignore=./tests/test_examples.py \
		$(if $(IS_GITHUB_CI),--report-log "$(PYTORCH_VERSION)_core.log",)

test_cli:
	python -m pytest -s -v ./tests/test_cli.py \
		$(if $(IS_GITHUB_CI),--report-log "$(PYTORCH_VERSION)_cli.log",)

test_examples:
	python -m pytest -s -v ./tests/test_examples.py \
		$(if $(IS_GITHUB_CI),--report-log "$(PYTORCH_VERSION)_examples.log",)

test:
	$(MAKE) test_core
	$(MAKE) test_cli
	$(MAKE) test_big_modeling
	$(MAKE) test_deepspeed
	$(MAKE) test_fsdp

test_prod:
	$(MAKE) test_core

test_rest:
	python -m pytest -s -v ./tests/test_examples.py::FeatureExamplesTests \
		$(if $(IS_GITHUB_CI),--report-log "$(PYTORCH_VERSION)_rest.log",)
