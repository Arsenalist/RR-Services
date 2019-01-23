import json
import os

from bs4 import BeautifulSoup

from dataservices.utils.httputils import HttpUtils
from dataservices.utils.misc import remove_attrs, decorate_table_with_material_design, findDomain, encode_string, \
    decode_string, sanitize_content


def get_podcasts():
    feed = json.loads(HttpUtils.make_request('https://assets.raptorsrepublic.com/rapcast.json'))
    result = []
    max_results = 20
    items = feed['rss']['channel']['item']
    if len(items) > max_results:
        items = items[:max_results]
    for item in items:
        result.append({
            'title': item['title']['#text'],
            'description': item['description']['#text'],
            'pubDate': item['pubDate']['#text'],
            'url': item['enclosure']['@url']
        })
    return result


def get_web_articles():
    web_articles = json.loads(HttpUtils.make_request(os.environ.get('WEB_ARTICLES_ENDPOINT', '')))
    results = []
    for a in web_articles:
        article = {
            'title': a['description'],
            'description': a['extended'],
            'href': a['href'],
            'domain': findDomain(a['href'])
        }
        results.append(article)
    return results


def get_news():
    text = HttpUtils.make_request('https://www.rotowire.com/basketball/news.php?team=TOR')
    news_updates = []
    soup = BeautifulSoup(text)
    for s in soup.find_all('div', 'news-update'):
        update = {
            'name': s.find('a', 'news-update__player-link').get_text(),
            'headline': s.find('div', 'news-update__headline').get_text(),
            'timestamp': s.find('div', 'news-update__timestamp').get_text(),
            'text': s.find('div', 'news-update__news').get_text()
        }
        news_updates.append(update)
    return news_updates


def get_salaries():
    text = HttpUtils.make_request('https://www.basketball-reference.com/contracts/TOR.html')
    soup = BeautifulSoup(text)
    results = {}
    # get table
    contracts = soup.select('#contracts')
    for c in contracts:
        for a in c.find_all('a'):
            a.parent.append(a.get_text())
            a.decompose()
    if contracts is not None and len(contracts) != 0:
        results['contracts'] = decorate_table_with_material_design(str(remove_attrs(contracts[0])))
    return results


def get_latest():
    soup = BeautifulSoup(HttpUtils.make_request('https://www.raptorsrepublic.com/amp/', with_headers=True))
    items = []
    for item in soup.select('.amp-wp-article-header'):
        items.append({
            'title': item.find('a').get_text(),
            'url': item.find('a')['href'],
            'hash': encode_string(item.find('a')['href']),
            'image': item.find('amp-img')['src'].replace('-100x75', ''),
            'excerpt': item.find('div', class_='amp-wp-content-loop').find('p').get_text()
        })
    return items


def get_article(hash):
    url = decode_string(hash)
    soup = BeautifulSoup(HttpUtils.make_request(url, with_headers=True))
    article = {
        'title': soup.find('h1', class_='amp-wp-title').get_text(),
        'image': soup.find('amp-img', class_='attachment-large')['src'],
        'html': sanitize_content(str(soup.find('div', class_='the_content'))),
        'author': soup.find('span', class_='amp-wp-author').get_text()
    }
    return article


def get_players_instagram_feed():
    return json.loads(HttpUtils.make_request('https://forums.raptorsrepublic.com/insta.json'))