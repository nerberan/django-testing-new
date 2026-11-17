from http import HTTPStatus

from django.urls import reverse

from news.forms import CommentForm


NEWS_LIMIT = 10
BAD_WORD = 'редиска'
BAD_WORD_ERROR = 'Не ругайтесь!'


def test_home_page_shows_no_more_than_limit(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    news_on_page = response.context['news_list']
    assert len(news_on_page) <= NEWS_LIMIT
    assert len(news_on_page) == NEWS_LIMIT


def test_home_page_news_sorted_new_to_old(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    dates = [news.date for news in response.context['news_list']]
    assert dates == sorted(dates, reverse=True)


def test_detail_comments_sorted_old_to_new(
    client, news_item, comments_with_different_dates
):
    url = reverse('news:detail', args=[news_item.pk])
    response = client.get(url)
    comments = list(response.context['object'].comment_set.all())
    created = [c.created for c in comments]
    assert created == sorted(created)


def test_anonymous_has_no_comment_form(client, news_item):
    url = reverse('news:detail', args=[news_item.pk])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_author_gets_comment_form(author_client, news_item):
    url = reverse('news:detail', args=[news_item.pk])
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context['form'], CommentForm)
