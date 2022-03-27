from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.signature import Signature
from ellipticcurve.publicKey import PublicKey
from ellipticcurve.privateKey import PrivateKey


class KeyMaster:
    
    @staticmethod
    def generate_keys() -> dict:
        prvk = PrivateKey() 
        return {'private_key': prvk, 
                'public_key': prvk.publicKey(),
                'public_key_string': prvk.publicKey().toString()} 
    
    @staticmethod
    def public_key_from_string(public_key_string: str) -> PublicKey:
        return PublicKey.fromString(public_key_string)
    
    @staticmethod
    def signature_from_string(signature_string: str) -> Signature:
        return Signature._fromString(signature_string)
    
    @staticmethod
    def sign(s: str, private_key: PrivateKey) -> Signature:
        return Ecdsa.sign(s, private_key)
    
    @staticmethod
    def is_verified(s: str, signature: Signature, 
                    public_key_string: str) -> bool:
        return Ecdsa.verify(s, signature, 
                            KeyMaster.public_key_from_string(public_key_string))
    
    @staticmethod
    def is_public_key_string_valid(public_key_string):
        try:
            PublicKey.fromString(public_key_string)
            return True
        except Exception:  # no exception subclass in ellipticcure lib
            return False
        