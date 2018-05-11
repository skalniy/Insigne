import base64


def main():
    with open('./testPDF_Version.6.x.pdf', mode='rb') as f:
        data = f.read()

    eof_pos = data.rfind(b'%%EOF')
    if eof_pos < 0:
        print("error: EOF not found")
        return None

    startxref_pos = data.rfind(b'startxref', 0, eof_pos)
    if startxref_pos < 0:
        print("error: startxref not found")
        return None

    trailer_pos = data.rfind(b'trailer', 0, startxref_pos)
    # print("DEBUG:{0}:trailer".format(trailer_pos))
    if trailer_pos <= 0:
        print("info: trailer not found\ninserting before startxref")

    to_insert_pos = trailer_pos if trailer_pos > 0 else startxref_pos
    data_to_insert = base64.standard_b64encode(b'Hello, PDF!') + b'\n'

    with open('./signed.pdf', mode='wb') as f:
        f.write(data[:to_insert_pos])
        f.write(data_to_insert)
        f.write(data[to_insert_pos:])


if __name__ == "__main__":
    main()
