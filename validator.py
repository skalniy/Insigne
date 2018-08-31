from argparse import ArgumentParser, FileType
from pathlib import Path

from pdf_file import PDFFile


def main():
    parser = ArgumentParser()
    parser.add_argument("file", type=FileType('rb'))
    args = parser.parse_args()

    pdf = PDFFile(args.file.read())
    print(pdf.validate())

if __name__ == "__main__":
    main()
