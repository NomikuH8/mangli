'''Object used to return search results and the home page'''
import requests

from manga import Manga
import utils

CONTENT_RATINGS = '&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica'

class MangaSearcher():
    '''Searches for manga'''
    def __init__(self):
        pass


    def get_homepage(self, limit, page):
        '''
        Get the homepage mangas
        '''
        params = f'manga?limit={limit}&order[createdAt]=desc&offset={str(page * limit)}{CONTENT_RATINGS}'
        url = utils.API_URL + params
        resp = requests.get(url)
        parsed_mangas = []
        if resp.status_code == 200:
            for i in utils.parse_mangas(resp):
                parsed_mangas.append(i)
        return parsed_mangas


    def search_manga(self, limit, page, query: str, sort_type: str, sort_order: str):
        '''
        Search for the mangas
        '''
        params = f'manga?limit={limit}&offset={str(page * limit)}&order[{sort_type}]={sort_order}&title={query}&{CONTENT_RATINGS}'
        url = utils.API_URL + params
        resp = requests.get(url)
        parsed_mangas = []
        if resp.status_code == 200:
            if len(resp.json()['data']) == 0:
                return []
            for i in utils.parse_mangas(resp):
                parsed_mangas.append(i)
        return parsed_mangas


    def take_manga_page(self, manga_id):
        manga = Manga(manga_id)
        manga.get_info()
        manga.get_volumes(True)
        return manga.data


#ms = MangaSearcher()
#ayoya = ms.get_homepage(5, 2)
#ayoya = ms.search_manga(10, 0, '', utils.SEARCH_ORDER_OPTIONS[0], 'desc')
#manga = ms.take_manga_page('b62659e0-fb91-4cf1-a62f-c4e058f9917a')
#print(manga)
#for i in ayoya:
#    print(i['title'])
