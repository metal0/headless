import hashlib

from pont.utility.string import int_to_bytes


def __handle_arg(arg, hash, encoding='latin1'):
	if isinstance(arg, list):
		for x in arg:
			__handle_arg(x, hash)

	elif isinstance(arg, int):
		hash.update(int_to_bytes(arg))

	elif isinstance(arg, str):
		hash.update(arg.encode(encoding))
	else:
		hash.update(arg)

class UnsupportedResultType(Exception):
	pass

def sha1v(*args, **kwargs):
	sha = hashlib.sha1()
	for arg in args:
		__handle_arg(arg, sha)
	return sha

def sha1(*args, **kwargs):
	sha = sha1v(*args, **kwargs)
	if 'out' in kwargs:
		out = kwargs['out']
		if out == int:
			return int.from_bytes(sha.digest(), byteorder='little')
		elif out == bytes:
			return sha.digest()
		elif out == hex:
			return sha.hexdigest()
		else:
			raise UnsupportedResultType(f'{out=} is not supported by this function')
	return sha.digest()

__all__ = ['sha1']