#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from pathlib import Path

from pdf_file import PDFFile


def main():
    parser = ArgumentParser()
    parser.add_argument("file", type=FileType('rb'))
    args = parser.parse_args()

    pdf = PDFFile(args.file.read())
    if not pdf.validate():
        raise RuntimeWarning("Sign is not valid.")
    pdf.sign(Path.joinpath(Path.home, '.insigne.pem'))
    pdf.save(Path(args.file.name).with_suffix('.signed.pdf'))

if __name__ == "__main__":
    main()
