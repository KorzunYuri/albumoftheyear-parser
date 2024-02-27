from bs4 import BeautifulSoup

import requests
import re
from difflib import SequenceMatcher
import time
import random

__aoty_base_url__ = 'https://www.albumoftheyear.org/'


def __get_headers_for_https__():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}


def __filter_list__(lst):
    return list(filter(lambda item: item is not None, lst))


def get_content_from_url(url):
    time.sleep(random.randint(1, 2))
    headers = __get_headers_for_https__()
    print("calling {url}".format(url=url))
    response = requests.get(url=url, headers=headers)
    # response = urllib.request.urlopen(url).read()
    return response.content.decode('utf-8')


class AotySearchPageParser(object):

    def get_release_info(self, artist, release):

        #   search by artist and release
        url = self.get_search_link(artist, release)
        release_divs = self.__get_release_divs__(get_content_from_url(url))
        release_info = self.__find_best_match__(release_divs, artist, release)

        if release_info is None:
            # search best match by artist and album separately
            release_info_by_release  = \
                self.__find_best_match__( \
                    self.__get_release_divs__( \
                        get_content_from_url( \
                            self.get_search_link(release=release))) \
                    , artist, release)
            release_info_by_artist   = \
                self.__find_best_match__( \
                    self.__get_release_divs__( \
                        get_content_from_url( \
                            self.get_search_link(artist=artist))) \
                    , artist, release)
            candidates = __filter_list__([release_info_by_release, release_info_by_artist])
            if len(candidates) == 1:
                release_info = candidates[0]
            elif len(candidates) > 1:
                release_info = candidates[0] if candidates[0]['match_ratio'] > candidates[1]['match_ratio'] else candidates[1]

        #   make a final object
        if release_info is not None:
            release_title_div = release_info['div'].find('div', attrs={'class': 'albumTitle'})
            if release_title_div is not None:
                return {
                    'artist_name': release_info['artist_name'],
                    'release_name': release_info['release_name'],
                    'release_link': __aoty_base_url__ + release_title_div.parent['href']
                }
        return None

    def __get_release_divs__(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        return soup.body.find_all('div', attrs={'class': 'albumBlock', 'data-type': 'lp'})

    def __prepare_search_token__(self, token):
        return token.replace(' ', '+')\
            .replace('&', '%26')

    def get_search_link(self, artist=None, release=None):
        tokens = __filter_list__([artist, release])
        params = map(self.__prepare_search_token__, tokens)
        return __aoty_base_url__ + "/search/?q={params}".format(params='+'.join(params))

    def __find_best_match__(self, release_block_divs, artist_name, release_name):
        if len(release_block_divs) == 1:
            return self.__get_release_info__(release_block_divs[0], artist_name, release_name)
        else:
            print(f"found {len(release_block_divs)} LPs for {artist_name} - {release_name}")
            best_score = 0
            best_match = None
            for release_block_div in release_block_divs:
                release_info = self.__get_release_info__(release_block_div, artist_name, release_name)
                if release_info['match_ratio'] > best_score:
                    best_score = release_info['match_ratio']
                    best_match = release_info
            return best_match

    def __get_release_info__(self, release_div, artist_name_input, release_name_input):
        release_name_actual = self.__get_lp_name__(release_div)
        artist_name_actual = self.__get_lp_artist__(release_div)
        artist_match_ratio = SequenceMatcher(None, artist_name_actual, artist_name_input).ratio()
        release_match_ratio = SequenceMatcher(None, release_name_actual, release_name_input).ratio()
        match_ratio = release_match_ratio * artist_match_ratio
        return {
            'artist_name': artist_name_actual,
            'release_name': release_name_actual,
            'match_ratio': match_ratio,
            'div': release_div
        }

    def __get_lp_artist__(self, release_block_div):
        artist_title_div = release_block_div.find('div', attrs={'class': 'artistTitle'})
        if artist_title_div is not None:
            a = artist_title_div.parent
            return a.text
        return None

    def __get_lp_name__(self, release_block_div):
        release_title_div = release_block_div.find('div', attrs={'class': 'albumTitle'})
        if release_title_div is not None:
            a = release_title_div.parent
            return a.text
        return None


class AotyReleaseInfo(object):
    __content__ = None

    def __init__(self, release_link):
        self.__content__ = get_content_from_url(url=release_link)

    def get_reviews(self):
        reviews = []
        soup = BeautifulSoup(self.__content__, 'html.parser')
        critics_div = soup.body.find('div', attrs={'id': 'criticReviewContainer'})
        if critics_div is not None:
            reviews_div = critics_div.find_all('div', attrs={'class': 'albumReviewRow'})
            for review_div in reviews_div:
                review_info = {}
                review_info['rating'] = review_div.find('span', attrs={'itemprop': 'ratingValue'}).text
                review_info['platform'] = review_div.find('div', attrs={'class': 'publication'}) \
                    .find('span', attrs={'itemprop': 'name'}).text
                #   author
                author_div = review_div.find('div', attrs={'class': 'author'})
                if author_div is not None:
                    author_name_a = author_div.find('a', attrs={'href': re.compile('^/critic/.*')})
                    review_info['author'] = author_name_a.text
                    review_info['author_link'] = __aoty_base_url__ + author_name_a.attrs['href']

                #   review link
                review_links_div = review_div.find('div', attrs={'class': 'albumReviewLinks'})
                if review_links_div is not None:
                    review_link_div = review_links_div.find('div', attrs={'class': 'extLink'})
                    if review_link_div is not None:
                        review_link_a = review_link_div.find_all('a', attrs={'itemprop': 'url'})
                        if len(review_link_a) > 0:
                            review_info['review_link'] = review_link_a[0]['href']

                reviews.append(review_info)

        return reviews
