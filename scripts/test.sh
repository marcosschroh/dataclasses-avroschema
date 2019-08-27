#!/bin/sh -e

set -o errexit

tests=${1-"./tests"}

pytest ${tests}