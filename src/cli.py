from downloader import ImageDownloader
from converter import ImageConverter
from manga import Manga
import configs
import shutil
import utils
import sys
import re

HELP_MESSAGE = """
mangli, a cli app to download and convert mangas to pdf from mangadex.org

Usage:

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

    lang_prompt = 'Which language? (write "show" to show all supported languages) (default: en) R: '
    lang_chose = input(lang_prompt)
    while lang_chose == "show":
        if lang_chose == "show":
            print(LANG_MESSAGE)
        lang_chose = input(lang_prompt)
    if lang_chose == "":
        lang_chose = "en"

    regex = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    tmp_id = sys.argv[1]
    try:
        manga_id = re.findall(regex, tmp_id)[0]
    except IndexError:
        print("Please insert a valid manga id!")
        sys.exit(0)

    if len(sys.argv) == 2:
        long_command(lang_chose)

    if len(sys.argv) > 2:
        short_command(lang_chose)


# long command because it's a harder way to download volumes, however,
# it allows to download chapters individually
# user need to provide:
#   command
#   manga-id
def long_command(lang_chose):
    conv_in = input("Convert to pdf (separately, by chapters)? [Y/n] ").lower()
    conv_bool = conv_in == "y" or conv_in == "yes"

    rm_in = ""
    if conv_bool:
        rm_in = input("Remove all images after conversion? [Y/n] ").lower()
    rm_bool = rm_in == "y" or rm_in == "yes"

    manga = Manga(sys.argv[1])
    manga.get_info()
    manga.get_volumes(True, lang=lang_chose)

    down = ImageDownloader(manga)
    conv = ImageConverter(manga)

    active_menu = ""

    def print_info():
        print("--------- ManglUi --------")
        print("-------- Manga info")
        print(f"Id: {manga.data['id']}")
        print(f"Name: {manga.data['title']}")
        print()
        print("(1) Download a volume")
        print("(2) Download a chapter")
        print("(e) Exit")

    def print_volumes():
        print("--------- Download -------")
        print("------- Volumes List")
        for i in list(manga.data["volumes"].values()):
            print(f"({i.volume_num}) Vol. {i.volume_num}")
        print("(e) Return")

    def print_chapters():
        print("--------- Download -------")
        print("------- Chapter list")
        print("--- If some are missing, they may not be available")
        print("--- for the language you chose, check the website")
        for i in range(len(list(manga.data["volumes"].values()))):
            for j in list(manga.data["volumes"].values())[i].chapters:
                chap = list(manga.data["volumes"].values())[i].chapters[j]
                print(f"({chap['chapter']}) Chap. {chap['chapter']}")
        print("(e) Return")

    while True:
        if active_menu == "":
            print_info()
            selected = input("> ")
            # if selected.find('e') != -1:
            if selected == "e":
                validated_title = utils.validate_filename(manga.data["title"])
                full_path = rf"{configs.DOWNLOAD_PATH}/{validated_title}"
                if rm_bool:
                    shutil.rmtree(full_path)
                sys.exit(0)
            elif selected.find("1") != -1:
                active_menu = "down_vol"
            elif selected.find("2") != -1:
                active_menu = "down_chap"
            else:
                continue

        if active_menu == "down_vol":
            print_volumes()
            selected = input("> ")
            # if selected.find('e') != -1 and selected.find('e') < 1:
            if selected == "e":
                active_menu = ""
                continue
            else:
                down.download_volume(selected)
                if conv_bool:
                    conv.convert_volume(selected)

        if active_menu == "down_chap":
            print_chapters()
            selected = input("> ")
            # if selected.find('e') != -1:
            if selected == "e":
                active_menu = ""
                continue
            else:
                down.download_chapter(selected)
                if conv_bool:
                    conv.convert_chapter(selected)


# short command because its the short way to download volumes.
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
