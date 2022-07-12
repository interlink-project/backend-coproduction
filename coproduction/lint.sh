#!/usr/bin/env bash

set -x

mypy coproduction
black coproduction --check
isort --recursive --check-only coproduction
flake8
