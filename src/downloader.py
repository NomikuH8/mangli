'''Download images from mangadex.'''
import platform
import configs
import utils
import os

import requests
import aiohttp
import asyncio
import aiofile

class image_downloader():
    def __init__(self, manga: Manga):
        self.manga = manga
        self.manga.get_info()
        self.manga.get_volumes()

    def create_download_directory(self):
        if not os.path.exists(configs.DOWNLOAD_PATH):
            os.makedirs(configs.DOWNLOAD_PATH)

    async def _queue_image(self, chapter):
        self.manga
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(5): # todo: this shit
                url = f'{utils.CDN_URL}/data/{}/{}'
        pass

    async def _download_image(self):
        pass

    def download_one_chapter(self):
        pass

    def download_all_chapters(self):
        pass

    def download_all_volume(self):
        pass
