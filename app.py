from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

import progressbar
import pymediainfo

from config import ALLOWED_FILETYPES
from formatters import generate_report


class InvalidMediaError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        strn = f"{self.message}"
        return strn

    def __repr__(self):
        return str(self)


class Progress:
    def __init__(self):
        self.video = False
        self.audio = False

    def reset(self):
        self.audio, self.video = False, False

    def complete(self, field):
        setattr(self, field, True)

    def is_complete(self):
        return self.video and self.audio


TitleData = namedtuple("TitleData", "filename")


@dataclass
class MediaData:
    video: pymediainfo.Track
    audio: pymediainfo.Track
    title: TitleData


def filter_filetypes(files):
    return [f for f in files if f.suffix in ALLOWED_FILETYPES]


def validate_data(data):
    missing = []
    if "video" not in data:
        missing.append("video")
    if "audio" not in data:
        missing.append("audio")
    if missing:
        raise InvalidMediaError(
            f"{data['title'].filename} does not contain {', '.join(missing)} data."
        )
    return data


def main(rootdir, recurse=False, output=None):
    if recurse:
        files = filter_filetypes(rootdir.glob("**/*.*"))
    else:
        files = filter_filetypes(rootdir.glob("*.*"))

    progress = Progress()
    infos = []
    with progressbar.ProgressBar(max_value=len(files)) as bar:
        for i, f in enumerate(files):
            mediainfo = pymediainfo.MediaInfo.parse(f)
            progress.reset()
            info = dict()
            info["title"] = TitleData(**{"filename": f})
            for track in mediainfo.tracks:
                if track.track_type == "Audio":
                    info["audio"] = track
                    progress.complete("audio")
                if track.track_type == "Video":
                    info["video"] = track
                    progress.complete("video")
                if progress.is_complete():
                    break

            try:
                info = validate_data(info)
            except InvalidMediaError as e:
                print()
                print(f"SKIPPING FILE: {e}")
                continue
            infos.append(MediaData(**info))
            bar.update(i)
    print("")
    data = generate_report(infos)
    if output and type(data) is str:
        output = Path(output)
        if output.is_dir():
            output.mkdir(parents=True, exist_ok=True)
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf8") as f:
            f.write(data)


if __name__ == "__main__":
    main()
