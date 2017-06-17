import re
import logging

import requests

from bs4 import BeautifulSoup

site_name = 'animeheaven'

BASE_URL = "http://animeheaven.eu"
SEARCH_URL = "%s/search.php" % (BASE_URL,)

source_pat = re.compile("<source src='(.*?)'")
epnum_pat = re.compile('e=(.*?)$')
status_pat = re.compile('<b>Status:</b> (.*?)<br/>')
released_pat = re.compile('<b>Year:</b> ([0-9]+)')

def _combine_link(url):
    return ("%s/%s" % (BASE_URL, url,)).replace(' ', '%20')

def _extract_single_search(data):
    anchor = data.find("a")
    name = anchor.find("img")['alt']
    return {
        'link': _combine_link(anchor['href']),
        'title': name,
        'language': 'dub' if 'dub' in name.lower() else 'sub',
        'host': site_name,
    }

def _extract_multiple_search(data):
    entries = data.findAll('div', {'class': 'iep'})
    # return list(map(lambda x: _extract_single_search(x), entries))
    return [_extract_single_search(x) for x in entries]

def _scrape_search_data(link, **kwargs):
    data = requests.get(link, kwargs).content

def search(query):
    '''
    Returns all search results based on a query
    [
        {
            'link': 'link to show on gogoanime',
            'title': 'the full title of the show',
            'language': 'either subbed or dubbed',
        }
    ]
    '''
    logging.info("A query for %s was made under animeheave" % (query,))
    params = {'q': query}
    data = requests.get(SEARCH_URL, params=params).content
    data = BeautifulSoup(data, 'html.parser')

    return _extract_multiple_search(data)

def _parse_list_single(data):
    return {
        'name': data.find("div", {"class": "infoept2"}),
        'link': _combine_link(data['href']),
    }

def _parse_list_multi(data):
    box = data.find("div", {"class": "infoepbox"})
    episodes = box.findAll("a")
    # return list(map(lambda x: _parse_list_single(x), episodes))
    return [_parse_list_single(x) for x in episodes]

def _scrape_single_video_source(data):
    return {
        'link': data,
        'type': 'mp4',
    }

def _scrape_epNum(url):
    return re.findall(epnum_pat, url)[0]

def _scrape_video_sources(link):
    logging.info("Scraping video sources for %s under animeheaven" % (link,))
    data = BeautifulSoup(requests.get(link).content, 'html.parser')
    sources = data.findAll("div", {'class': 'c'})
    sources = re.findall(source_pat, str(data))

    return {
        'epNum': _scrape_epNum(link),
        'sources': list(map(lambda x: _scrape_single_video_source(x), sources)),
    }

def _scrape_title(data):
    return data.find("div", {"class": "infodes"}).text

def _scrape_released(data):
    box = data.findAll("div", {"class": 'infodes2'})[1]
    return re.findall(released_pat, str(box))[0]

def _scrape_status(data):
    box = data.findAll("div", {"class": "infodes2"})[1]
    return re.findall(status_pat, str(box))[0]

def scrape_all_show_sources(link):
    logging.info("A request for '%s' was made to animeheaven scraper." % (link,))
    data = BeautifulSoup(requests.get(link).content, 'html.parser')
    episodes = _parse_list_multi(data)
    logging.debug("Got %i links for %s" % (len(episodes), link,))

    return {
        'episodes': [_scrape_video_sources(x['link']) for x in episodes],# list(map(lambda x: _scrape_video_sources(x['link']), episodes)),
        'title': _scrape_title(data),
        'status': _scrape_status(data),
        'host': 'animeheaven',
        'released': _scrape_released(data),
    }

matching_urls = [
    {
        'urls': [r'http://animeheaven.eu/i.php\?a=(.*)'],
        'function': scrape_all_show_sources,
    },
    {
        'urls': [r'http://animeheaven.eu/search.php\?q=(.*)'],
        'function': search,
    },
    {
        'urls': [r'http://animeheaven.eu/watch.php\?a=(.*)&e=([0-9]+)'],
        'function': _scrape_video_sources,
    }
]
