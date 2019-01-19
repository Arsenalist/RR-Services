import json
import os

from bs4 import BeautifulSoup

from services.utils.misc import considerCache, remove_attrs, decorate_table_with_material_design, findDomain


def get_web_articles():
    web_articles = json.loads(considerCache(os.environ.get('WEB_ARTICLES_ENDPOINT', '')))
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
    text = considerCache('https://www.rotowire.com/basketball/news.php?team=TOR')
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
    text = considerCache('https://www.basketball-reference.com/contracts/TOR.html')
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