#!/usr/bin/env bash

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place coproduction --exclude=__init__.py
black coproduction
isort --recursive --force-single-line-imports --apply coproduction
