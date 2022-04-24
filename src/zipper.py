"""Zipper object"""
import zipfile
import re
import os

from manga import Manga
import configs
import utils


class ImageZipper:
    """Object to zip mangas. Accept volume, volumes(separately), chapters and the full manga"""

    def __init__(self, manga: Manga):
        self.manga = manga
        self.manga.get_info()

    def run_common(self, path_to_zip, title_flag: str):
        """Zips a list of chapters"""
        old_work_dir = os.getcwd()
        os.chdir(path_to_zip)

        title = utils.validate_filename(self.manga.data["title"])
        path_zip = rf"{configs.DOWNLOAD_PATH}/zips/{title}"
        if not os.path.exists(path_zip):
            os.makedirs(path_zip)

        zip_file = rf"{path_zip}/[{title_flag}] {title}.zip"
        # test compressed modes: ZIP_DEFLATED, ZIP_BZIP2, ZIP_LZMA
        # best: ZIP_DEFLATED, others too slow and no compression
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zip_f:
            for (root, dirs, files) in os.walk("."):
                zip_f.write(root, os.path.relpath(root, path_to_zip))
                for file in files:
                    zip_f.write(
                        os.path.join(root, file),
                        os.path.join(os.path.relpath(root, path_to_zip), file),
                    )

        print("Zip located in: " + path_zip)

        os.chdir(old_work_dir)

    def zip_all(self):
        """Zips the entire manga"""
        old_work_dir = os.getcwd()
        manga_name = utils.validate_filename(self.manga.data["title"])
        dir_path = rf"{configs.DOWNLOAD_PATH}/mangas/{manga_name}"

        os.chdir(dir_path)
        volumes = os.listdir(".")
        chapters = []

        chap = 0
        for vol in range(len(volumes)):
            vol_name = "vol_" + str(vol + 1)
            for i in os.listdir(vol_name):
                chap_name = "chap_" + str(chap + 1)
                chapters.append(rf"{dir_path}/{vol_name}/{chap_name}")
                chap += 1

        os.chdir(old_work_dir)
        self.run_common(dir_path, "full")

    def zip_volume(self, volume):
        """Zips one volume"""
        vol_to_search = "vol_" + str(volume)
        manga_name = utils.validate_filename(self.manga.data["title"])
        dir_path = rf"{configs.DOWNLOAD_PATH}/mangas/{manga_name}"
        path = os.listdir(dir_path)

        for vol in path:
            if vol == vol_to_search:
                path_vol = dir_path + "/" + vol
                self.run_common(path_vol, vol_to_search)

    def zip_volumes_separately(self):
        """Zips all volumes separately"""
        manga_name = utils.validate_filename(self.manga.data["title"])
        dir_path = rf"{configs.DOWNLOAD_PATH}/mangas/{manga_name}"
        path = os.listdir(dir_path)

        chapters = []

        for vol in path:
            chapters = []
            path_vol = dir_path + "/" + vol
            chap = 999999
            for i in os.listdir(path_vol):
                num = int(re.findall(r"(?<=chap_)\d+", i)[-1])
                chap = min(chap, num)
            for i in os.listdir(path_vol):
                chap_name = "chap_" + str(chap)
                chapters.append(rf"{path_vol}/{chap_name}")
                chap += 1

            self.run_common(path_vol, vol)

    def zip_chapter(self, chapter):
        """Zips one chapter"""
        chap_to_search = "chap_" + str(chapter)
        manga_name = utils.validate_filename(self.manga.data["title"])
        dir_path = rf"{configs.DOWNLOAD_PATH}/mangas/{manga_name}"
        path = os.listdir(dir_path)
        for vol in path:
            path_vol = dir_path + "/" + vol
            for chap in os.listdir(path_vol):
                if chap == chap_to_search:
                    path_chap = path_vol + "/" + chap
                    self.run_common(path_chap, chap_to_search)


# manga = Manga('b62659e0-fb91-4cf1-a62f-c4e058f9917a')
# iz = ImageZipper(manga)
# iz.zip_volumes_separately()
# iz.zip_chapter('13')
# iz.zip_volume('2')
# iz.zip_all()
