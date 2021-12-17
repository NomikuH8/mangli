'''Utilities for the app'''
import subprocess
import platform
import os

def start_image_app(filepath):
    '''Starts the default image app to show the manga'''
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

SITE_URL = 'https://mangadex.org/'
CDN_URL = 'https://uploads.mangadex.org/'
API_URL = 'https://api.mangadex.org/'

MANGA_URL = API_URL + 'manga/'
CHAPTER_URL = API_URL + 'chapter/'
