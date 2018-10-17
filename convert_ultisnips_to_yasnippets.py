# convert UltiSnips (one file) to Yasnippets (one folder with multiple files)

import sys
import os
from pathlib import Path
import re

from collections import namedtuple
UltiSnips_SnippetRecord = namedtuple(
    "UltiSnips_SnippetRecord", "name, key, i, snippet_content")
Yasnippet_SnippetRecord = namedtuple(
    "Yasnippet_SnippetRecord", "name, key, snippet_content")

"""
i means: expand snippet even if the key is not preceded by a whitespace,
e.g. pressing tab (triggering expansion) after 
hellopdv 
would expand to
hello\pdv{}{}
Sadly, there is no such thing as "i" in yasnippet
"""

""" a yasnippet file can look like this:
# -*- mode: snippet -*-
# name: pdv
# key: pdv
# --
\pdv{$1}{$2}
"""

""" an UltiSnips file can look like this (e.g. a part of my tex.snippets):
snippet pdv "pdv"
\pdv{$1}{$2}
endsnippet
                 
snippet dd "dd"
\dd{$1}
endsnippet
"""


def convert_ultisnip_to_yasnip(ultisnip):
    pattern = re.compile(
        r'snippet\s*(.*?)\s*"(.*?)"(.*?)\n(.*?)\nendsnippet', re.DOTALL)
    pattern_tuple = re.match(pattern, ultisnip).group(1, 2, 3, 4)
    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    ultiSnips_SnippetRecord = UltiSnips_SnippetRecord(*pattern_tuple)

    yasnippet_SnippetRecord = Yasnippet_SnippetRecord(
        name=ultiSnips_SnippetRecord.name,
        key=ultiSnips_SnippetRecord.key,
        snippet_content=ultiSnips_SnippetRecord.snippet_content)

    yasnippet_str = ("# -*- mode: snippet -*-" + "\n" +
                     "# name: " + yasnippet_SnippetRecord.name + "\n" +
                     "# key: " + yasnippet_SnippetRecord.key + "\n" +
                     "# --" + "\n" +
                     yasnippet_SnippetRecord.snippet_content)

    return (yasnippet_SnippetRecord.name, yasnippet_str)


def main():
    if len(sys.argv) != 2:
        print(
            "USAGE: python3 convert_ultisnips_to_yasnippets.py [ultisnips-file]")
        exit(1)

    us_filepath = Path(Path.cwd() / Path(sys.argv[1]))

    # read in the whole file as one big string
    with open(str(us_filepath), 'r') as us_file:
        us_file_string = us_file.read()

        # read the individual snippets
        us_pattern = re.compile(r'(snippet.*?endsnippet)', re.DOTALL)
        us_snippets = re.findall(us_pattern, us_file_string)

        filenames_yasnippet_strings_set = set([])

        for ultisnip in us_snippets:
            filenames_yasnippet_strings_set.add(
                convert_ultisnip_to_yasnip(ultisnip))

        # now make a new folder and write them to files
        directory_path = Path(Path.cwd() / "converted")
        while os.path.exists(str(directory_path)):
            print("directory", directory_path, "already exists")
            directory_path = Path(
                input('Enter new directory name to save the files into: '))

            if not os.path.isabs(str(directory_path)):
                directory_path = Path(Path.cwd() / directory_path)

        directory_path.mkdir()

        for filename, yasnippet_str in filenames_yasnippet_strings_set:
            with open(str(Path(directory_path / Path(filename))), "w+") as text_file:
                text_file.write(yasnippet_str)

        print("yasnippets written to", directory_path)


if __name__ == "__main__":
    main()
