from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment

BAD_WORD = 'редиска'
BAD_WORD_ERROR = 'Не ругайтесь!'


def test_anonym_cannot_create_comment(client, news_item):
    url = reverse('news:detail', args=[news_item.pk])
    before = Comment.objects.count()
    data = {'text': 'Текст от анонима'}
    response = client.post(url, data=data)
    assert response.status_code == HTTPStatus.FOUND
    assert reverse('users:login') in response.url
    assert Comment.objects.count() == before


def test_author_creates_comment(author_client, author, news_item):
    url = reverse('news:detail', args=[news_item.pk])
    before = Comment.objects.count()
    text = 'Новый тестовый комментарий'
    response = author_client.post(url, data={'text': text})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')
    assert Comment.objects.count() == before + 1
    comment = Comment.objects.order_by('-pk').first()
    assert comment.text == text
    assert comment.author == author
    assert comment.news == news_item


@pytest.mark.parametrize(
    'url_name, method, args_from',
    (
        ('news:detail', 'post', 'news'),
        ('news:edit', 'post', 'comment'),
        ('news:delete', 'post', 'comment'),
    ),
)
def test_redirect_to_comments(
    author_client, news_item, comment, url_name, method, args_from
):
    obj = news_item if args_from == 'news' else comment
    url = reverse(url_name, args=[obj.pk])
    data = {'text': 'Обновлённый текст'}
    response = getattr(author_client, method)(url, data=data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')


def test_bad_word_comment(author_client, author, news_item):
    url = reverse('news:detail', args=[news_item.pk])
    before = Comment.objects.count()
    data = {'text': f'Ты {BAD_WORD}!'}
    response = author_client.post(url, data=data)
    assert response.status_code == HTTPStatus.OK
    form = response.context['form']
    assert form.errors
    assert BAD_WORD_ERROR in form.errors['text']
    assert Comment.objects.count() == before


def test_author_edits_comment_author_and_news(
    author_client, author, news_item, comment
):
    url = reverse('news:edit', args=[comment.pk])
    new_text = 'Изменённый текст'
    response = author_client.post(url, data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    updated = Comment.objects.get(pk=comment.pk)
    assert updated.text == new_text
    assert updated.author == author
    assert updated.news == news_item


def test_author_deletes_comment(author_client, comment):
    url = reverse('news:delete', args=[comment.pk])
    pk = comment.pk
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=pk).exists()


@pytest.mark.parametrize(
    'url_name',
    ('news:edit', 'news:delete'),
)
def test_other_user_cannot_touch_comment(
    other_client, comment, url_name
):
    url = reverse(url_name, args=[comment.pk])
    original_text = comment.text
    original_author_id = comment.author_id
    original_news_id = comment.news_id
    response = other_client.post(url, data={'text': 'Взлом!'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    saved = Comment.objects.get(pk=comment.pk)
    assert saved.text == original_text
    assert saved.author_id == original_author_id
    assert saved.news_id == original_news_id
