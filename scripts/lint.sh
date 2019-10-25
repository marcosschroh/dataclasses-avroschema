#!/bin/sh -e

set -o errexit

black . --check
flake8 .
