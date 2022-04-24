from downloader import ImageDownloader
from converter import ImageConverter
from manga import Manga
import configs
import shutil
import utils
import sys

HELP_MESSAGE = """
Usage:
    mangli, a cli app to download and convert mangas to pdf from mangadex.org

    mangli <manga-id> <volumes...>
    ex.: mangli a96676e5-8ae2-425e-b549-7f15dd34a6d8 1 4 6-8 none

    arguments:
        manga-id: manga id, you can take it in them manga page
            example: a96676e5-8ae2-425e-b549-7f15dd34a6d8

        volumes: single numbers for single volumes. 1-4 for 1, 2, 3, 4 volumes
            note: can be "none"
                none: chapters without a volume
            example: none 1 4 6-8
"""

LANG_MESSAGE = """
Language can be:
    vi uk tr th sv es-la es sr ru ro pt-br pt pl fa no
    ne mn ms lt la it id hu hi he el de fr fi tl et nl
    da cs hr ca my bg bn ar en zh-hk zh ko ja
"""


def run():
    if len(sys.argv) < 2:
        print(HELP_MESSAGE)
        sys.exit(0)

    lang_prompt = 'Which language? (write "show" to show all supported languages) R: '
    lang_chose = input(lang_prompt)
    while lang_chose == "show":
        if lang_chose == "show":
            print(LANG_MESSAGE)
        lang_chose = input(lang_prompt)
    if lang_chose == "": lang_chose = "en"
    
    if len(sys.argv) == 2:
        long_command(lang_chose)
    
    if len(sys.argv) > 2:
        short_command(lang_chose)

def long_command(lang_chose):
    pass

# short command because its the short way to download volumes
# user need to provide:
#   command
#   manga-id
#   volumes
def short_command(lang_chose):
    conv_in = input("Convert all to pdf? [Y/n] ").lower()
    conv_bool = conv_in == "y" or conv_in == "yes"

    rm_in = ""
    if conv_bool:
        rm_in = input("Remove all images after? [Y/n] ").lower()
    rm_bool = rm_in == "y" or rm_in == "yes"

    manga = Manga(sys.argv[1])
    manga.get_info()
    manga.get_volumes(True, lang=lang_chose)

    print("Available chapters:")
    for i in sys.argv[2:]:
        hifen = i.find("-")
        if hifen != -1:
            start = i[:hifen]
            stop = i[hifen + 1 :]
            for j in range(int(start), int(stop) + 1, 1):
                print("\nVol " + str(j) + ":")
                try:
                    manga.data["volumes"][str(j)]
                except KeyError:
                    print("  No chapters available")
                for volume in list(manga.data["volumes"].values()):
                    if str(j) == volume.volume_num:
                        chap_list = list(volume.chapters.keys())
                        chap_list.reverse()
                        for k in chap_list:
                            print("  Chap " + k)
        else:
            print("\nVol " + str(i) + ":")
            try:
                manga.data["volumes"][str(i)]
            except KeyError:
                print("  No chapters available")
            for volume in list(manga.data["volumes"].values()):
                if str(i) == volume.volume_num:
                    chap_list = list(volume.chapters.keys())
                    chap_list.reverse()
                    for k in chap_list:
                        print("  Chap " + k)

    print("\nAlways check if all the chapters you want are there!")
    proceed_in = input("Proceed to download? [Y/n] ").lower()
    if proceed_in != "y" and proceed_in != "yes":
        sys.exit(0)

    down = ImageDownloader(manga)
    conv = ImageConverter(manga)

    for i in sys.argv[2:]:
        hifen = i.find("-")
        if hifen != -1:
            start = i[:hifen]
            stop = i[hifen + 1 :]
            for j in range(int(start), int(stop) + 1, 1):
                print("\nDownloading vol: " + str(j))
                down.download_volume(j)
                if conv_bool:
                    print("Converting vol: " + str(j))
                    conv.convert_volume(j)
        else:
            print("\nDownloading vol: " + i)
            down.download_volume(i)
            if conv_bool:
                print("Converting vol: " + i)
                conv.convert_volume(i)

    validated_title = utils.validate_filename(manga.data["title"])
    full_path = rf"{configs.DOWNLOAD_PATH}/{validated_title}"
    if rm_bool:
        shutil.rmtree(full_path)


if __name__ == "__main__":
    run()
