from bs4 import BeautifulSoup

from aoty_commons import AotyCommons as Aoty


input_file = open('input/input_lists.txt', mode='r', encoding="utf-8")
error_file = open('errors/errors_lists.txt', mode='w', encoding="utf-8")
output_lists = open('output/output_lists.txt', mode='w', encoding="utf-8")
output_albums = open('output/output_lists_albums.txt', mode='w', encoding="utf-8")
for l in input_file:
    page_number = 1
    btn_next = None
    base_url = l.replace('\n', '')
    while page_number == 1 or btn_next is not None:
        url = base_url + ("{}".format(page_number) if page_number > 1 else '')
        content = Aoty.get_content_from_url(url)
        soup = BeautifulSoup(content, 'html.parser')
        #   list name
        if page_number == 1:
            list_div = soup.find('div', attrs={'class': 'listHeader'})
            list_name = list_div.find('h1', attrs={'class': 'headline'}).text
            list_link = list_div.find('a')['href']
            output_lists.write("{top}\t{link}\n".format(top=list_name, link=list_link))
        album_divs = soup.find_all('div', attrs={'class': 'albumListRow'})
        print(f"found {len(album_divs)} albums")
        #   iterate and make objects
        albums = []
        for div in album_divs:
            rank = div['id'].replace('rank-', '') if div.has_attr('id') else ''
            a = div.find('h2', attrs={'class': 'albumListTitle'}) \
                .find('a', attrs={'itemprop': 'url'})
            release_link = Aoty.get_base_url() + a['href']
            release_title = a.contents[0]
            print(release_title)
            artist_name, release_name = release_title.split(' - ', 1)
            # write line
            output_albums.write("{list_name}\t{list_link}\t{rank}\t{artist}\t{release}\t{link}\n" \
                                .format(list_name=list_name, list_link=list_link, rank=rank, artist=artist_name,
                                        release=release_name, link=release_link))
        #   check if btn_next exists
        btn_next = soup.find('div', attrs={'class': 'pageSelect next'})
        page_number = page_number + 1
