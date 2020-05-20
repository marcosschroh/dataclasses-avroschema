#!/bin/sh

if [ -d 'dist' ] ; then
    rm -rf dist
fi

if [ -d 'site' ] ; then
    rm -rf site
fi

if [ -d 'htmlcov' ] ; then
    rm -rf htmlcov
fi

if [ -d 'python_schema_registry_client.egg-info' ] ; then
    rm -rf python_schema_registry_client.egg-info
fi

# delete python cache
find . -iname '*.pyc' -delete
find . -iname '__pycache__' -delete
