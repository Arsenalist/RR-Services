import json
import os

from bs4 import BeautifulSoup

from dataservices.utils.httputils import HttpUtils
from dataservices.utils.misc import remove_attrs, decorate_table_with_material_design, findDomain

podcast_string_map = {
    'reaction': 'reaction',
    'talking-raptors': 'talking raptors',
    'weekly': 'weekly'
}


def get_podcasts(podcast_type):
    feed = json.loads(HttpUtils.make_request('https://assets.raptorsrepublic.com/rapcast.json'))
    result = []
    max_results = 20
    items = feed['rss']['channel']['item']
    for item in items:
        if podcast_string_map[podcast_type].lower() in str(item['title']['#text']).lower():
            result.append({
                'title': item['title']['#text'],
                'description': item['description']['#text'],
                'pubDate': item['pubDate']['#text'],
                'url': str(item['enclosure']['@url']),
                'playerUrl': str(item['enclosure']['@url']).replace('.mp3', '?').replace('traffic', 'player')
            })
        if len(result) > max_results:
            break
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
        results['contracts'] = str(contracts[0])
    return results


def get_draft_history():
    text = HttpUtils.make_request('https://www.basketball-reference.com/teams/TOR/draft.html')
    soup = BeautifulSoup(text)
    results = {}
    # get table
    history = soup.find(id="draft")
    results['history'] = str(history)
    return results


def get_articles_by_category(category_id):
    return decorate_posts(
        json.loads(HttpUtils.make_request("https://www.raptorsrepublic.com/wp-json/wp/v2/posts?categories="
                                          + str(category_id), with_headers=True)))


def get_latest():
    return decorate_posts(json.loads(HttpUtils.make_request("https://www.raptorsrepublic.com/wp-json/wp/v2/posts",
                                                            with_headers=True)))


def decorate_posts(posts):
    items = []
    for item in posts:
        items.append({
            'title': item['title']['rendered'],
            'url': item['link'],
            'id': item['id'],
            'image': get_featured_media_url(item['featured_media']),
            'excerpt': item['excerpt']['rendered']
        })
    return items


def get_featured_media_url(media_id):
    media = json.loads(HttpUtils.make_request('https://www.raptorsrepublic.com/wp-json/wp/v2/media/' + str(media_id),
                                              with_headers=True))
    return media['guid']['rendered']


def get_user(user_id):
    return json.loads(HttpUtils.make_request('https://www.raptorsrepublic.com/wp-json/wp/v2/users/' + str(user_id),
                                             with_headers=True))


def get_article(id):
    article = json.loads(HttpUtils.make_request("https://www.raptorsrepublic.com/wp-json/wp/v2/posts/" + id,
                                                with_headers=True))
    disqus_identifier = "raptorsrepublic-" + str(id)
    user = get_user(article['author'])
    result = {
        'title': article['title']['rendered'],
        'image': get_featured_media_url(article['featured_media']),
        'html': article['content']['rendered'],
        'author_name': user['name'],
        'author_avatar_url': user['avatar_urls']['96'],
        'date_gmt': article['date_gmt'],
        'disqus_identifier': disqus_identifier
    }
    return result


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
    client_key = 'AIzaSyBj4_ZtlcLvxjaGXRJVzvO6suavNiT5-kc'
    channel_id = 'UCr7Qh5Ks10ub49U6sCmywoA'
    url = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&part=snippet,id&order=date&maxResults=20' \
        .format(client_key, channel_id)
    youtube_feed = json.loads(HttpUtils.make_request(url, with_headers=True))
    if 'items' not in youtube_feed:
        raise Exception("Could not get YouTube feed, instead got: " + str(youtube_feed))
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
    return json.loads(HttpUtils.make_request('https://assets.raptorsrepublic.com/insta.json'))
