import pytest
from http import HTTPStatus

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

pytestmark = pytest.mark.django_db


def test_home_page_shows_no_more_than_limit(client, many_news, home_url):
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    news_on_page = response.context['news_list']
    assert news_on_page.count() <= NEWS_COUNT_ON_HOME_PAGE


def test_home_page_news_sorted_new_to_old(client, many_news, home_url):
    response = client.get(home_url)
    dates = [news.date for news in response.context['news_list']]
    assert dates == sorted(dates, reverse=True)


def test_detail_comments_sorted_old_to_new(
    client, news_item, comments_with_different_dates, news_detail_url
):
    response = client.get(news_detail_url)
    comments = list(response.context['object'].comment_set.all())
    created = [c.created for c in comments]
    assert created == sorted(created)


def test_anonymous_has_no_comment_form(client, news_item, news_detail_url):
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_author_gets_comment_form(author_client, news_item, news_detail_url):
    response = author_client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.context['form'], CommentForm)
