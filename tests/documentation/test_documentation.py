import pathlib

import pytest
from mktestdocs import check_md_file


@pytest.mark.parametrize("fpath", pathlib.Path(".").glob("**/*.md"), ids=str)
def test_docs(fpath):
    check_md_file(fpath=fpath)
