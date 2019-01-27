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


def get_quick_reaction():
    return parse_amp_article_list('https://www.raptorsrepublic.com/category/quick-reaction/amp/')


def get_morning_coffee():
    return parse_amp_article_list('https://www.raptorsrepublic.com/category/morning-coffee/amp/')


def get_latest():
    return parse_amp_article_list('https://www.raptorsrepublic.com/amp/')


def parse_amp_article_list(url):
    soup = BeautifulSoup(HttpUtils.make_request(url, with_headers=True))
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
    disqus_identifier = "raptorsrepublic-" + get_post_id(soup)
    article = {
        'title': soup.find('h1', class_='amp-wp-title').get_text(),
        'image': soup.find('amp-img', class_='attachment-large')['src'],
        'html': sanitize_content(str(soup.find('div', class_='the_content'))),
        'author': soup.find('span', class_='amp-wp-author').get_text(),
        'disqus_identifier': disqus_identifier
    }
    return article


# We're trying to parse <body class="body single-post 96993 post-id-96993 singular-96993 design_1_wrapper">
def get_post_id(soup):
    classes = soup.find('body').attrs['class']
    for c in classes:
        if c.startswith("post-id"):
            class_chunks = c.split("-")
            if len(class_chunks) == 3:
                return class_chunks[2]
    raise Exception("Could not parse disqus ID")


def get_youtube_feed():
    client_key = os.environ.get('YOUTUBE_CLIENT_API_KEY')
    channel_id = 'UCr7Qh5Ks10ub49U6sCmywoA'
    url = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&part=snippet,id&order=date&maxResults=20' \
        .format(client_key, channel_id)
    youtube_feed = json.loads(HttpUtils.make_request(url, with_headers=True))
    if 'items' not in youtube_feed:
        raise Exception("Could not get YouTube feed, instead got: " + youtube_feed)
    return condensed_youtube_feed(youtube_feed)


def condensed_youtube_feed(feed):
    items = []
    for item in feed["items"]:
        items.append({
            'videoId': item['id']['videoId'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'title': item['snippet']['title'],
            'publishedAt': item['snippet']['publishedAt']
        })
    return items


def get_players_instagram_feed():
    return json.loads(HttpUtils.make_request('https://forums.raptorsrepublic.com/insta.json'))
