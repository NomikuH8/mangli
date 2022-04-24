"""
Script to make my life easier
"""

from dataclasses import dataclass


@dataclass
class Volume:
    """Volume object to store chapters."""

    volume_num: str
    chapter_num: int
    chapters: dict

    def __init__(self, volume_num, chapter_num, chapters):
        self.volume_num = volume_num
        self.chapter_num = int(chapter_num)
        self.chapters = chapters
