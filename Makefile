LND := submodules/lnd/%

all: test

clean:
	rm -rf build dist *.egg-info/ .tox/ target/
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

test:
	tox
	tox -e codechecks

$(LND):
	git submodule update --init

itest: $(LND)
	./src/itests/run_itest.sh

coverage:
	tox -e coverage

mypy:
	tox -e mypy

freeze:
	python -m fbs freeze

.PHONY: all clean test coverage mypy freeze
