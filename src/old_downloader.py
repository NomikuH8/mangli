'''Download images from mangadex.'''

import os
import asyncio
import aiofile
import aiohttp

import configs
from manga import Manga


class ImageDownloader():
    '''
    This class downloads all images from a volume, chapter or manga.
    '''
    def __init__(self, manga: Manga):
        self.manga = manga
        self.manga.get_info()
        self.manga.get_volumes()

        self.image_paths = []
        self.full_path = ''
        self._el = None


    def create_download_directory(self):
        '''
        Creates the directory for download.
        '''
        validated_title = self._validate_filename(self.manga.data['title'])
        self.full_path = fr'{configs.DOWNLOAD_PATH}/{validated_title}'
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)


    def create_volume_directory(self, volume):
        '''
        Creates the directory for volume.
        '''
        tmp_path = self.full_path
        tmp_path = fr'{self.full_path}/vol_{str(volume)}'
        self.full_path = tmp_path
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)


    def create_chapter_directory(self, chapter):
        '''
        Creates the directory for chapter.
        '''
        tmp_path = self.full_path
        tmp_path = fr'{self.full_path}/chap_{str(chapter)}'
        self.full_path = tmp_path
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)


    def _set_image_path(self, image, array):
        in_png = configs.IN_PNG
        ext = 'png' if in_png else 'jpg'

        image_path = fr'{self.full_path}/{str(array.index(image) + 1)}.{ext}'
        self.image_paths.append(image_path)


    def _validate_filename(self, text):
        '''
        Some manga titles have these characters, this could create some
        problems while placing the images in a path.
        '''
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        new_text = text

        for char in invalid_chars:
            new_text_tmp = new_text.replace(char, '')
            new_text = new_text_tmp

        return new_text


    async def queue_image(self, chapter):
        async with aiohttp.ClientSession() as session:
            tasks = []
            urls = self.manga.get_page_urls(chapter)

            multiplier = configs.DOWNREQ_TIME
            time_wait = 1

            for url in urls:
                # added wait because it was a mess
                time_wait = multiplier * urls.index(url)
                self._set_image_path(url, urls)
                task = asyncio.ensure_future(self._download_image(session, url, urls, 1, time_wait))
                tasks.append(task)

            status = await asyncio.gather(*tasks)


    async def _download_image(self, session, url, url_arr, time_tested=1, time_to_wait=1):
        try:
            async with session.get(url) as _resp:
                # print(f'Downloading page: {url_arr.index(url) + 1}/{len(url_arr)}')
                # print(url + 'aaaaaaaaaaaaaaaaaaaaaa' + str(_resp.status))
                await asyncio.sleep(time_to_wait)
                if _resp.status == 200:
                    async with aiofile.async_open(self.image_paths[url_arr.index(url)], 'wb') as file:
                        await file.write(await _resp.read())
                else:
                    if time_tested < 3:
                        # print(f'Problem downloading page {url_arr.index(url) + 1}, retrying...')
                        return await self._download_image(session, url, url_arr, time_tested + 1)
                    # else:
                        # print(f"Couldn't download page {url_arr.index(url) + 1}")
        except:
            #print('problem here, retrying')
            return await self._download_image(session, url, url_arr, time_tested)


    def run(self, volume, chapter):
        self.create_download_directory()
        self.create_volume_directory(volume)
        self.create_chapter_directory(chapter)
        self._el = asyncio.get_event_loop()
        self._el.run_until_complete(self.queue_image(chapter))


class DownloadManager():
    '''Download manager because 1 image downloader can download something once only'''
    def __init__(self, manga: Manga):
        self.manga = manga
        self.manga.get_volumes()


    def download_all_volumes(self):
        '''Downloads all volumes'''
        print('Downloading everything...')
        for i in self.manga.data['volumes'].values():
            for j in i.chapters:
                downn = ImageDownloader(self.manga)
                downn.run(i.volume_num, j)


    def download_volume(self, volume):
        '''Downloads a volume'''
        vol_to_down = self.manga.data['volumes'][str(volume)].chapters
        for i in vol_to_down.values():
            print('Downloading chapter ' + i['chapter'] + '...')
            downn = ImageDownloader(self.manga)
            downn.run(volume, i['chapter'])


    def download_chapter(self, chapter):
        '''Downloads one chapter.'''
        print('Downloading chapter ' + chapter + '...')
        for i in self.manga.data['volumes'].values():
            for j in i.chapters:
                if j == chapter:
                    downn = ImageDownloader(self.manga)
                    downn.run(i.volume_num, j)


manga = Manga('b62659e0-fb91-4cf1-a62f-c4e058f9917a')
dm = DownloadManager(manga)
#dm.download_volume('1')
#dm.download_chapter('3')
dm.download_all_volumes()
