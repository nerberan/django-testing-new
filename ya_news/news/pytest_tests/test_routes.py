from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

import pytest


@pytest.mark.parametrize(
    'fixture_name',
    ('home_url', 'news_detail_url', 'login_url', 'signup_url'),
)
def test_pages_available_for_anonym(
    client, news_item, request, fixture_name
):
    url = request.getfixturevalue(fixture_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'fixture_name',
    ('edit_comment_url', 'delete_comment_url'),
)
def test_author_can_edit_and_delete(
    author_client, comment, request, fixture_name
):
    url = request.getfixturevalue(fixture_name)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'fixture_name',
    ('edit_comment_url', 'delete_comment_url'),
)
def test_other_user_gets_404_for_comment(
    other_client, comment, request, fixture_name
):
    url = request.getfixturevalue(fixture_name)
    response = other_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'fixture_name',
    ('edit_comment_url', 'delete_comment_url'),
)
def test_anonym_redirected_to_login(
    client, comment, login_url, request, fixture_name
):
    url = request.getfixturevalue(fixture_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    redirect = response.url
    assert redirect.startswith(login_url)
    assert 'next=' in redirect
    parsed = urlparse(redirect)
    next_param = parse_qs(parsed.query).get('next', [None])[0]
    assert next_param == url


def test_logout_by_post_clears_session(author_client, author, logout_url):
    assert '_auth_user_id' in author_client.session
    assert author_client.session['_auth_user_id'] == str(author.pk)
    response = author_client.post(logout_url)
    assert response.status_code in (
        HTTPStatus.OK,
        HTTPStatus.FOUND,
    )
    assert '_auth_user_id' not in author_client.session
