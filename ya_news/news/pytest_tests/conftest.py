import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

NEWS_ON_PAGE = 10


@pytest.fixture
def author(db, django_user_model):
    """Автор комментария."""
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def other_user(db, django_user_model):
    """Другой пользователь."""
    return django_user_model.objects.create(username='Другой пользователь')


@pytest.fixture
def author_client(author):
    """Авторизованный клиент автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def other_client(other_user):
    """Авторизованный клиент другого пользователя."""
    client = Client()
    client.force_login(other_user)
    return client


@pytest.fixture
def news_item(db):
    """Одна новость."""
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
    )


@pytest.fixture
def comment(db, news_item, author):
    """Комментарий автора к новости."""
    return Comment.objects.create(
        news=news_item,
        author=author,
        text='Текст тестового комментария',
    )


@pytest.fixture
def many_news(db):
    """Набор из 11 новостей для проверки лимита в 10."""
    return News.objects.bulk_create(
        [
            News(
                title=f'Новость {i}',
                text='Текст тестовой новости',
            )
            for i in range(NEWS_ON_PAGE + 1)
        ]
    )


@pytest.fixture
def comments_with_different_dates(db, news_item, author):
    """Несколько комментариев с разным временем создания."""
    now = timezone.now()
    comments = []
    for i in range(3):
        c = Comment.objects.create(
            news=news_item,
            author=author,
            text=f'Комментарий {i}',
        )

        Comment.objects.filter(pk=c.pk).update(
            created=now - timezone.timedelta(days=i)
        )
        comments.append(c)
    return comments


@pytest.fixture
def urls(news_item):
    """Часто используемые адреса."""
    return {
        'home': reverse('news:home'),
        'detail': reverse('news:detail', args=[news_item.pk]),
        'edit': reverse('news:edit', args=[news_item.pk]),
        'delete': reverse('news:delete', args=[news_item.pk]),
    }
