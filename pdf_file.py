""" Module for use with steganography electronic signatures PDF documents  """

from base64 import standard_b64decode, standard_b64encode
from collections import namedtuple
from io import BytesIO
from pickle import dump, load

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


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
        # TODO check header

        # TODO change bound to header size
        eof_pos = file_content.rfind(b'%%EOF')

        if eof_pos < 0:
            raise RuntimeError("EOF not found")

        # TODO change bound to header size
        startxref_pos = file_content.rfind(b'startxref', 0, eof_pos)
        if startxref_pos < 0:
            raise RuntimeError("startxref not found")

        # TODO change bound to header size
        trailer_pos = file_content.rfind(b'trailer', 0, startxref_pos)
        trailer_pos = (trailer_pos if trailer_pos > 0 else startxref_pos)

        chain_pos = file_content.rfind(b'\n', 0, trailer_pos-1) + 1
        if not file_content.startswith(b'% ', chain_pos, trailer_pos):
            chain_pos = trailer_pos

        self.body = file_content[:chain_pos]
        self.chain = self.__deserealize(file_content[chain_pos:trailer_pos])
        self.trailer = file_content[trailer_pos:]

    @classmethod
    def open(cls, path):
        """ Create PDFFile from PDF file """
        with open(path, 'rb') as f:
            return cls(f.read())

    def sha256(self):
        """ Return SHA-2 binary digest of original PDF """
        return SHA256.new(self.body + self.trailer).digest()

    def sign(self, private_key_path, public_key_path):
        """ Add new sign to signatures chain """
        with open(private_key_path, 'rb') as f:
            private_key = RSA.importKey(f.read())

        with open(public_key_path, 'rb') as f:
            public_key = RSA.importKey(f.read())

        # TODO Crypto.Signature.PKCS1_PSS or Crypto.Signature.PKCS1_v1_5
        self.chain.append(
            MetaSign(
                public_key.exportKey(format='DER'),
                private_key.sign(self.sha256(), '')
            )
        )

    def validate(self):
        """ Check if all signatures in signature chain are valid """
        for meta_signature in self.chain:
            public_key = RSA.importKey(meta_signature.public_key)
            if not public_key.verify(self.sha256(), meta_signature.signature):
                return False
        return True

    def save(self, path):
        """ Save to file """
        with open(path, 'wb') as f:
            f.write(b''.join((self.body, self.__serealize(), self.trailer)))