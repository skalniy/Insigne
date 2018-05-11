import base64


def find_trailer_end(data):
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
        print("info: trailer not found")

    return trailer_pos if trailer_pos > 0 else startxref_pos


def insert(fname, payload):
    with open(fname, mode='rb') as f:
        data = f.read()

    insert_pos = find_trailer_end(data)
    data_to_insert = base64.standard_b64encode(payload)

    with open('./signed.pdf', mode='wb') as f:
        f.write(data[:insert_pos])
        f.write(data_to_insert + b'\n' + \
                bytes(str(len(data_to_insert)), 'utf-8') + b'\n')
        f.write(data[insert_pos:])


def extract():
    with open('./signed.pdf', mode='rb') as f:
        data = f.read()

    # expected payload position
    end_pos = find_trailer_end(data) - 1

    # position of separator between len and data
    len_sep_pos = data.rfind(b'\n', 0, end_pos)

    # data len
    len_str = int(data[len_sep_pos+1:end_pos])

    decoded_data = base64.standard_b64decode(
        data[len_sep_pos-16:len_sep_pos]
    )
    
    return decoded_data


def main():
    hidden_data = b'Hello, PDF!'
    insert('/Users/skalniy/Documents/Insigne/vimbook-OPL.pdf', hidden_data)
    extracted = extract()
    print(hidden_data == extracted)


if __name__ == "__main__":
    main()