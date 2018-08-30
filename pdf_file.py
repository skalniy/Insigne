""" Module for use with steganography electronic signatures PDF documents  """

from base64 import standard_b64decode, standard_b64encode
from collections import namedtuple
from io import BytesIO
from pickle import dump, load
from re import match

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

MetaSign = namedtuple('MetaSign', ['public_key', 'signature'])


class PDFFile:
    """ Represent PDF file in context of project logic """

    @staticmethod
    def __deserealize(data):
        if not data:
            return []

        decoded = standard_b64decode(data[2:])
        buf = BytesIO(decoded)
        return load(buf)

    def __serealize(self):
        buf = BytesIO()
        dump(self.chain, buf)
        return b''.join((b'% ', standard_b64encode(buf.getvalue()), b'\n'))

    def __init__(self, file_content):
        header = match(b'%PDF-1\.[1-7][\r\n]{1,2}', file_content)
        if not header:
            raise RuntimeError("invalid header")
        header_len = len(header.group(0))

        eof_pos = file_content.rfind(b'%%EOF', header_len)
        if eof_pos < 0:
            raise RuntimeError("EOF not found")

        startxref_pos = file_content.rfind(b'startxref', header_len, eof_pos)
        if startxref_pos < 0:
            raise RuntimeError("startxref not found")

        trailer_pos = file_content.rfind(b'trailer', header_len, startxref_pos)
        if not trailer_pos > header_len:
            trailer_pos = startxref_pos
        self.trailer = file_content[trailer_pos:]

        endsign_pos = file_content.rfind(b'% endsign\n', header_len, trailer_pos)
        if endsign_pos < 0:
            self.body = file_content[:trailer_pos]
            self.chain = self.__deserealize(file_content[trailer_pos:trailer_pos])
        else:
           chain_pos = file_content.rfind(b'% ', header_len, endsign_pos)
           self.body = file_content[:chain_pos]
           self.chain = self.__deserealize(file_content[chain_pos:endsign_pos])

    @classmethod
    def open(cls, path):
        """ Create PDFFile from PDF file """
        with open(path, 'rb') as f:
            return cls(f.read())

    def sha256(self):
        """ Return SHA-2 of original PDF """
        return SHA256.new(self.body + self.trailer)

    def sign(self, private_key_path):
        """ Add new sign to signatures chain """
        with open(private_key_path, 'rb') as f:
            key = RSA.importKey(f.read())

        self.chain.append(
            MetaSign(
                key.publickey().exportKey(format='DER'),
                PKCS1_v1_5.new(key).sign(self.sha256())
            )
        )

    def validate(self):
        """ Check if all signatures in signature chain are valid """
        for meta_signature in self.chain:
            key = RSA.importKey(meta_signature.public_key)
            if not PKCS1_v1_5.new(key).verify(self.sha256(), meta_signature.signature):
                return False
        return True

    def save(self, path):
        """ Save to file """
        path.write_bytes(b''.join(
            (self.body, self.__serealize(), b'% endsign\n', self.trailer)
        ))
