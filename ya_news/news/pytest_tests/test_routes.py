from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment


@pytest.mark.parametrize(
    'url_name, args',
    (
        ('news:home', None),
        ('news:detail', 'news_pk'),
        ('users:login', None),
        ('users:signup', None),
    ),
)
def test_public_pages_available_for_anonymous(
    client, news_item, url_name, args
):
    """Главная, детальная, вход и регистрация доступны анониму."""
    if args == 'news_pk':
        url = reverse(url_name, args=[news_item.pk])
    else:
        url = reverse(url_name)

    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    ('news:edit', 'news:delete'),
)
def test_author_can_access_edit_and_delete(author_client, comment, url_name):
    """Автор комментария получает 200 на edit и delete."""
    url = reverse(url_name, args=[comment.pk])
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    ('news:edit', 'news:delete'),
)
def test_other_user_gets_404_for_foreign_comment(
    other_client, comment, url_name
):
    """Другой пользователь не видит чужой комментарий (queryset фильтрует)."""
    url = reverse(url_name, args=[comment.pk])
    response = other_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_name',
    ('news:edit', 'news:delete'),
)
def test_anonymous_redirected_to_login_with_next(client, comment, url_name):
    """Аноним редиректится на логин, next содержит исходный адрес."""
    url = reverse(url_name, args=[comment.pk])
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND

    login_url = reverse('users:login')
    redirect = response.url

    assert redirect.startswith(login_url)
    assert 'next=' in redirect

    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirect)
    next_param = parse_qs(parsed.query).get('next', [None])[0]
    assert next_param == url


def test_logout_by_post_clears_session(author_client, author):
    """Авторизованный пользователь выходит POST-запросом."""
    logout_url = reverse('users:logout')

    assert '_auth_user_id' in author_client.session
    assert author_client.session['_auth_user_id'] == str(author.pk)

    response = author_client.post(logout_url)

    assert response.status_code in (
        HTTPStatus.OK,
        HTTPStatus.FOUND,
    )

    assert '_auth_user_id' not in author_client.session
