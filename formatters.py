from abc import ABC, abstractmethod
from dataclasses import asdict
from functools import reduce

from prettytable import PrettyTable

from config import ALLOWED_FILETYPES, DEFAULT_FORMATTER
from utils import merge_arrays


class FormatterForPrettyTable:
    fields = dict()

    def __init__(self, data):
        self.data = data

    @classmethod
    def get_field_aliases(cls):
        return list(cls.fields.values())

    @property
    def field_names(self):
        return self.fields.keys()

    def make(self):
        res = []
        for field in self.field_names:
            f = getattr(self, f"do_{field}", self.default)
            res.append(f())
        return res

    def default(self):
        return ""


class AudioFormatter(FormatterForPrettyTable):
    fields = {
        "bit_rate": "Bit Rate",
        "channels": "Channels",
    }

    def do_bit_rate(self):
        return f"{self.data.bit_rate:,}"

    def do_channels(self):
        count = self.data.channel_s
        layout = self.data.channel_layout
        if not layout:
            return f"{count}"
        layout = layout.replace(" ", ",")
        return f"{count} {layout}"


class VideoFormatter(FormatterForPrettyTable):
    fields = {
        "frame_rate": "FR",
        "codec": "Codec",
        "dimensions": "Dimensions",
    }

    def do_frame_rate(self):
        fr = self.data.frame_rate
        return f"{fr}"

    def do_codec(self):
        format = self.data.format
        libname = self.data.encoded_library_name
        return f"{format} - {libname}"

    def do_dimensions(self):
        width, height = self.data.width, self.data.height
        dim = f"{width} x {height}"
        ar = self.data.display_aspect_ratio
        ar = f"@ {ar}" if ar else ""
        return " ".join([dim, ar])


class TitleFormatter(FormatterForPrettyTable):
    fields = {
        "filename": "Filename",
    }

    def do_filename(self):
        return str(self.data.filename.name)


def make_row(info):
    formatters = (
        TitleFormatter,
        VideoFormatter,
        AudioFormatter,
    )
    data = (info.title, info.video, info.audio)
    return merge_arrays(f(d).make() for f, d in zip(formatters, data))


def make_table_data(infos):
    formatters = (TitleFormatter, VideoFormatter, AudioFormatter)
    data = dict()
    data["field_names"] = reduce(
        lambda acc, formatter: acc + formatter.get_field_aliases(), formatters, []
    )
    res = []
    for info in infos:
        res.append(make_row(info))
        data["rows"] = res
    return data


def make_table(infos):
    table_data = make_table_data(infos)
    table = PrettyTable()
    table.field_names = table_data["field_names"]
    table.align["Filename"] = "l"
    for row in table_data["rows"]:
        table.add_row(row)
    return table


def generate_pretty_table_report(infos):
    table = make_table(infos)
    print(table)
    return table


def do_empty_report():
    print(f"The provided directory did not contain any file with allowed file types.")
    print(f"Allowed file types are: {', '.join(ALLOWED_FILETYPES)}")


def generate_report(infos):
    if not infos:
        do_empty_report()
        return
    formatters = {
        "prettytable": generate_pretty_table_report,
    }
    return str(formatters[DEFAULT_FORMATTER](infos))


if __name__ == "__main__":
    main()
