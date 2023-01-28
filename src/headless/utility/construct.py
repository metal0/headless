import construct


class EncryptedConstruct(construct.Adapter):
    def __init__(self, subcon=construct.GreedyBytes, encrypt=None, decrypt=None):
        super().__init__(subcon)
        self.decrypt = decrypt
        self.encrypt = encrypt

    def _decode(self, obj, context, path):
        return self.decrypt(obj)

    def _encode(self, obj, context, path):
        return self.encrypt(obj)
