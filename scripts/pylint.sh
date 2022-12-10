#!/bin/bash -eux

python3 -m pylint $(find . -name "*.py" -not -path "./venv/*") --reports=yes --rcfile=.pylintrc
