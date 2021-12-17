'''Manga object module, to make life easier.'''
# manga object
# title
# alt titles
# volumes
# chapters
# last chapter
# original language
# status {completed, ongoing, etc}
# content rating {safe, etc}
# author
# scanlators
import requests
from volume import Volume
import configs
import utils

class Manga():
    '''
    Manga object to collect and store all usefull information about it.
    '''
    def __init__(self, manga_id : str):
        self.data = {}

        self.volumes = []
        self.chapters_num = 0

        self.manga_id = manga_id
        self.hash = '' # id to take images


    def get_info(self):
        '''
        This function retrieves all the manga information from the site.
        '''
        params = '?includes[]=artist&includes[]=author&includes[]=cover_art'
        _resp = requests.get(utils.MANGA_URL + self.manga_id + params)
        if _resp.status_code == 200:
            data = _resp.json()['data']
            attrs = data['attributes']
            rel_ships = data['relationships']

            self.data['title'] = list(attrs['title'].values())[0]

            self.data['altTitles'] = []
            for i in attrs['altTitles']:
                self.data['altTitles'].append(i)

            self.data['description'] = attrs['description']['en']

            self.data['original_lang'] = attrs['originalLanguage']

            if attrs['lastVolume'] == 'null':
                self.data['last_volume'] = None
            else:
                self.data['last_volume'] = attrs['lastVolume']

            self.data['last_chapter'] = attrs['lastChapter']

            self.data['status'] = attrs['status']
            self.data['content_rating'] = attrs['contentRating']

            for i in rel_ships:
                if i['type'] == 'author':
                    self.data['author'] = i['attributes']['name']
                elif i['type'] == 'artist':
                    self.data['artist'] = i['attributes']['name']
                elif i['type'] == 'cover_art':
                    # this was an attempt to make the url short
                    _all_cdn_url = utils.CDN_URL + self.manga_id + '/covers/'
                    _filename = i['attributes']['fileName']
                    _cover_url = _all_cdn_url + _filename + '.' + str(configs.COVER_SIZE) + '.jpg'
                    self.data['cover_art'] = _cover_url
        else:
            print('failed retrieving manga information')


    def get_volumes(self):
        '''
        This function gets all the volumes with the chapters.
        '''
        _url = utils.MANGA_URL + self.manga_id + '/aggregate?translatedLanguage[]=en'
        _resp = requests.get(_url)
        _vol_list = _resp.json()['volumes']
        self.data['volumes'] = {}

        if _resp.status_code == 200:
            for i in _vol_list:
                vol = Volume(_vol_list[i]['volume'],_vol_list[i]['count'],_vol_list[i]['chapters'])
                self.data['volumes'][i] = vol
        else:
            print('problem requesting chapters!')


    def get_chapter(self, chapter):
        '''
        Returns the chapter dict, with its number, id and count
        '''
        for i in range(len(list(self.data['volumes'].values()))):
            for j in list(self.data['volumes'].values())[i].chapters:
                if j == chapter:
                    return list(self.data['volumes'].values())[i].chapters[j]


    def get_pages(self, chapter):
        '''
        Returns the pages from the chapter requested and the hash to the cdn.
        '''
        chapter_id = self.get_chapter(chapter)['id']
        _resp = requests.get(f'{utils.CHAPTER_URL}{chapter_id}')
        pages = {}
        pages['hash'] = _resp.json()['data']['attributes']['hash']
        pages['filenames'] = []

        for i in _resp.json()['data']['attributes']['data']:
            pages['filenames'].append(i)

        return pages

    def get_page_urls(self, chapter):
        '''
        Return the urls from the pages
        '''
        pages = self.get_pages(chapter)
        pages_url = []

        for i in pages['filenames']:
            pages_url.append(f'{utils.CDN_URL}data/{pages["hash"]}/{i}')

        return pages_url


# test
# manga = Manga('b62659e0-fb91-4cf1-a62f-c4e058f9917a')
# manga.get_info()
# manga.get_volumes()
# print(manga.data['volumes']['3'].volume_num)
# print(manga.data)
# print(manga.get_chapter('3'))
# print(manga.get_page_urls('13'))
# print(manga.data)
