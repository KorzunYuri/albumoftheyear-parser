from aoty.aotyparser import *

import time
import random

search_page_parser = AotySearchPageParser()

input_file  = open('input/input_reviews.txt', mode='r', encoding="utf-8")
error_file  = open('errors/errors_reviews.txt', mode='w', encoding="utf-8")
output_file = open('output/output_reviews.txt', mode='w', encoding="utf-8")
for l in input_file:
    line = l.replace('\n', '')
    try:
        artist, album = line.split('\t')
        album_info = search_page_parser.get_release_info(artist, album)
        if album_info is not None and album_info['release_link'] is not None:
            print(f'{artist}\t{album}\tLink found!\n')
            aoty_info = AotyReleaseInfo(album_info['release_link'])
            reviews = aoty_info.get_reviews()
            #   write to file
            for rvw in reviews:
                output_file.write(f"{artist}"
                                  f"\t{album}"
                                  f"\t{album_info['artist_name']}"
                                  f"\t{album_info['release_name']}"
                                  f"\t{album_info['release_link']}"
                                  f"\t{rvw['rating']}"
                                  f"\t{rvw['platform']}"
                                  f"\t{rvw['author'] if 'author' in rvw.keys() else ''}"
                                  f"\t{rvw['author_link'] if 'author_link' in rvw.keys() else ''}"
                                  f"\t{rvw['review_link'] if 'review_link' in rvw.keys() else ''}"
                                  f"\n")
        else:
            error_file.write("{artist}\t{album}\tFailed to find album\t{search_link}\n" \
                             .format(artist=artist,
                                     album=album,
                                     search_link=search_page_parser.get_search_link(artist, album)))
    except Exception as e:
        error_file.write('{line}\t{e}\n'.format(line=line, e=e))
    time.sleep(random.randint(2, 5))

#   free the resources
input_file.close()
output_file.close()
error_file.close()
