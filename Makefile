linters:
	pylint ./triple_barrier/*.py;
	pylint ./tests/triple_barrier/*.py;

unit-test:
	coverage run -m pytest ./tests/triple_barrier/unit/;

integration-test:
	pytest ./tests/triple_barrier/integration/;

build:
    rm ./dist/*;
	python -m build;
	twine upload ./dist/*;

reverse:
	pyreverse -o png ./strategy;