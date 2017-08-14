#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Sistemas Distribuídos 2017/1 - Código modificado por João Otávio Chervinski
import socket
import traceback
import struct
import os, sys, getopt
import threading
import base64
import os
import ssl
from random import choice, randint
from string import ascii_uppercase, ascii_letters, digits
from Crypto import Random
from Crypto.Cipher import AES

BLOCK_SIZE = 16

# Modo no qual o algoritmo vai operar - CBC = Cipher block chaining
# O modo CBC exige que seja feito um 'padding' na entrada, para que seja
# um múltiplo do tamanho do bloco
MODE = AES.MODE_CBC
LOCK_FILE = threading.Lock()

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


# Função que manipula as threads
def request_handler(IP, Port, Filename, key):
    # Cria um descritor de socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(sock, ca_certs="server.crt",
    cert_reqs=ssl.CERT_REQUIRED)

    try:
		global LOCK_FILE
		ssl_sock.connect((IP, int(Port)))
        # Envia para o servidor o tamanho do nome do arquivo a ser esperado
		#name_len = struct.pack('>L', len(Filename))
		#ssl_sock.sendall(encrypt(name_len,key))
		ssl_sock.sendall(bytes(encrypt(Filename, key)))

		# Mutex nas threads para evitar que abram o mesmo arquivo ao mesmo tempo
		LOCK_FILE.acquire()
		f = open(Filename,'rb')
		for line in f:
			ssl_sock.sendall(encrypt(line, key))

		print "[+]" + threading.current_thread().name + " -- Data has been sent"
		f.close()
		LOCK_FILE.release()

    except:
        traceback.print_exc()
    ssl_sock.close()

# Exibe a ajuda do parser
def help():
    print os.path.basename(sys.argv[0]) +  '-h -i <IP> -p <Port> -t <Threads> -f <Filename> -k <Encryption key>'

def main(argv):
    IP = ''
    Port = 0
    Threads = 0
    Filename = ''
    try:
        opts, args = getopt.getopt(argv,"hi:p:t:f:k:",["IP=", "Port=", "Threads=", "Filename=", "Key="])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    # Trata os argumentos da linha de comando
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-i", "--IP"):
            IP = arg
        elif opt in ("-p", "--Port"):
            Port = arg
        elif opt in ("-t", "--Threads"):
            Threads = arg
        elif opt in ("-f", "--Filename"):
            Filename = arg
        elif opt in ("-k", "--Key"):
            key = arg.zfill(32)
    if ((IP == '') or (Port == 0) or (Threads == 0) or (Filename == '')):
        help()
        quit()

    if len(key) > 32:
        print "[-] Key size must not be longer than 32 bytes"
        quit()
    ''' Cria uma lista 'threads'. Cada thread existente manipula uma instância da função
    request_handler e é adicionada na lista de threads'''
    threads = []
    for i in range(int(Threads)):
        thread = threading.Thread(target=request_handler, args = (IP, Port, Filename, key))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main(sys.argv[1:])
