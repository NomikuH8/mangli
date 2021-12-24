# script that controls menus
#
# directions
#	main
#		main_feed
#			manga_page
#		search
#			results
#				manga_page
#		url
#			manga_page
#
#	manga_page:
#		read
#       see cover
#		download all volumes - may take a lot of time
from __future__ import print_function, unicode_literals

from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
import requests
import sys
import os

from cache_downloader import ImageDownloader
from searcher import MangaSearcher
from manga import Manga
import configs
import utils

class Mangli():
    def __init__(self):
        self.searcher = MangaSearcher()
        #self.downn = ImageDownloader()

    def clear_term(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def main(self):
        self.clear_term()
        questions = [
            {
                'type': 'list',
                'name': 'entry',
                'message': 'Welcome to Mangli!',
                'choices': [
                    'Homepage',
                    'Search',
                    'Specify a url',
                    'Exit Mangli'
                ]
            }
        ]

        answer = prompt(questions)

        while len(answer) == 0:
            try:
                self.clear_term()
                answer = prompt(questions)
            except KeyboardInterrupt:
                sys.exit(0)

        if answer['entry'] == 'Homepage': self.homepage(0)
        if answer['entry'] == 'Search': self.search()
        if answer['entry'] == 'Specify a url': pass
        if answer['entry'] == 'Exit Mangli': sys.exit(0)

    def homepage(self, page):
        self.clear_term()
        control = []
        mangas = self.searcher.get_homepage(10, page)

        control.append('Exit home')
        control.append('Next page')
        if page > 0:
            control.append('Previous page')
        control.append(Separator())
        control.append(Separator(f'--- Page: {page + 1} ---'))
        control.append(Separator())

        for i in mangas:
            control.append(i['title'])
        questions = [
            {
                'type': 'list',
                'name': 'home',
                'message': 'Mangadex.org Homepage',
                'choices': control,
                'default': 'Next page'
            }
        ]
        answer = prompt(questions)

        while len(answer) == 0:
            try:
                self.clear_term()
                answer = prompt(questions)
            except KeyboardInterrupt:
                sys.exit(0)

        if answer['home'] == 'Next page':
            self.homepage(page + 1)
        if answer['home'] == 'Previous page':
            self.homepage(page - 1)
        if answer['home'] == 'Exit home':
            self.main()

        for i in mangas:
            if answer['home'] == i['title']:
                self.manga_page(i['id'], lambda: self.homepage(page))


    def search(self):
        pass


    def manga_page(self, manga_id, return_to_func, manga={}):
        self.clear_term()
        manga = {}
        if len(manga) == 0:
            manga = self.searcher.take_manga_page(manga_id)

        choices = []
        choices.append(Separator('Information:'))
        choices.append(Separator('  Title: ' + manga['title']))
        choices.append(Separator('  Alt titles:'))
        for i in manga['alt_titles']:
            choices.append(Separator('    ' + list(i.values())[0]))
        choices.append(Separator('  Author: ' + manga['author']))
        choices.append(Separator('  Artist: ' + manga['artist']))
        #choices.append(Separator('Description: ' + manga['description']))
        choices.append(Separator('  Original language: ' + manga['original_lang']))
        choices.append(Separator('  Content rating: ' + manga['content_rating']))
        choices.append(Separator('  Status: ' + manga['status']))
        if manga['status'] == 'Completed':
            choices.append(Separator('  Last chapter: ' + manga['last_chapter']))
        else:
            choices.append(Separator('  Last chapter: not yet available'))

        choices.append(Separator())
        choices.append('Show cover')
        if len(manga['volumes']) == 0:
            choices.append(Separator("--- Couldn't take any chapter :("))
        else:
            choices.append('Read')
            choices.append('Download')

        manga_title = utils.validate_filename(manga["title"])
        manga_path = fr'{configs.DOWNLOAD_PATH}/mangas/{manga_title}'
        if os.path.exists(manga_path):
            choices.append(Separator())
            choices.append('Convert to pdf')
            choices.append('Zip the manga')

        choices.append(Separator())
        choices.append('Return')

        questions = [
            {
                'type': 'list',
                'name': 'manpage',
                'message': manga['title'],
                'choices': choices
            }
        ]

        answer = {}
        while len(answer) == 0:
            self.clear_term()
            try:
                answer = prompt(questions)
            except:
                self.manga_page(manga['id'], return_to_func, manga)

            cache_path = fr'{configs.DOWNLOAD_PATH}/.cache'
            cover_path = fr'{cache_path}/[cover] {manga_title}.png'
            if len(answer) != 0:
                if answer['manpage'] == 'Show cover':
                    if not os.path.exists(cache_path):
                        os.makedirs(cache_path)
                    if not os.path.exists(cover_path):
                        with open(cover_path, 'wb') as file:
                            print('Downloading cover...')
                            resp = requests.get(manga['cover_art'])
                            if resp.status_code == 200:
                                file.write(resp.content)
                                utils.start_image_app(cover_path)
                            else:
                                os.remove(cover_path)
                                print("Couldn't download cover")
                                print(resp.status_code)
                    else:
                        utils.start_image_app(cover_path)
                    self.manga_page(manga['id'], return_to_func, manga)
                if answer['manpage'] == 'Read': self.vol_read_menu(manga, return_to_func)

                if answer['manpage'] == 'Return':
                    return_to_func()
        self.manga_page(manga['id'], return_to_func, manga)


    def vol_read_menu(self, manga, page_return):
        self.clear_term()
        choices = []
        choices.append(Separator('--- Some volumes may not be in english, ok?'))
        choices.append(Separator('--- And please put your image viewer to sort by name'))
        choices.append(Separator('--- Volumes ---'))
        chap_num = 1
        for i in manga['volumes'].values():
            min_chap = chap_num
            chap_num += i.chapter_num
            choices.append(f'Volume {i.volume_num} ({min_chap}-{chap_num})')
        choices.append('Return')

        questions = [
            {
                'type': 'list',
                'name': 'volume',
                'message': manga['title'],
                'choices': choices
            }
        ]

        answer = {}
        while len(answer) == 0:
            self.clear_term()
            answer = prompt(questions)

        if answer['volume'] == 'Return': self.manga_page(manga['id'], page_return, manga)

        chap_num = 1
        for i in manga['volumes'].values():
            min_chap = chap_num
            chap_num += i.chapter_num
            if answer['volume'] == f'Volume {i.volume_num} ({min_chap}-{chap_num})':
                self.chap_read_menu(i, manga, page_return)

    def chap_read_menu(self, sel_vol, manga, page_return):
        self.clear_term()
        choices = [Separator('--- Chapter ---')]
        for i in sel_vol.chapters.keys():
            choices.append(i)
        choices.append(Separator())
        choices.append('Return')

        questions = [
            {
                'type': 'list',
                'name': 'chapter',
                'message': manga['title'],
                'choices': choices
            }
        ]

        answer = {}
        while len(answer) == 0:
            self.clear_term()
            answer = prompt(questions)

        if answer['chapter'] == 'Return': self.vol_read_menu(manga, page_return)

        for i in sel_vol.chapters.keys():
            if answer['chapter'] == i:
                manga_obj = Manga(manga['id'])
                manga_obj.data = manga
                downn = ImageDownloader(manga_obj)
                downn.download_chapter(i)
                validated_title = utils.validate_filename(manga['title'])
                cache_path = fr'{configs.DOWNLOAD_PATH}/.cache/'
                volume_num = sel_vol.volume_num
                first_page_path = fr'{cache_path}{validated_title}/vol_{volume_num}/chap_{i}/1.png'
                utils.start_image_app(first_page_path)
                self.manga_page(manga['id'], page_return, manga)



a = Mangli()
a.main()
