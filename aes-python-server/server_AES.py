#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Sistemas Distribuídos 2017/1 - Código modificado por João Otávio Chervinski
import os
import sys
import getopt
import socket
import threading
import struct
import base64
import ssl
from Crypto import Random
from Crypto.Cipher import AES

BLOCK_SIZE = 16
MODE = AES.MODE_CBC

class threaded_server(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))

	def listen(self, key):
		self.sock.listen(5)
		while True:
			try:
				#print "Waiting for incoming connections..."
				client, address = self.sock.accept()
				client.settimeout(60)
				ssl_sock = ssl.wrap_socket(client,
				server_side=True, certfile="server.crt", keyfile="server.key")
				# Envia os descritores de conexão para as threads com a função ping_pong
				threading.Thread(target = self.ping_pong, args = (ssl_sock,address, key)).start()
			except (KeyboardInterrupt, SystemExit):
				print "[+] Shutdown requested...exiting"
				sys.exit(0)


	def ping_pong(self, ssl_sock, address, key):
		global MUTEX
		print '[+] Got secure connection from {}'.format(address)
		#len_name = decrypt(ssl_sock.recv(), key)
		fname = decrypt(ssl_sock.recv(), key)
		print '[+] File name = {}'.format(repr(fname))
		# Cada thread abre um arquivo cujo nome contém seu descritor (ex: *Thread-1.srv, *Thread-2.srv)
		# Mutex para evitar conflitos no acesso ao arquivo
		with open(fname.decode('UTF-8') + '_'  + threading.current_thread().name + '.srv', 'wb') as f:
			print '[+] File opened'
			print '[+] Receiving data...'
			while True:
				data = ssl_sock.recv(1024)
				if not data:
					print '[-] End of file '
					ssl_sock.shutdown(socket.SHUT_RDWR)
					ssl_sock.close()
					return
				print '[+] Encrypted data: {}'.format(data)
				data = decrypt(data, key)
				print '[+] Decrypted data: {} \n'.format(data.strip())
				f.write(data)


def encrypt(message, key):
    # Vetor de inicialização, fixo por motivos de praticidade, porém não é seguro
	IV = 16 * '\x04'
	global MODE
	# Aplica padding na mensagem, e a retorna criptografada usando Cipher block chaining
	return AES.new(key, MODE, IV).encrypt(pad_pkcs5(message))


def decrypt(message, key):
    # Vetor de inicialização, fixo por motivos de praticidade, porém não é seguro
	IV = 16 * '\x04'
	global MODE
	# Descriptografa a mensagem usando o mesmo vetor de inicialização usado na
	# função 'encrypt'
	decrypted = AES.new(key, MODE, IV).decrypt(message)
	# Remove os caracteres de padding adicionados à mensagem na função 'encrypt', e então
	# retorna a mensagem original
	return unpad_pkcs5(decrypted)


def pad_pkcs5(message):
	global BLOCK_SIZE
	# Aplica padding na mensagem de acordo com as especificações do PKCS5
	# Link: https://tools.ietf.org/html/rfc2898
	return message + (BLOCK_SIZE - len(message) % BLOCK_SIZE) *  \
	chr(BLOCK_SIZE - len(message) % BLOCK_SIZE)


def unpad_pkcs5(message):
	# Remove o padding da mensagem original
	return message[0:-ord(message[-1])]


def help():
    print(os.path.basename(sys.argv[0]), '-h -p <Port> -k <Encryption Key>')

def main(argv):
	port = 0
	try:
		opts, args = getopt.getopt(argv,"hp:k:",["Port=", "Key="])
	except getopt.GetoptError:
		help()
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			help()
			sys.exit()
		elif opt in ("-p", "--Port"):
			port = arg
		elif opt in ("-k", "--Key"):
			'''A função zfill é utilizada para preencher a
			chave até um tamanho que seja aceito pelo algoritmo, nesse
			caso, 32 bytes'''
			key = arg.zfill(32)

	if (port == 0):
		help()
		quit()

	# Se a chave for grande demais, exibe ajuda e termina a execução
	if len(key) > 32:
		print "[-] Key size must not be longer than 32 bytes"
		quit()


	threaded_server('', int(port)).listen(key)

if __name__ == "__main__":
    main(sys.argv[1:])
