from pdf_file import PDFFile

def main():
    pdf = PDFFile.open('./testPDF_Version.6.x.pdf')
    pdf.sign('./key1.txt', './key2.txt')
    pdf.sign('./key1.txt', './key2.txt')
    pdf.sign('./key1.txt', './key2.txt')
    pdf.save('./signed.pdf')
    pdf2 = PDFFile.open('./signed.pdf')
    print(pdf2.validate())

if __name__ == "__main__":
    main()
