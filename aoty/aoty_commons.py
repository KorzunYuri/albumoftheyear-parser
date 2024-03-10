import time
import random
import requests


__aoty_base_url__ = 'https://www.albumoftheyear.org/'


class AotyCommons(object):

    @staticmethod
    def get_base_url():
        return __aoty_base_url__

    @staticmethod
    def __get_headers_for_https__():
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}

    @staticmethod
    def get_content_from_url(url):
        time.sleep(random.randint(1, 2))
        headers = AotyCommons.__get_headers_for_https__()
        print("calling {url}".format(url=url))
        response = requests.get(url=url, headers=headers)
        # response = urllib.request.urlopen(url).read()
        return response.content.decode('utf-8')
