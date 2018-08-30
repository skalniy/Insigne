from argparse import ArgumentParser, FileType

from pdf_file import PDFFile


def main():
    parser = ArgumentParser()
    parser.add_argument("file", type=FileType('rb'))
    parser.add_argument("-o", "--output", help="outputfile", action="store_true")
    parser.add_argument("-s", "--sign", type=FileType('wb'))
    args = parser.parse_args()

    pdf = PDFFile(args.file.read())
    if args.sign:
        pdf.sign('./key1.txt')
        pdf.sign('./key1.txt')
        pdf.sign('./key1.txt')
        pdf.save(args.sign)
    else:
        print(pdf.validate())

if __name__ == "__main__":
    main()
