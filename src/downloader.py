"""Download images from mangadex."""

import os
import asyncio
import aiofile
import aiohttp

from manga import Manga
import configs
import utils


class ImageDownloader:
    """
    This class downloads all images from a volume, chapter or manga.
    """

    def __init__(self, manga: Manga):
        self.manga = manga
        # self.manga.get_info()
        # self.manga.get_volumes()

        self.image_paths = []
        self.full_path = ""
        self._el = None

    def create_download_directory(self):
        """
        Creates the directory for download.
        """
        validated_title = utils.validate_filename(self.manga.data["title"])
        self.full_path = rf"{configs.DOWNLOAD_PATH}/{validated_title}"
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)

    def create_volume_directory(self, volume):
        """
        Creates the directory for volume.
        """
        tmp_path = self.full_path
        tmp_path = rf"{self.full_path}/vol_{str(volume)}"
        self.full_path = tmp_path
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)

    def create_chapter_directory(self, chapter):
        """
        Creates the directory for chapter.
        """
        tmp_path = self.full_path
        tmp_path = rf"{self.full_path}/chap_{str(chapter)}"
        self.full_path = tmp_path
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)

    def _set_image_path(self, image, array):
        image_path = rf"{self.full_path}/{str(array.index(image) + 1)}.png"
        self.image_paths.append(image_path)

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
                if os.path.exists(self.image_paths[urls.index(url)]):
                    continue
                task = asyncio.ensure_future(
                    self._download_image(session, url, urls, 1, time_wait)
                )
                tasks.append(task)

            status = await asyncio.gather(*tasks)

    async def _download_image(
        self, session, url, url_arr, time_tested=1, time_to_wait=1
    ):
        try:
            await asyncio.sleep(time_to_wait)
            async with session.get(url) as _resp:
                if _resp.status == 200:
                    async with aiofile.async_open(
                        self.image_paths[url_arr.index(url)], "wb"
                    ) as file:
                        await file.write(await _resp.read())
                else:
                    if time_tested < 3:
                        # print(f'Problem downloading page {url_arr.index(url) + 1}, retrying...')
                        return await self._download_image(
                            session, url, url_arr, time_tested + 1
                        )
                    # else:
                    # print(f"Couldn't download page {url_arr.index(url) + 1}")
        except:
            # print('problem here, retrying')
            return await self._download_image(session, url, url_arr, time_tested)

    def run(self, volume, chapter):
        """Runs the download"""
        self.image_paths = []
        self.create_download_directory()
        self.create_volume_directory(volume)
        self.create_chapter_directory(chapter)
        self._el = asyncio.get_event_loop()
        self._el.run_until_complete(self.queue_image(chapter))

    def download_all_volumes(self):
        """Downloads all volumes"""
        print("Downloading everything...")
        for i in self.manga.data["volumes"].values():
            for j in i.chapters:
                self.run(i.volume_num, j)

    def download_volume(self, volume):
        """Downloads a volume"""
        vol_to_down = ""
        try:
            vol_to_down = self.manga.data["volumes"][str(volume)].chapters
            for i in vol_to_down.values():
                print("Downloading chapter " + i["chapter"] + "...")
                self.run(volume, i["chapter"])
        except KeyError:
            print(f"Volume {volume} doesn't exist")

    def download_chapter(self, chapter):
        """Downloads one chapter."""
        print("Downloading chapter " + chapter + "...")
        found = False

        vol_list = list(self.manga.data["volumes"].values())
        vol_list.reverse()

        for i in vol_list:
            for j in i.chapters:
                if j == chapter:
                    found = True
                    self.run(i.volume_num, j)
                    return
        if not found:
            print(f"Chapter {chapter} not found!")


# manga = Manga('b62659e0-fb91-4cf1-a62f-c4e058f9917a')
# manga = Manga('c52565c9-d99a-4380-9dc8-67369d448eb7')
# downloader = ImageDownloader(manga)
# downloader.download_volume('1')
# downloader.download_chapter('3')
# downloader.download_all_volumes()
