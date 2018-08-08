#!/bin/bash

readonly ROOT_DIR="$(readlink -m "$(dirname "${0}")")"

find "${ROOT_DIR}/test" \
	-type f \
	-name '*.py' \
	! -name '__init__.py' \
	-exec 'python3' '-m' 'unittest' '{}' ';'
