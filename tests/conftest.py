import os
import pathlib

from ugoira.lib import login

from click.testing import CliRunner
from pytest import fixture, skip


def pytest_addoption(parser):
    parser.addoption('--pixiv-id', default=os.getenv('PIXIV_ID', None))
    parser.addoption('--pixiv-password',
                     default=os.getenv('PIXIV_PASSWORD', None))


@fixture
def fx_tmpdir(tmpdir):
    return pathlib.Path(str(tmpdir))


@fixture
def fx_valid_id_pw(request):
    try:
        id = request.config.getoption('--pixiv-id')
    except ValueError:
        skip('This test must need --pixiv-id.')
    if id is None:
        skip('This test must need --pixiv-id.')

    try:
        password = request.config.getoption('--pixiv-password')
    except ValueError:
        skip('This test must need --pixiv-password.')
    if password is None:
        skip('This test must need --pixiv-password.')

    return id, password


@fixture
def fx_too_short_id_pw():
    return 'test', '1'


@fixture
def fx_invalid_id_pw():
    return 'test', 'test'


@fixture
def fx_login_only(fx_valid_id_pw):
    res = login(*fx_valid_id_pw)

    if not res:
        skip('This test must need valid id and password pair.')

    return True

@fixture
def fx_clirunner():
    return CliRunner()


@fixture
def fx_ugoira_body():
    with open('./tests/mock/ugoira.html') as f:
        return f.read().encode('u8')


@fixture
def fx_non_ugoira_body():
    with open('./tests/mock/non_ugoira.html') as f:
        return f.read().encode('u8')