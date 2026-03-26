import base64
import hashlib
import json
from random import randint
from socket import socket, AF_INET, SOCK_STREAM
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class client:
	sock = socket(AF_INET, SOCK_STREAM)
	cipher = None
	def __init__(self):
		pass
	def connect(self, ip, port):
		self.sock.connect((ip, port))
		# Diffie‑Hellman 1
		G, P, a = randint(10000, 100000), randint(10000, 100000), randint(10000, 100000)
		A = G ** a % P
		self.send(f"{G}|{A}|{P}")
		B = int(self.recv())
		Step1Key = B ** a % P
		# Diffie‑Hellman 2
		G, P, a = randint(10000, 100000), randint(10000, 100000), randint(10000, 100000)
		A = G ** a % P
		self.send(f"{G}|{A}|{P}")
		B = int(self.recv())
		Step2Key = B ** a % P
		# Diffie‑Hellman 3
		G, P, a = randint(10000, 100000), randint(10000, 100000), randint(10000, 100000)
		A = G ** a % P
		self.send(f"{G}|{A}|{P}")
		B = int(self.recv())
		Step3Key = B ** a % P
		# Diffie‑Hellman Finalizing
		secret = Step1Key * Step2Key * Step3Key
		hashed = hashlib.sha512(str(secret).encode())
		hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=hashed.digest(), info=hashed.hexdigest().encode(), backend=default_backend())
		self.cipher = Fernet(base64.urlsafe_b64encode(hkdf.derive(secret.to_bytes((secret.bit_length() + 7) // 8, "big"))))
	def send(self, data):
		if isinstance(data, dict): data = json.dumps(data, ensure_ascii=False)
		data = str(data)
		if self.cipher: data = self.cipher.encrypt(data.encode())
		self.sock.sendall((data.encode() if not self.cipher else data) + b"\xDD\x98\xC7\xDC\x7C\x00")
	def recv(self):
		buf = bytearray()
		while True:
			chunk = self.sock.recv(1024)
			if not chunk:
				return None if not buf else bytes(buf)
			buf += chunk
			if b"\xDD\x98\xC7\xDC\x7C\x00" in buf:
				data, _, rest = buf.partition(b"\xDD\x98\xC7\xDC\x7C\x00")
				return data.decode() if not self.cipher else self.cipher.decrypt(bytes(data)).decode()
	def close(self):
		self.sock.close()

class serversclient:
	def __init__(self, socket, address):
		self.cipher = None
		self.sock = socket
		self.address = address
		# Diffie‑Hellman 1
		G, A, P = tuple([int(val) for val in self.recv().split("|")])
		b = randint(10000, 100000)
		B = G ** b % P
		self.send(B)
		Step1Key = A ** b % P
		# Diffie‑Hellman 2
		G, A, P = tuple([int(val) for val in self.recv().split("|")])
		b = randint(10000, 100000)
		B = G ** b % P
		self.send(B)
		Step2Key = A ** b % P
		# Diffie‑Hellman 3
		G, A, P = tuple([int(val) for val in self.recv().split("|")])
		b = randint(10000, 100000)
		B = G ** b % P
		self.send(B)
		Step3Key = A ** b % P
		# Diffie‑Hellman Finalizing
		secret = Step1Key * Step2Key * Step3Key
		hashed = hashlib.sha512(str(secret).encode())
		hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=hashed.digest(), info=hashed.hexdigest().encode(), backend=default_backend())
		self.cipher = Fernet(base64.urlsafe_b64encode(hkdf.derive(secret.to_bytes((secret.bit_length() + 7) // 8, "big"))))
	def send(self, data):
		if isinstance(data, dict): data = json.dumps(data, ensure_ascii=False)
		data = str(data)
		if self.cipher: data = self.cipher.encrypt(data.encode())
		self.sock.sendall((data.encode() if not self.cipher else data) + b"\xDD\x98\xC7\xDC\x7C\x00")
	def recv(self):
		buf = bytearray()
		while True:
			chunk = self.sock.recv(1024)
			if not chunk:
				return None if not buf else bytes(buf)
			buf += chunk
			if b"\xDD\x98\xC7\xDC\x7C\x00" in buf:
				data, _, rest = buf.partition(b"\xDD\x98\xC7\xDC\x7C\x00")
				return data.decode() if not self.cipher else self.cipher.decrypt(bytes(data)).decode()
	def close(self):
		self.sock.close()

class server:
	sock = socket(AF_INET, SOCK_STREAM)
	def __init__(self):
		pass
	def start(self, port, clienthandler, clientsnum=-1, block=True):
		self.sock.bind(("", port))
		self.sock.listen()
		self.clienthandler = clienthandler
		clients = 0
		if block:
			while clients != clientsnum:
				clients += 1
				clientsock, address = self.sock.accept()
				self.clienthandler(serversclient(clientsock, address))