"""Object used to convert chapters, volumes and the full manga to pdf"""
# convert to pdf
import os
import re
from PIL import Image
from natsort import natsorted
from PIL import ImageFile as pilImageFile

from manga import Manga
import configs
import utils

pilImageFile.LOAD_TRUNCATED_IMAGES = True


class ImageConverter:
    """Object used to convert chapters, volumes and the full manga to pdf"""

    def __init__(self, manga: Manga):
        self.manga = manga
        #self.manga.get_info()

        self._converted_images = []

    def _generate_pdf(self, pdf_path):
        print("Converting to pdf...")
        try:
            other_imgs = self._converted_images[1:]
            self._converted_images[0].save(
                pdf_path, save_all=True, append_images=other_imgs
            )
        except IndexError:
            try:
                self._converted_images[0].save(pdf_path)
            except IndexError:
                print("Couldn't convert the manga.")

    def _add_image_to_conversion(self, image_path):
        img_tmp = Image.open(image_path, "r").convert("RGB")
        self._converted_images.append(img_tmp)

    def run_common(self, chap_paths: list, title_flag: str):
        """Converts a list of chapters in one pdf"""
        self._converted_images = []

        old_work_dir = os.getcwd()

        for i in chap_paths:
            os.chdir(i)
            for j in range(len(os.listdir(i))):
                self._add_image_to_conversion(rf"{i}/{str(j + 1)}.png")

        title = utils.validate_filename(self.manga.data["title"])
        path_pdf = rf"{configs.DOWNLOAD_PATH}"# "/{title}"
        if not os.path.exists(path_pdf):
            os.makedirs(path_pdf)

        pdf_file = rf"{path_pdf}/[{title_flag}] {title}.pdf"
        self._generate_pdf(pdf_file)
        print("Pdf located in: " + pdf_file)

        os.chdir(old_work_dir)

    def convert_all(self):
        """Converts the entire manga to pdf (not recommended)"""
        old_work_dir = os.getcwd()
        manga_name = utils.validate_filename(self.manga.data["title"])
        dir_path = rf"{configs.DOWNLOAD_PATH}/{manga_name}"

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
        self.run_common(chapters, "full")

    def convert_volume(self, volume):
        """Convert one volume to pdf (most recommended)"""
        vol_to_search = "vol_" + str(volume)
        manga_name = utils.validate_filename(self.manga.data["title"])
        dir_path = rf"{configs.DOWNLOAD_PATH}/{manga_name}"
        path = os.listdir(dir_path)

        chapters = []

        for vol in path:
            if vol == vol_to_search:
                path_vol = dir_path + "/" + vol
                #chap = 999999
                # for i in os.listdir(path_vol):
                    # num = float(re.findall(r"(?<=chap_)[0-9\.]+", i)[-1])
                    # chap = min(chap, num)
                for i in natsorted(os.listdir(path_vol)):
                    # chap_name = "chap_" + str(chap)
                    chap_name = i
                    chapters.append(rf"{path_vol}/{chap_name}")

                self.run_common(chapters, vol_to_search)

    def convert_volumes_separately(self):
        """Convert all volumes to pdf separately"""
        manga_name = utils.validate_filename(self.manga.data["title"])
        dir_path = rf"{configs.DOWNLOAD_PATH}/{manga_name}"
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

            self.run_common(chapters, vol)

    def convert_chapter(self, chapter):
        """Convert one chapter to pdf"""
        chap_to_search = "chap_" + str(chapter)
        manga_name = utils.validate_filename(self.manga.data["title"])
        dir_path = rf"{configs.DOWNLOAD_PATH}/{manga_name}"
        path = os.listdir(dir_path)
        for vol in path:
            path_vol = dir_path + "/" + vol
            for chap in os.listdir(path_vol):
                if chap == chap_to_search:
                    path_chap = [path_vol + "/" + chap]
                    self.run_common(path_chap, chap_to_search)


# manga = Manga('b62659e0-fb91-4cf1-a62f-c4e058f9917a')
# manga = Manga('c52565c9-d99a-4380-9dc8-67369d448eb7')
# conv = ImageConverter(manga)
# conv.convert_chapter('15')
# conv.convert_volume('3')
# conv.convert_volumes_separately()
# conv.convert_all()
