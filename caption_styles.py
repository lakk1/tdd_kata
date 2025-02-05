from typing import List
from dataclasses import dataclass
from moviepy.editor import TextClip


@dataclass
class Word:
    text: str
    start: float
    end: float


# Style constants
DEFAULT_TEXT_COLOR = "white"
HIGHLIGHT_TEXT_COLOR = "black"
HIGHLIGHT_BG_COLOR = "white"
WORD_PADDING = 10  # Pixels of padding around words


class CaptionStyle:
    def __init__(self, font: str, font_size: int, width: int):
        self.font = font
        self.font_size = font_size
        self.width = width


class HighlightedCaptionStyle(CaptionStyle):
    def __init__(self, font: str, font_size: int, width: int):
        super().__init__(font, font_size, width)

    def create_word_clips(self, words: List[Word]) -> List[TextClip]:
        clips = []
        for word in words:
            # Highlighted version (active word)
            highlighted = (
                TextClip(
                    f" {word.text} ",  # Add spacing for padding
                    font=self.font,
                    fontsize=self.font_size,
                    color=HIGHLIGHT_TEXT_COLOR,
                    bg_color=HIGHLIGHT_BG_COLOR,
                    size=(None, None),
                    method="label",
                    stroke_color=HIGHLIGHT_BG_COLOR,
                    stroke_width=WORD_PADDING,
                )
                .set_position(("center", "center"))
                .set_start(word.start)
                .set_end(word.end)
            )

            # Non-highlighted version (inactive word)
            normal = (
                TextClip(
                    f" {word.text} ",
                    font=self.font,
                    fontsize=self.font_size,
                    color=DEFAULT_TEXT_COLOR,
                    size=(None, None),
                    method="label",
                )
                .set_position(("center", "center"))
                .set_start(word.end)
                .set_duration(0.1)
            )

            clips.extend([highlighted, normal])
        return clips


def get_word_timing(text: str, start: float, end: float) -> List[Word]:
    """Split caption into words with estimated timing"""
    words = text.split()
    word_duration = (end - start) / len(words)

    result = []
    current_time = start
    for word in words:
        result.append(
            Word(text=word, start=current_time, end=current_time + word_duration)
        )
        current_time += word_duration
    return result
