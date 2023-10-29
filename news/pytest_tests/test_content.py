import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_detail_page_contains_form(
        id_for_news, parametrized_client, form_in_context
):
    url = reverse('news:detail', args=(id_for_news))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context


def test_comments_order(client, id_for_news, two_comments):
    detail_url = reverse('news:detail', args=(id_for_news))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_news_count(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates
