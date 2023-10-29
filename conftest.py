from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def many_news(author):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def two_comments(author, news):
    now = timezone.now()
    for index in range(2):
        comments = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comments.created = now + timedelta(days=index)
        comments.save()
    return comments


@pytest.fixture
def id_for_news(news):
    return news.id,


@pytest.fixture
def id_for_comment(comment):
    return comment.id,


@pytest.fixture
def form_data():
    return {
        'text': 'Какой-то текст комментария',
    }
