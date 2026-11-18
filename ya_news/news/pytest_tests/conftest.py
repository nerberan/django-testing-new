import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(db, django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def other_user(db, django_user_model):
    return django_user_model.objects.create(username='Другой пользователь')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def other_client(other_user):
    client = Client()
    client.force_login(other_user)
    return client


@pytest.fixture
def news_item(db):
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
    )


@pytest.fixture
def comment(db, news_item, author):
    return Comment.objects.create(
        news=news_item,
        author=author,
        text='Текст тестового комментария',
    )


@pytest.fixture
def many_news(db):
    return News.objects.bulk_create(
        [
            News(
                title=f'Новость {i}',
                text='Текст тестовой новости',
            )
            for i in range(NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )


@pytest.fixture
def comments_with_different_dates(db, news_item, author):
    now = timezone.now()
    comments = []
    for i in range(4):
        comment = Comment.objects.create(
            news=news_item,
            author=author,
            text=f'Тестовый комментарий {i}',
        )

        Comment.objects.filter(pk=comment.pk).update(
            created=now - timezone.timedelta(days=i)
        )
        comments.append(comment)
    return comments


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news_item):
    return reverse('news:detail', args=[news_item.pk])


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=[comment.pk])


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=[comment.pk])


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def urls(home_url, news_detail_url, edit_comment_url, delete_comment_url):
    return {
        'home': home_url,
        'detail': news_detail_url,
        'edit': edit_comment_url,
        'delete': delete_comment_url,
    }
