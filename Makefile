# vim: set noet sw=4 ts=4 fileencoding=utf-8:

# Project-specific constants
NAME=mosromgr
DOC_HTML=docs/build/html
DOC_TREES=docs/build/doctrees

# Default target
all:
	@echo "make install - Install on local system"
	@echo "make develop - Install symlinks for development"
	@echo "make build - Build sdist and bdist_wheel"
	@echo "make clean - Remove all generated files"
	@echo "make lint - Run linter"
	@echo "make test - Run tests"
	@echo "make doc-graphs - Generate graphviz graphs"
	@echo "make doc - Build the docs as HTML"
	@echo "make doc-serve - Serve the docs locally"
	@echo "make release - Release to PyPI"

install:
	pip install .

develop:
	pip install -e .[test,doc]
	pip install twine
	@echo "To build the docs you will also need to install graphviz using apt/brew"

build: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf build/ dist/ $(NAME).egg-info/ docs/build/ .pytest_cache/ .coverage

lint:
	pylint -E mosromgr

test:
	coverage run --rcfile coverage.cfg -m pytest -v tests
	coverage report --rcfile coverage.cfg

doc-graphs:
	python docs/images/class_hierarchy.py

doc: doc-graphs
	rm -rf docs/build/
	sphinx-build -b html -d $(DOC_TREES) docs/ $(DOC_HTML)

doc-serve:
	python -m http.server -d $(DOC_HTML)

release:
	twine upload dist/*

.PHONY: all install develop build clean lint test doc-graphs doc doc-serve release
