
#!/bin/sh

./scripts/clean.sh

VERSION=`cat setup.py | grep '__version__ =' | sed 's/__version__ = //' | sed 's/"//g'`

# # uploading to pypi
python setup.py sdist
twine upload dist/*

# # creating git tag
echo "Creating tag version ${VERSION}:"
echo "git tag -a ${VERSION} -m 'Bump version ${VERSION}'"
echo "git push origin ${VERSION}"

# deploy documentation
mkdocs gh-deploy