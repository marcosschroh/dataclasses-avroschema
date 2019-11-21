#!/bin/sh

./scripts/clean.sh

VERSION=`cat setup.py | grep '__version__ =' | sed 's/__version__ = //' | sed 's/"//g'`

# # uploading to pypi
python setup.py sdist
twine upload dist/*

# # creating git tag
echo "Creating tag version v${VERSION}:"
git tag -a v${VERSION} -m 'Bump version v${VERSION}'

echo "git push origin v${VERSION}"

# deploy documentation
mkdocs gh-deploy
