from downloader import ImageDownloader
from converter import ImageConverter
from manga import Manga
import configs
import shutil
import utils
import sys

HELP_MESSAGE = """
Usage:
    mangli <manga-id> <volumes...>
    ex.: mangli a96676e5-8ae2-425e-b549-7f15dd34a6d8 1 4 6-8 none
    ex.: mangli a96676e5-8ae2-425e-b549-7f15dd34a6d8 all

    arguments:
        manga-id: manga id, you can take it in them manga page
            example: a96676e5-8ae2-425e-b549-7f15dd34a6d8
        
        volumes: single numbers for single volumes. 1-4 for 1, 2, 3, 4 volumes
            note: can be "none" or "all"
                none: chapters without a volume
                all: all volumes, use alone
            example: 1 4 6-8 none
"""

def run():
    if len(sys.argv) < 3:
        print(HELP_MESSAGE)
        sys.exit(0)
        
    conv_in = input("Convert all to pdf? [Y/n] ")
    conv_bool = conv_in == 'y' or conv_in == 'Y'

    rm_in = ""
    if conv_bool:
        rm_in = input("Remove all images after? [Y/n] ")
    rm_bool = rm_in == 'y' or rm_in == 'Y'

    manga = Manga(sys.argv[1])
    manga.get_info()
    manga.get_volumes(True)

    availableVolumes = ''
    for i in list(manga.data["volumes"].keys()):
        availableVolumes +=  i + ', ' if i != len(manga.data["volumes"]) - 1 else i + '.'
    print('Available volumes in the selected language: ' + availableVolumes)

    down = ImageDownloader(manga)
    conv = ImageConverter(manga)

    for i in sys.argv[2:]:
        hifen = i.find('-')
        if hifen != -1:
            start = i[:hifen]
            stop = i[hifen + 1:]
            for j in range(int(start), int(stop) + 1, 1):
                print('downloading: ' + str(j))
                down.download_volume(j)
                if conv_bool:
                    print('converting: ' + str(j))
                    conv.convert_volume(j)
        else:
            print('downloading: ' + i)
            down.download_volume(i)
            if conv_bool:
                print('converting: ' + i)
                conv.convert_volume(i)

    validated_title = utils.validate_filename(manga.data["title"])
    full_path = rf"{configs.DOWNLOAD_PATH}/{validated_title}"
    if rm_bool:
        shutil.rmtree(full_path)


if __name__ == "__main__":
    run()
