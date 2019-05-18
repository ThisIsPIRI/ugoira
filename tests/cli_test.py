from click.testing import CliRunner

import responses

from ugoira.cli import ugoira
from ugoira.lib import get_illust_url

ugoira_id = 74442143
multiple_download_ids = [ugoira_id, 74442144]
non_ugoira_id = 74073488
zip_url = 'https://i.pximg.net/img-zip-ugoira/img/2019/04/29/16/09/38/74442143_ugoira600x600.zip'
multiple_download_zips = [zip_url,
                          'https://i.pximg.net/img-zip-ugoira/img/2019/04/29/16/09/39/74442144_ugoira600x600.zip']

def test_download(fx_tmpdir, fx_ugoira_body, fx_ugoira_zip):
    """Test for command download"""

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': get_illust_url(ugoira_id),
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })
        responses.add(**{
            'method': responses.HEAD,
            'url': zip_url,
            'status': 200,
        })
        responses.add(**{
            'method': responses.GET,
            'url': zip_url,
            'body': fx_ugoira_zip,
            'content_type': 'application/zip',
            'status': 200,
        })

        runner = CliRunner()
        result = runner.invoke(
            ugoira,
            [str(ugoira_id)]
        )
        assert result.exit_code == 0
        assert result.output.strip() == (
            'Downloading {} (0/1)\n'.format(ugoira_id) + 
            'Download was completed successfully.'
            ' format is {} and output path is {}{}'.format(
                'gif',
                ugoira_id,
                '.gif',
            )
        )

    test()


def test_mutliple_downloads(fx_tmpdir, fx_ugoira_body, fx_ugoira_zip):
    """Tests downloading multiple files at once."""

    @responses.activate
    def test():
        responses.reset()
        for i in range(len(multiple_download_ids)):
            responses.add(**{
                'method': responses.GET,
                'url': get_illust_url(multiple_download_ids[i]),
                'body': fx_ugoira_body,  # Note: this is actually same for every id.
                'content_type': 'text/html; charset=utf-8',
                'status': 200,
                'match_querystring': True,
            })
            responses.add(**{
                'method': responses.HEAD,
                'url': multiple_download_zips[i],
                'status': 200,
            })
            responses.add(**{
                'method': responses.GET,
                'url': multiple_download_zips[i],
                'body': fx_ugoira_zip,
                'content_type': 'application/zip',
                'status': 200,
            })

        runner = CliRunner()
        result = runner.invoke(
            ugoira,
            [str(i) for i in multiple_download_ids]
        )
        assert result.exit_code == 0
        expected = ''
        for i in range(len(multiple_download_ids)):
            expected += (
                'Downloading {} ({}/{})\n'.format(multiple_download_ids[i], i, len(multiple_download_ids)) +
                'Download was completed successfully.'
                ' format is {} and output path is {}{}'.format(
                    'gif',
                    multiple_download_ids[i],
                    '.gif\n',
                )
            )
        expected = expected[0:-1]  # Remove the trailing newline.
        assert result.output.strip() == expected

    test()


def test_error(fx_tmpdir, fx_ugoira_body, fx_ugoira_zip):
    """Test for encount PixivError"""

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': get_illust_url(ugoira_id),
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })
        responses.add(**{
            'method': responses.HEAD,
            'url': zip_url,
            'status': 503,
        })

        runner = CliRunner()
        result = runner.invoke(
            ugoira,
            [str(ugoira_id)]
        )
        assert result.output.strip() == (
            'Downloading {} (0/1)\n'.format(ugoira_id) + 
            'Error: Wrong image src. Please report it with illust-id'
        )

    test()


def test_is_not_ugoira(fx_non_ugoira_body):
    """Test for command download as gif"""

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': get_illust_url(non_ugoira_id),
            'body': fx_non_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })

        runner = CliRunner()
        result = runner.invoke(
            ugoira,
            [str(non_ugoira_id)]
        )
        assert result.output.strip() == (
            'Downloading {} (0/1)\n'.format(non_ugoira_id) +
            'Illust ID {} is not ugoira.'.format(non_ugoira_id)
        )

    test()
