.PHONY: install test run clean lint format

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html

run:
	python -m src.main

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf memory_store/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 src/ tests/

format:
	black src/ tests/

setup-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8
	pip install -e .
