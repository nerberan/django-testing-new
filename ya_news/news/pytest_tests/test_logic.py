from http import HTTPStatus

import pytest
from django.test import TestCase

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

COMMENT_TEXT = 'Текст от анонима'
NEW_COMMENT_TEXT = 'Новый тестовый комментарий'
EDITED_TEXT = 'Изменённый текст'
BAD_COMMENT_TEXT = f'Ты {BAD_WORDS}!'
HACK_TEXT = 'Взлом!'


def test_anonym_cannot_create_comment(
    client, news_item, news_detail_url, login_url
):
    before = Comment.objects.count()
    data = {'text': COMMENT_TEXT}
    response = client.post(news_detail_url, data=data)
    assert response.status_code == HTTPStatus.FOUND
    assert login_url in response.url
    assert Comment.objects.count() == before


def test_author_creates_comment(
    author_client, author, news_item, news_detail_url
):
    response = author_client.post(
        news_detail_url, data={'text': NEW_COMMENT_TEXT}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news_item


@pytest.mark.parametrize(
    'fixture_name, method',
    (
        ('news_detail_url', 'post'),
        ('edit_comment_url', 'post'),
        ('delete_comment_url', 'post'),
    ),
)
def test_redirect_to_comments(
    author_client, request, fixture_name, method
):
    url = request.getfixturevalue(fixture_name)
    data = {'text': EDITED_TEXT}
    response = getattr(author_client, method)(url, data=data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')


def test_bad_word_comment(
    author_client, author, news_item, news_detail_url
):
    before = Comment.objects.count()
    data = {'text': BAD_COMMENT_TEXT}
    response = author_client.post(news_detail_url, data=data)
    assert response.status_code == HTTPStatus.OK
    form = response.context['form']
    TestCase().assertFormError(form, 'text', WARNING)
    assert Comment.objects.count() == before


def test_author_edits_comment_author_and_news(
    author_client, author, news_item, comment, edit_comment_url
):
    before = Comment.objects.count()
    response = author_client.post(
        edit_comment_url, data={'text': EDITED_TEXT}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == before
    updated = Comment.objects.get(pk=comment.pk)
    assert updated.text == EDITED_TEXT
    assert updated.author == author
    assert updated.news == news_item


def test_author_deletes_comment(author_client, comment, delete_comment_url):
    before = Comment.objects.count()
    pk = comment.pk
    response = author_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == before - 1
    assert not Comment.objects.filter(pk=pk).exists()


@pytest.mark.parametrize(
    'fixture_name',
    ('edit_comment_url', 'delete_comment_url'),
)
def test_other_user_cannot_touch_comment(
    other_client, comment, request, fixture_name
):
    url = request.getfixturevalue(fixture_name)
    before = Comment.objects.count()
    response = other_client.post(url, data={'text': HACK_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == before
    saved = Comment.objects.get(pk=comment.pk)
    assert saved.text == comment.text
    assert saved.author_id == comment.author_id
    assert saved.news_id == comment.news_id
