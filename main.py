from argparse import ArgumentParser, FileType
from pathlib import Path

from pdf_file import PDFFile


def main():
    parser = ArgumentParser()
    parser.add_argument("file", type=FileType('rb'))
    parser.add_argument("-s", "--sign", action="store_true")
    args = parser.parse_args()

    pdf = PDFFile(args.file.read())
    if args.sign:
        if not pdf.validate():
            raise RuntimeWarning("Sign is not valid.")
        pdf.sign('./key1.txt')
        pdf.sign('./key1.txt')
        pdf.sign('./key1.txt')
        pdf.save(Path(args.file.name).with_suffix('.signed.pdf'))
    else:
        print(pdf.validate())

if __name__ == "__main__":
    main()
